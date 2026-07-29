import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from typing import TypedDict, List, Optional, Any
from config import *
import vectorstore as vs
import json

logger = logging.getLogger(__name__)

# ── LLM ──────────────────────────────────────────────────
GROQ_MODEL = "openai/gpt-oss-120b"
llm = ChatGroq(model=GROQ_MODEL)
logger.info("LLM initialized with model=%s", GROQ_MODEL)

try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search_tool = DuckDuckGoSearchRun()
    WEB_SEARCH_ENABLED = True
except Exception as e:
    DuckDuckGoSearchRun = None
    search_tool = None
    WEB_SEARCH_ENABLED = False
    logger.warning(
        "DuckDuckGoSearchRun disabled because ddgs is missing. "
        "Install `pip install -U ddgs` to enable web search. Error: %s",
        e
    )

# ── State ─────────────────────────────────────────────────
class LexAIState(TypedDict):
    question: str
    mode: str                    # qa, risk, summary, compare, extract
    documents: List[str]         # retrieved chunk texts
    metadatas: List[dict]        # source info per chunk
    distances: List[float]       # relevance scores
    web_results: str             # web search results if used
    generation: str              # final answer
    sources: List[str]           # source files cited
    search_strategy: str         # "vectorstore", "web", "both"
    confidence: str              # "high", "medium", "low"
    retry_count: int
    chat_history: List[dict]     # NEW — prior Q&A turns for this session


def extract_plain_text_from_response(response: Any) -> str:
    """Normalize ChatGroq response content into a plain string."""
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if "text" in item:
                    texts.append(str(item["text"]))
                elif "type" in item and item["type"] == "text" and "text" in item:
                    texts.append(str(item["text"]))
            elif isinstance(item, str):
                texts.append(item)
        return "\n".join(texts).strip()
    return str(content) if content is not None else ""

# ── Node 1: Retrieve ─────────────────────────────────────
def retrieve_node(state: LexAIState) -> dict:
    """
    Choose retrieval strategy based on mode.
    Summary/compare → MMR (diverse chunks)
    QA/risk/extract → similarity (most relevant chunks)
    """
    mode = state.get("mode", "qa")
    question = state["question"]

    if mode in ["summary", "compare"]:
        # MMR for broad coverage — get diverse chunks across the document
        results = vs.mmr_search(question, k=TOP_K_CHUNKS)
        documents = [r.page_content for r in results]
        metadatas = [r.metadata for r in results]
        distances = [0.3] * len(results)  # MMR doesn't return scores
    else:
        # similarity search for specific questions
        results = vs.similarity_search(question, k=TOP_K_CHUNKS)
        documents = [r[0].page_content for r in results]
        metadatas = [r[0].metadata for r in results]
        distances = [r[1] for r in results]

    return {
        "documents": documents,
        "metadatas": metadatas,
        "distances": distances
    }

# ── Node 2: Grade ─────────────────────────────────────────
def grade_node(state: LexAIState) -> dict:
    """
    Check if retrieved chunks are actually relevant.
    If best distance > threshold → mark for web search fallback.
    """
    distances = state.get("distances", [1.0])
    best = min(distances) if distances else 1.0

    if best < 0.35:
        confidence = "high"
    elif best < 0.55:
        confidence = "medium"
    elif best < RELEVANCE_THRESHOLD:
        confidence = "low"
    else:
        confidence = "insufficient"

    return {
        "confidence": confidence,
        "retry_count": state.get("retry_count", 0) + 1
    }

# ── Node 3: Web Search fallback ───────────────────────────
def web_search_node(state: LexAIState) -> dict:
    """
    Fall back to DuckDuckGo when vectorstore doesn't have the answer.
    Searches for relevant case law, legal definitions, precedents.
    WHY: Legal questions often need current case law not in uploaded docs.
    """
    if not WEB_SEARCH_ENABLED or search_tool is None:
        logger.warning("Web search is disabled because DuckDuckGoSearchRun is not available.")
        return {
            "web_results": "",
            "search_strategy": "vectorstore"
        }

    legal_query = f"legal {state['question']} law regulation"
    results = search_tool.run(legal_query)
    return {
        "web_results": results,
        "search_strategy": "web"
    }

# ── Node 4: Generate ──────────────────────────────────────
def generate_node(state: LexAIState) -> dict:
    """
    Generate the final answer based on mode.
    Different prompts for different analysis modes.
    """
    mode = state.get("mode", "qa")
    question = state["question"]
    doc_context = "\n\n---\n\n".join(state.get("documents", []))
    web_context = state.get("web_results", "")

    history = state.get("chat_history", [])
    history_text = ""
    if history:
        recent = history[-3:]
        history_text = "=== CONVERSATION SO FAR ===\n" + "\n".join(
            f"Q: {h['question']}\nA: {h['answer']}" for h in recent
        ) + "\n\n"

    # build context from both sources
    full_context = history_text
    if doc_context:
        full_context += f"=== FROM UPLOADED DOCUMENTS ===\n{doc_context}\n\n"
    if web_context:
        full_context += f"=== FROM WEB SEARCH ===\n{web_context}"
    # mode-specific prompts
    mode_prompts = {
        "qa": f"""You are a legal AI assistant. Answer using ONLY the provided context.
Cite the source document and page for every claim.
If the answer is not in the context, say so clearly.

Context: {full_context}
Question: {question}
Answer (with citations):""",

        "risk": f"""You are a senior legal risk analyst.
Analyze the provided contract text for risk clauses.
Structure your response as:
RISK LEVEL: [LOW/MEDIUM/HIGH/CRITICAL]
KEY RISKS:
- [risk 1]
- [risk 2]
MISSING PROTECTIONS:
- [what's not there but should be]
RECOMMENDATIONS:
- [specific actions]

Context: {full_context}
Focus question: {question}""",

        "summary": f"""You are a legal document summarizer.
Provide a comprehensive executive summary of the document.
Include: parties, key obligations, important dates, financial terms, termination conditions.

Context: {full_context}
Produce a structured legal summary:""",

        "compare": f"""You are a legal document comparison specialist.
Compare the documents in the context.
Highlight: key differences, conflicting clauses, version changes, missing provisions.

Context: {full_context}
Comparison request: {question}""",

        "extract": f"""You are a legal clause extraction specialist.
Extract the specific clauses or information requested.
Quote the exact text, then explain its legal significance.

Context: {full_context}
Extract: {question}"""
    }

    prompt = mode_prompts.get(mode, mode_prompts["qa"])
    response = llm.invoke(prompt)
    generation = extract_plain_text_from_response(response)

    # extract source files cited
    sources = list(set([
        m.get("source_file", "unknown")
        for m in state.get("metadatas", [])
    ]))

    strategy = "both" if (doc_context and web_context) \
               else ("web" if web_context else "vectorstore")

    return {
        "generation": generation,
        "sources": sources,
        "search_strategy": strategy,
        "chat_history": history + [{"question": question, "answer": generation}]
    }

# ── Routing function ──────────────────────────────────────
def route_after_grade(state: LexAIState) -> str:
    """Decide: generate directly or do web search first"""
    confidence = state.get("confidence", "low")
    retry = state.get("retry_count", 0)

    # if relevance is insufficient AND we haven't retried yet → web search
    if confidence == "insufficient" and retry <= MAX_RETRIES and WEB_SEARCH_ENABLED:
        return "web_search"

    # otherwise generate from what we have
    return "generate"

# ── Build graph ───────────────────────────────────────────
graph = StateGraph(LexAIState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("grade", grade_node)
graph.add_node("web_search", web_search_node)
graph.add_node("generate", generate_node)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "grade")
graph.add_conditional_edges("grade", route_after_grade, {
    "web_search": "web_search",
    "generate": "generate"
})
graph.add_edge("web_search", "generate")
graph.add_edge("generate", END)

memory = MemorySaver()
agent_app = graph.compile(checkpointer=memory)

# ── Public interface ─────────────────────────────────────
def run_analysis(question: str, mode: str = "qa", session_id: str = "default") -> dict:
    """
    Main entry point for the agent.
    Called by FastAPI endpoints.
    """
    config = {"configurable": {"thread_id": session_id}}

    try:
        existing = agent_app.get_state(config)
        prior_history = existing.values.get("chat_history", []) if existing.values else []
    except Exception:
        prior_history = []

    initial_state = {
        "question": question,
        "mode": mode,
        "documents": [],
        "metadatas": [],
        "distances": [],
        "web_results": "",
        "generation": "",
        "sources": [],
        "search_strategy": "vectorstore",
        "confidence": "high",
        "retry_count": 0,
        "chat_history": prior_history
    }
    result = agent_app.invoke(initial_state, config=config)
    return {
        "answer": result["generation"],
        "sources": result["sources"],
        "confidence": result["confidence"],
        "search_used": result["search_strategy"],
        "mode": mode,
        "session_id": session_id
    }
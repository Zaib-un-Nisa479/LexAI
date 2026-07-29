import logging
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import *
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# ── Embeddings ──────────────
# ────────────────────────────
embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    output_dimensionality=768,
    google_api_key=GEMINI_API_KEY,
    task_type="retrieval_document"
)
logger.info(
    "Embeddings initialized with model=%s, task_type=%s, vertexai=%s",
    embeddings.model,
    embeddings.task_type,
    getattr(embeddings, '_use_vertexai', None),
)

query_embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=GEMINI_API_KEY,
    task_type="retrieval_query"  # different task type for queries vs documents
)
logger.info(
    "Query embeddings initialized with model=%s, task_type=%s, vertexai=%s",
    query_embeddings.model,
    query_embeddings.task_type,
    getattr(query_embeddings, '_use_vertexai', None),
)

# ── Text splitter ────────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " ", ""]
    # priority: paragraph breaks → line breaks → sentences → words
    # keeps legal clauses together as much as possible
)

def get_vectorstore() -> Chroma:
    """Load or create persistent vectorstore"""
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="lexai_documents"
    )

def ingest_pdf(filepath: str, doc_type: str = "legal") -> dict:
    """
    Ingest a PDF into the vectorstore.
    Stores rich metadata: filename, page, doc_type, upload_date.
    Returns stats about what was ingested.
    """
    filename = os.path.basename(filepath)
    loader = PyPDFLoader(filepath)
    pages = loader.load()

    chunks = splitter.split_documents(pages)

    # enrich metadata on every chunk
    for chunk in chunks:
        chunk.metadata.update({
            "source_file": filename,
            "doc_type": doc_type,
            "upload_date": datetime.now().isoformat(),
            "page_display": chunk.metadata.get("page", 0) + 1
        })

    vs = get_vectorstore()
    vs.add_documents(chunks)

    total = vs._collection.count()
    return {
        "filename": filename,
        "pages": len(pages),
        "chunks_created": len(chunks),
        "total_chunks_in_db": total
    }

def ingest_text(text: str, source_name: str, doc_type: str = "extracted") -> dict:
    """
    Ingest plain text (e.g., extracted from an image via vision).
    Used when user uploads a photo of a handwritten document.
    """
    doc = Document(
        page_content=text,
        metadata={
            "source_file": source_name,
            "doc_type": doc_type,
            "upload_date": datetime.now().isoformat(),
            "page_display": 1
        }
    )
    chunks = splitter.split_documents([doc])
    vs = get_vectorstore()
    vs.add_documents(chunks)
    return {"chunks_created": len(chunks)}

def similarity_search(query: str, k: int = TOP_K_CHUNKS) -> list:
    """Standard similarity search — best for QA and specific questions"""
    vs = get_vectorstore()
    results = vs.similarity_search_with_score(query, k=k)
    return results  # list of (Document, float) tuples

def mmr_search(query: str, k: int = TOP_K_CHUNKS) -> list:
    """
    MMR = Maximum Marginal Relevance.
    Returns diverse chunks instead of 4 similar ones.
    Best for summaries, comparisons, and broad analysis.
    Avoids repeating the same clause section 4 times.
    """
    vs = get_vectorstore()
    return vs.max_marginal_relevance_search(query, k=k, fetch_k=k*3)

def get_all_documents() -> list:
    """List all unique source files in the vectorstore"""
    vs = get_vectorstore()
    results = vs.get()
    sources = list(set([
        m.get("source_file", "unknown")
        for m in results.get("metadatas", [])
    ]))
    return sources

def get_chunk_count() -> int:
    """Total chunks stored"""
    return get_vectorstore()._collection.count()

def clear_all():
    """Wipe entire vectorstore — use carefully"""
    store = get_vectorstore()
    existing = store.get()
    ids = existing.get("ids", [])
    if ids:
        store._collection.delete(ids=ids)
    print(f"Vectorstore cleared. Removed {len(ids)} chunks.")
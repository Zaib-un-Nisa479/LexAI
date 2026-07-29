# LexAI — Multimodal Legal Document Intelligence Platform

A full-stack RAG (Retrieval-Augmented Generation) application that lets you upload legal documents — PDFs, scanned images, or spoken questions — and get grounded, source-cited answers, risk analysis, summaries, and clause extraction, powered by a self-correcting LangGraph agent.

Built as an end-to-end capstone project: FastAPI + LangGraph backend, Next.js + TypeScript frontend, multimodal input (text, image, voice), and a genuinely agentic retrieval pipeline that knows when it doesn't know something.

---

## Why this project is different from a typical RAG demo

Most RAG tutorials retrieve chunks, stuff them in a prompt, and generate — with no way to tell whether the retrieved context actually answers the question. LexAI's agent graph adds a real **grading and fallback loop**:

```
question → retrieve → grade confidence → [insufficient?] → web search → generate
                                       ↘ [sufficient] ───────────────→ generate
```

- **Retrieve** pulls the most relevant chunks from ChromaDB (similarity search for Q&A/risk/extract modes, MMR for diverse coverage in summary/compare modes).
- **Grade** scores retrieval quality using vector distance — no extra LLM call, so this step is instant.
- **Fallback** — if the uploaded documents don't cover the question, the agent automatically searches the web instead of guessing, and tells you which source it used.
- **Generate** produces a mode-specific answer (Q&A, risk analysis, summary, comparison, or clause extraction) with every claim traceable to a source document or the web.
- **Memory** — the agent remembers prior turns in a session, so natural follow-up questions ("explain the second point in more detail") resolve correctly instead of failing as out-of-context.

The frontend surfaces all of this — confidence level, which source was used, and full conversation history — rather than hiding it behind a plain chat bubble.

---

## Features

- 📄 **PDF ingestion** — chunked, embedded, and indexed with per-chunk metadata (source file, page, upload date)
- 🖼️ **Vision/OCR analysis** — extract and analyze text from photos of physical documents, with automatic classification (contract, court order, invoice, etc.)
- 🎙️ **Voice input** — record a question in-browser, transcribed via Whisper, answered by the same agent as text queries
- ⚖️ **Five analysis modes** — Q&A, risk detection, executive summary, document comparison, clause extraction
- 🔍 **Self-correcting retrieval** — automatic web search fallback when uploaded documents don't have the answer
- 🧠 **Conversation memory** — follow-up questions reference prior answers correctly, per session
- 📊 **Transparent confidence + sourcing** — every answer shows confidence level and whether it came from your documents, the web, or both
- 🕘 **Conversation history panel** — review the full Q&A trail for the current session

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI |
| Agent orchestration | LangGraph (StateGraph with conditional routing + checkpointed memory) |
| LLM (generation) | Groq — `openai/gpt-oss-120b` |
| Embeddings + Vision OCR | Google Gemini (`gemini-embedding-2-preview`, Gemini Vision) |
| Vector store | ChromaDB (persistent, local) |
| Speech-to-text | OpenAI Whisper (local inference) |
| Text-to-speech | gTTS |
| Web search fallback | DuckDuckGo Search |
| Frontend framework | Next.js 16 (App Router) + TypeScript |
| Styling | Tailwind CSS + shadcn/ui |
| Frontend state | Zustand |
| File upload | react-dropzone |

---

## Architecture

```
lexai/
├── backend/
│   ├── main.py            FastAPI app — 7 REST endpoints
│   ├── agent.py           LangGraph state machine (retrieve → grade → [web search] → generate)
│   ├── vectorstore.py     ChromaDB ingestion, similarity/MMR search, embeddings
│   ├── vision.py          Gemini Vision — OCR, document classification, risk detection from images
│   ├── voice.py           Whisper transcription + gTTS speech synthesis
│   ├── schemas.py         Pydantic request/response models
│   ├── config.py          Environment config, model names, RAG parameters
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── app/page.tsx                    3-panel workspace layout
    │   ├── components/
    │   │   ├── workspace/                  DocumentPanel · ChatPanel · InspectorPanel
    │   │   ├── chat/                       ModeSelector · MessageBubble · ConfidenceBadge · HistoryPanel
    │   │   ├── upload/                     DropZone (PDF + image, drag-and-drop)
    │   │   └── voice/                      In-browser recorder + waveform
    │   ├── lib/
    │   │   ├── api.ts                      Typed API client for all backend endpoints
    │   │   └── types.ts                    Shared types mirroring backend Pydantic schemas
    │   └── store/useAppStore.ts            Zustand — messages, session, mode, documents
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check — chunk count, indexed documents |
| `POST` | `/ingest/pdf` | Upload and index a PDF |
| `POST` | `/analyze/text` | Ask a question in a given mode (`qa`, `risk`, `summary`, `compare`, `extract`) |
| `POST` | `/analyze/voice` | Upload/record audio — transcribed and analyzed, with spoken response |
| `POST` | `/analyze/vision` | Upload an image — OCR + analysis, optionally indexed into the knowledge base |
| `POST` | `/analyze/risk-image` | Upload a contract photo — instant structured risk assessment |
| `GET` | `/documents` | List all indexed documents |
| `DELETE` | `/documents/all` | Clear the vector store |

Interactive API docs available at `/docs` (Swagger UI) once the backend is running.

---

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 22 LTS
- A [Google AI Studio](https://aistudio.google.com/apikey) API key (embeddings + vision)
- A [Groq](https://console.groq.com) API key (generation)

### Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
# source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
```

Run the server:
```bash
python -m uvicorn main:app --reload --port 8000
```

Backend available at `http://127.0.0.1:8000` — Swagger docs at `http://127.0.0.1:8000/docs`.

### Frontend setup

```bash
cd frontend
npm install
```

Create a `.env.local` file in `frontend/`:
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Run the dev server:
```bash
npm run dev
```

Open `http://localhost:3000`.

---

## Usage

1. Drag a PDF or a photo of a document into the upload zone.
2. Pick an analysis mode — Q&A, Risk, Summary, Compare, or Extract.
3. Ask a question by typing or recording your voice.
4. Review the answer alongside its confidence level and cited sources in the inspector panel.
5. Ask a follow-up — the agent remembers the conversation within the session.
6. Open the history panel to review the full session trail.

---

## Honest scope and limitations

This project is a strong **document intelligence and triage assistant**, not a substitute for legal advice, and that distinction is intentional:

- No citation verification against authoritative legal databases (uses open web search, not Westlaw/Lexis)
- No jurisdiction-awareness in prompts
- Single shared vector collection — not yet multi-tenant/access-controlled
- Local file storage is unencrypted — not production-ready for confidential client data as-is

These are documented deliberately rather than glossed over, because knowing the boundary between "fast contract triage tool" and "legal advice engine" is itself part of responsible AI system design.

---

## License

MIT — feel free to fork and build on this.

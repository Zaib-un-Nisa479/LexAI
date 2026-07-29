from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from config import UPLOAD_DIR
from schemas import *
import vectorstore as vs
import vision, voice, agent
import os, shutil, uuid

app = FastAPI(
    title="LexAI — Legal Document Intelligence API",
    description="Multimodal RAG agent for legal document analysis",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], allow_credentials=True)

# ── Health ────────────────────────────────────────────────
@app.get("/", summary="Health check")
def root():
    return {
        "status": "running",
        "system": "LexAI Legal Intelligence",
        "docs": "/docs",
        "chunks_in_db": vs.get_chunk_count(),
        "documents": vs.get_all_documents()
    }

# ── Document Ingestion ────────────────────────────────────
@app.post("/ingest/pdf", response_model=IngestResponse,
    summary="Upload and index a PDF document")
async def ingest_pdf(
    file: UploadFile = File(...),
    doc_type: str = Form(default="legal")
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files accepted")

    # save uploaded file
    save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = vs.ingest_pdf(save_path, doc_type=doc_type)
        return IngestResponse(
            filename=file.filename,
            chunks_created=result["chunks_created"],
            total_chunks_in_db=result["total_chunks_in_db"],
            message=f"Successfully indexed {result['pages']} pages into {result['chunks_created']} chunks"
        )
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")

# ── Text Analysis ─────────────────────────────────────────
@app.post("/analyze/text", response_model=AnalysisResponse,
    summary="Analyze documents via text question")
async def analyze_text(request: TextRequest):
    try:
        result = agent.run_analysis(
            question=request.question,
            mode=request.mode,
            session_id=request.session_id
        )
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

# ── Voice Analysis ────────────────────────────────────────
@app.post("/analyze/voice", response_model=VoiceResponse,
    summary="Upload voice recording — transcribe and analyze")
async def analyze_voice(
    request: Request,
    audio: UploadFile = File(...),
    mode: str = Form(default="qa"),
    session_id: str = Form(default="default")
):
    # read audio bytes
    audio_bytes = await audio.read()
    suffix = os.path.splitext(audio.filename)[1] if audio.filename else ".wav"

    # transcribe
    transcription_result = voice.transcribe_audio_bytes(audio_bytes, suffix=suffix)
    question = transcription_result["text"]

    if not question:
        raise HTTPException(400, "No speech detected in audio")

    # run through agent
    result = agent.run_analysis(question, mode=mode, session_id=session_id)

    audio_filename = f"{uuid.uuid4()}.mp3"
    audio_path = os.path.join(UPLOAD_DIR, audio_filename)
    voice.text_to_speech(result["answer"], output_path=audio_path)
    audio_url = request.url_for("get_audio", filename=audio_filename)

    return VoiceResponse(
        transcription=question,
        answer=result["answer"],
        sources=result["sources"],
        mode_used=mode,
        audio_url=audio_url
    )

# ── Generated audio playback ─────────────────────────────
@app.get("/audio/{filename}", response_class=FileResponse, summary="Serve generated voice response audio")
def get_audio(filename: str):
    audio_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(audio_path):
        raise HTTPException(404, "Audio file not found")
    return FileResponse(audio_path, media_type="audio/mpeg")

# ── Vision Analysis ───────────────────────────────────────
@app.post("/analyze/vision", response_model=VisionResponse,
    summary="Upload image of document — extract and analyze")
async def analyze_vision(
    image: UploadFile = File(...),
    question: str = Form(default="Extract and analyze all text from this document"),
    ingest_after: bool = Form(default=True)
):
    # save image
    save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{image.filename}")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    # extract text and analyze
    extraction = vision.extract_text_from_image(save_path)
    analysis = vision.analyze_document_image(save_path, question)

    # optionally ingest the extracted text into vectorstore
    if ingest_after and extraction.get("extracted_text"):
        vs.ingest_text(
            text=extraction["extracted_text"],
            source_name=f"image:{image.filename}",
            doc_type=extraction.get("document_type", "image_extracted")
        )

    return VisionResponse(
        extracted_text=extraction.get("extracted_text", ""),
        analysis=analysis,
        document_type=extraction.get("document_type", "unknown")
    )

# ── Risk Analysis from image ──────────────────────────────
@app.post("/analyze/risk-image",
    summary="Upload contract image — instant risk analysis")
async def risk_from_image(image: UploadFile = File(...)):
    save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{image.filename}")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(image.file, f)
    return vision.detect_risk_from_image(save_path)

# ── Document list ─────────────────────────────────────────
@app.get("/documents", summary="List all indexed documents")
def list_documents():
    return {
        "documents": vs.get_all_documents(),
        "total_chunks": vs.get_chunk_count()
    }

# ── Clear vectorstore ─────────────────────────────────────
# ── Clear vectorstore ─────────────────────────────────────
@app.delete("/documents/all", summary="Clear all indexed documents")
def clear_documents():
    try:
        vs.clear_all()
        return {"message": "All documents cleared"}
    except Exception as e:
        raise HTTPException(500, f"Clear failed: {str(e)}")
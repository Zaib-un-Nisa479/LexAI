from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class AnalysisMode(str, Enum):
    qa = "qa"                       # general question answering
    risk = "risk"                   # extract risk clauses
    summary = "summary"             # summarize document
    compare = "compare"             # compare two documents
    extract = "extract"             # extract specific clauses

class TextRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    mode: AnalysisMode = AnalysisMode.qa
    session_id: str = Field(default="default")

class VoiceResponse(BaseModel):
    transcription: str
    answer: str
    sources: List[str]
    mode_used: str
    audio_url: Optional[str] = None
    audio_url: Optional[str] = None

class VisionResponse(BaseModel):
    extracted_text: str
    analysis: str
    document_type: str

class IngestResponse(BaseModel):
    filename: str
    chunks_created: int
    total_chunks_in_db: int
    message: str

class AnalysisResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: str              # "high", "medium", "low"
    search_used: str             # "vectorstore", "web", "both", "none"
    mode: str
    session_id: str

class RiskAnalysis(BaseModel):
    risk_level: str              # "low", "medium", "high", "critical"
    risks_found: List[str]
    recommendations: List[str]
    clauses_reviewed: int
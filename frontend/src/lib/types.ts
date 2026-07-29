export type AnalysisMode = "qa" | "risk" | "summary" | "compare" | "extract";

export interface AnalysisResponse {
  answer: string;
  sources: string[];
  confidence: "high" | "medium" | "low" | "insufficient";
  search_used: "vectorstore" | "web" | "both" | "none";
  mode: string;
  session_id: string;
}

export interface IngestResponse {
  filename: string;
  chunks_created: number;
  total_chunks_in_db: number;
  message: string;
}

export interface VisionResponse {
  extracted_text: string;
  analysis: string;
  document_type: string;
}

export interface VoiceResponse {
  transcription: string;
  answer: string;
  sources: string[];
  mode_used: string;
  audio_url?: string;
}
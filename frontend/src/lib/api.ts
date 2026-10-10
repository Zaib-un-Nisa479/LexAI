const BASE = process.env.NEXT_PUBLIC_API_URL ?? "https://lexai-0vic.onrender.com";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    let message = text;
    try {
      const json = JSON.parse(text);
      message = json.detail ?? json.error ?? JSON.stringify(json);
    } catch {
      // response is not JSON, keep raw text
    }
    throw new Error(`API error ${res.status}: ${message}`);
  }
  return res.json();
}

export const api = {
  health: () => fetch(`${BASE}/`).then((res) => handle(res)),

  ingestPdf: (file: File, docType = "legal") => {
    const form = new FormData();
    form.append("file", file);
    form.append("doc_type", docType);
    return fetch(`${BASE}/ingest/pdf`, { method: "POST", body: form }).then((res) => handle(res));
  },

  analyzeText: (question: string, mode: string, sessionId: string) =>
    fetch(`${BASE}/analyze/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, mode, session_id: sessionId }),
    }).then((res) => handle(res)),

  analyzeVision: (image: File, question: string, ingestAfter = true) => {
    const form = new FormData();
    form.append("image", image);
    form.append("question", question);
    form.append("ingest_after", String(ingestAfter));
    return fetch(`${BASE}/analyze/vision`, { method: "POST", body: form }).then((res) => handle(res));
  },

  analyzeVoice: (audioBlob: Blob, mode: string, sessionId: string, signal?: AbortSignal) => {
    const form = new FormData();
    form.append("audio", audioBlob, "recording.wav");
    form.append("mode", mode);
    form.append("session_id", sessionId);
    return fetch(`${BASE}/analyze/voice`, { method: "POST", body: form, signal }).then((res) => handle(res));
  },

  listDocuments: () => fetch(`${BASE}/documents`).then((res) => handle(res)),
  clearDocuments: () => fetch(`${BASE}/documents/all`, { method: "DELETE" }).then((res) => handle(res)),
};

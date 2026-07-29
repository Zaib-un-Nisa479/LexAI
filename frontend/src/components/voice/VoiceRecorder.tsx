"use client";
import { useRef, useState } from "react";
import { useAudioRecorder } from "./useAudioRecorder";
import { api } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";
import { Mic, Square, Send, X } from "lucide-react";

export function VoiceRecorder() {
  const [responseAudioUrl, setResponseAudioUrl] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const { isRecording, audioBlob, start, stop, reset } = useAudioRecorder();
  const { mode, sessionId, addMessage, isThinking, setThinking } = useAppStore();

  const handleSend = async () => {
    if (!audioBlob || isSending) return;
    setThinking(true);
    setIsSending(true);
    setIsCancelling(false);
    abortControllerRef.current = new AbortController();

    try {
      const res: any = await api.analyzeVoice(audioBlob, mode, sessionId, abortControllerRef.current.signal);
      addMessage({ id: crypto.randomUUID(), role: "user", content: res.transcription });
      addMessage({ id: crypto.randomUUID(), role: "assistant", content: res.answer, sources: res.sources });
      setResponseAudioUrl(res.audio_url ?? null);
    } catch (error: any) {
      if (error.name === "AbortError") {
        addMessage({ id: crypto.randomUUID(), role: "assistant", content: "Response stopped by user." });
      } else {
        console.error("Voice request failed", error);
      }
    } finally {
      setThinking(false);
      setIsSending(false);
      reset();
      abortControllerRef.current = null;
      setIsCancelling(false);
    }
  };

  const handleCancel = () => {
    if (!abortControllerRef.current) return;
    setIsCancelling(true);
    abortControllerRef.current.abort();
  };

  const handleStart = () => {
    setResponseAudioUrl(null);
    start();
  };

  return (
    <div className="rounded-3xl border border-white/10 bg-slate-950/90 p-4 shadow-sm shadow-slate-950/20">
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between text-sm font-semibold text-slate-200">
          <span>Voice recorder</span>
          <span className="rounded-full bg-slate-800 px-2 py-1 text-xs text-slate-400">Audio input</span>
        </div>

        <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
          <button
            onClick={handleStart}
            disabled={isRecording || isSending}
            className="flex items-center justify-center gap-2 rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Mic size={16} />
            {isRecording ? "Recording…" : "Start recording"}
          </button>

          {isRecording && (
            <button
              onClick={stop}
              className="flex items-center justify-center gap-2 rounded-2xl border border-red-500 bg-slate-950 px-4 py-3 text-sm font-semibold text-red-400 transition hover:bg-red-500/10"
            >
              <Square size={16} /> Stop recording
            </button>
          )}
        </div>

        <div className="flex flex-col gap-3">
          {audioBlob && !isRecording ? (
            <div className="flex flex-col gap-2 rounded-2xl border border-slate-800 bg-slate-900 p-3">
              <div className="flex items-center justify-between text-sm text-slate-300">
                <span>Recorded audio ready</span>
                <button
                  onClick={handleSend}
                  disabled={isSending}
                  className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <Send size={16} />
                  {isSending ? "Sending…" : "Send voice"}
                </button>
              </div>
              <audio controls src={URL.createObjectURL(audioBlob)} className="w-full rounded-xl bg-slate-950" />
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/80 px-4 py-3 text-sm text-slate-400">
              {isRecording
                ? "Recording audio. Click stop when finished."
                : "Click Start recording to capture your question via microphone."}
            </div>
          )}
        </div>

        {isSending && abortControllerRef.current && (
          <div className="flex items-center justify-between gap-3 rounded-2xl border border-orange-500/30 bg-orange-500/10 px-3 py-3 text-sm text-orange-100">
            <span>Generating response…</span>
            <button
              onClick={handleCancel}
              disabled={isCancelling}
              className="inline-flex items-center gap-2 rounded-2xl border border-orange-500 bg-orange-500/90 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-orange-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <X size={16} />
              {isCancelling ? "Stopping…" : "Stop response"}
            </button>
          </div>
        )}

        {responseAudioUrl && (
          <div className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-900 p-3 text-sm text-slate-300">
            <span className="text-slate-400">Assistant audio:</span>
            <audio controls src={responseAudioUrl} className="w-full rounded-xl bg-slate-950" />
          </div>
        )}
      </div>
    </div>
  );
}
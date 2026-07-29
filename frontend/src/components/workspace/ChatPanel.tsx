"use client";
import { useState } from "react";
import { useAppStore } from "@/store/useAppStore";
import { api } from "@/lib/api";
import { ModeSelector } from "@/components/chat/ModeSelector";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { VoiceRecorder } from "@/components/voice/VoiceRecorder";
import { Send, Loader2, History } from "lucide-react";
import { HistoryPanel } from "@/components/chat/HistoryPanel";

export function ChatPanel() {
  const { messages, addMessage, mode, sessionId, isThinking, setThinking } = useAppStore();
  const [input, setInput] = useState("");
  const [showHistory, setShowHistory] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isThinking) return;
    const question = input.trim();
    setInput("");
    addMessage({ id: crypto.randomUUID(), role: "user", content: question });
    setThinking(true);
    try {
      const res: any = await api.analyzeText(question, mode, sessionId);
      addMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        content: res.answer,
        confidence: res.confidence,
        sources: res.sources,
        searchUsed: res.search_used,
      });
    } catch (e) {
      addMessage({
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Something went wrong reaching the backend. Check it's running on port 8000.",
      });
    } finally {
      setThinking(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-800/80 bg-[linear-gradient(90deg,_rgba(15,23,42,0.95),_rgba(2,6,23,0.8))] px-6 py-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <p className="panel-heading">Workspace</p>
            <h2 className="section-title mt-2 text-[1.2rem]">AI document conversation</h2>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-2xl border border-slate-700/80 bg-slate-950/70 px-4 py-2 text-sm text-slate-300">
              Session: {sessionId}
            </span>
            <ModeSelector />
            <button
              type="button"
              onClick={() => setShowHistory(true)}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-700/80 bg-slate-950/70 px-3 py-2 text-sm font-medium text-slate-200 shadow-sm transition hover:border-sky-400/40 hover:bg-slate-900 hover:text-white"
              title="View history"
            >
              <History size={16} />
              <span>History</span>
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto bg-[linear-gradient(180deg,_rgba(15,23,42,0.35),_rgba(2,6,23,0.2))] p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="rounded-[1.6rem] border border-dashed border-slate-700/80 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.08),_transparent_60%),rgba(2,6,23,0.9)] p-10 text-center text-sm text-slate-400 shadow-inner shadow-slate-950/40">
            <p className="text-base font-medium text-slate-200">Ready for your first legal analysis</p>
            <p className="mt-2 text-slate-400">Upload a document, then ask a question or start a voice session for instant insight.</p>
          </div>
        ) : (
          messages.map((m) => <MessageBubble key={m.id} {...m} />)
        )}

        {isThinking && (
          <div className="flex items-center gap-3 rounded-[1.25rem] border border-sky-500/20 bg-slate-950/80 px-4 py-3 text-sm text-slate-300 shadow-sm shadow-slate-950/20">
            <Loader2 className="animate-spin text-sky-300" size={18} />
            Thinking… generating the best possible response.
          </div>
        )}
      </div>

      <div className="border-t border-slate-800/80 bg-slate-950/85 px-6 py-5">
        <div className="flex flex-col gap-3 rounded-[1.25rem] border border-slate-800/80 bg-slate-900/70 p-3 shadow-inner shadow-slate-950/40 sm:flex-row sm:items-center">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about the document…"
            className="input-surface border-0 bg-transparent px-2 py-2 shadow-none"
          />
          <button onClick={handleSend} className="button-primary w-full sm:w-auto">
            <Send size={16} className="mr-2" />
            Send question
          </button>
        </div>
        <div className="mt-4 hidden items-center justify-between text-xs text-slate-500 sm:flex">
          <span>Tip: Use concise legal queries for better results.</span>
          <span>Q&A, risk review, summary, compare, and extraction modes supported.</span>
        </div>
      </div>

      <div className="border-t border-slate-800/80 bg-slate-950/70 px-6 py-4">
        <VoiceRecorder />
      </div>

      {showHistory && <HistoryPanel onClose={() => setShowHistory(false)} />}
    </div>
  );
}

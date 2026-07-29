"use client";
import { useAppStore } from "@/store/useAppStore";
import { X, History as HistoryIcon, MessageSquare } from "lucide-react";
import { ConfidenceBadge } from "@/components/chat/ConfidenceBadge";

interface Props {
  onClose: () => void;
}

export function HistoryPanel({ onClose }: Props) {
  const messages = useAppStore((s) => s.messages);

  // group into Q&A pairs for readability
  const pairs: { question: string; answer: typeof messages[number] | null }[] = [];
  messages.forEach((m) => {
    if (m.role === "user") {
      pairs.push({ question: m.content, answer: null });
    } else if (pairs.length > 0) {
      pairs[pairs.length - 1].answer = m;
    }
  });

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/20" onClick={onClose}>
      <div
        className="w-full max-w-md h-full bg-white shadow-xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            <HistoryIcon size={16} />
            <span className="text-sm font-medium">Conversation history</span>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {pairs.length === 0 && (
            <p className="text-sm text-gray-400 text-center mt-10">
              No questions asked yet in this session.
            </p>
          )}
          {pairs.map((p, i) => (
            <div key={i} className="border rounded-lg p-3 space-y-2">
              <div className="flex items-start gap-2">
                <MessageSquare size={14} className="mt-0.5 text-gray-400 shrink-0" />
                <p className="text-sm font-medium text-gray-800">{p.question}</p>
              </div>
              {p.answer && (
                <div className="pl-6">
                  <p className="text-xs text-gray-600 leading-relaxed line-clamp-4">
                    {p.answer.content}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    {p.answer.confidence && <ConfidenceBadge level={p.answer.confidence} />}
                    {p.answer.searchUsed && (
                      <span className="text-[11px] text-gray-400">via {p.answer.searchUsed}</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
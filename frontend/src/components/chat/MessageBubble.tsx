import { ConfidenceBadge } from "@/components/chat/ConfidenceBadge";

interface Props {
  role: "user" | "assistant";
  content: string;
  confidence?: string;
  sources?: string[];
  searchUsed?: string;
}

export function MessageBubble({ role, content, confidence, sources, searchUsed }: Props) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[82%] rounded-[1.35rem] px-4 py-3 text-sm shadow-sm ${
          isUser
            ? "bg-gradient-to-br from-sky-600 to-cyan-500 text-white"
            : "border border-slate-700/80 bg-slate-900/90 text-slate-100"
        }`}
      >
        <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
        {!isUser && (confidence || sources?.length) && (
          <div className="mt-2 flex flex-wrap items-center gap-2">
            {confidence && <ConfidenceBadge level={confidence} />}
            {searchUsed && (
              <span className="text-[11px] text-slate-400">via {searchUsed}</span>
            )}
            {sources?.map((s, i) => (
              <span key={i} className="rounded-full border border-slate-700 bg-slate-950/70 px-2 py-0.5 text-[11px] text-slate-400">
                {s}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
"use client";
import { useAppStore } from "@/store/useAppStore";

export function InspectorPanel() {
  const messages = useAppStore((s) => s.messages);
  const last = [...messages].reverse().find((m) => m.role === "assistant");

  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-6 rounded-[1.2rem] border border-slate-800/80 bg-slate-950/70 p-4">
        <p className="panel-heading">Insight panel</p>
        <h2 className="section-title mt-2 text-xl">Latest AI analysis</h2>
      </div>

      {!last ? (
        <div className="rounded-3xl border border-dashed border-slate-700 bg-slate-950/70 p-6 text-sm text-slate-400">
          Ask a question to see confidence, sources, and search path details.
        </div>
      ) : (
        <div className="space-y-4">
          <div className="rounded-[1.2rem] border border-slate-800/80 bg-slate-950/75 p-4 shadow-[0_10px_30px_-20px_rgba(2,8,23,0.95)]">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Confidence</p>
            <p className="mt-3 text-2xl font-semibold text-white">{last.confidence ?? "—"}</p>
          </div>

          <div className="rounded-[1.2rem] border border-slate-800/80 bg-slate-950/75 p-4 shadow-[0_10px_30px_-20px_rgba(2,8,23,0.95)]">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Search path</p>
            <p className="mt-3 text-sm text-slate-200">{last.searchUsed ?? "—"}</p>
          </div>

          <div className="rounded-[1.2rem] border border-slate-800/80 bg-slate-950/75 p-4 shadow-[0_10px_30px_-20px_rgba(2,8,23,0.95)]">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Sources</p>
            {last.sources?.length ? (
              <ul className="mt-4 space-y-3">
                {last.sources.map((source, index) => (
                  <li
                    key={index}
                    className="rounded-2xl border border-slate-700 bg-slate-950/90 px-4 py-3 text-sm text-slate-300"
                  >
                    {source}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-slate-400">No sources were detected for this answer.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

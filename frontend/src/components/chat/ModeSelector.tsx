"use client";
import { useAppStore } from "@/store/useAppStore";
import { AnalysisMode } from "@/lib/types";

const modes: { value: AnalysisMode; label: string }[] = [
  { value: "qa", label: "Q&A" },
  { value: "risk", label: "Risk" },
  { value: "summary", label: "Summary" },
  { value: "compare", label: "Compare" },
  { value: "extract", label: "Extract" },
];

export function ModeSelector() {
  const mode = useAppStore((s) => s.mode);
  const setMode = useAppStore((s) => s.setMode);

  return (
    <div className="flex flex-wrap gap-2 rounded-2xl border border-slate-700/80 bg-slate-950/70 p-1.5 shadow-sm shadow-slate-950/20">
      {modes.map((m) => (
        <button
          key={m.value}
          onClick={() => setMode(m.value)}
          className={`rounded-xl px-3 py-2 text-xs font-semibold transition ${
            mode === m.value
              ? "bg-sky-500 text-slate-950 shadow-lg shadow-sky-500/20"
              : "text-slate-300 hover:bg-slate-900 hover:text-white"
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}

import { DocumentPanel } from "@/components/workspace/DocumentPanel";
import { ChatPanel } from "@/components/workspace/ChatPanel";
import { InspectorPanel } from "@/components/workspace/InspectorPanel";

export default function Home() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.16),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(59,130,246,0.12),_transparent_32%),linear-gradient(135deg,_#020617_0%,_#0f172a_40%,_#111827_100%)] text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-none flex-col px-2 py-2 lg:px-4 lg:py-4 2xl:px-6 2xl:py-5">
        <header className="mb-2 rounded-[1.6rem] border border-slate-800/80 bg-slate-900/60 px-5 py-4 shadow-[0_16px_60px_-28px_rgba(2,8,23,0.95)] backdrop-blur-2xl">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-4xl">
              <p className="text-[11px] font-semibold uppercase tracking-[0.38em] text-sky-300">LexAI Legal Intelligence</p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white sm:text-4xl lg:text-[2.35rem]">
                Legal review, risk detection, and document intelligence in one polished AI workspace.
              </h1>
            </div>
            <div className="flex flex-wrap gap-2.5">
              <div className="rounded-2xl border border-slate-700/80 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
                <span className="font-semibold text-white">Multimodal</span> · PDF · Image · Voice
              </div>
              <div className="rounded-2xl border border-slate-700/80 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
                <span className="font-semibold text-white">Traceable</span> · citations · confidence
              </div>
            </div>
          </div>
        </header>

        <main className="grid flex-1 gap-2.5 xl:grid-cols-[270px_minmax(0,1fr)_300px] 2xl:grid-cols-[300px_minmax(0,1fr)_330px]">
          <aside className="overflow-hidden rounded-[1.4rem] border border-slate-800/70 bg-slate-900/45 shadow-[0_16px_60px_-30px_rgba(2,8,23,0.92)] backdrop-blur-xl">
            <DocumentPanel />
          </aside>
          <section className="overflow-hidden rounded-[1.4rem] border border-slate-800/70 bg-slate-900/45 shadow-[0_14px_50px_-26px_rgba(2,8,23,0.9)] backdrop-blur-xl">
            <ChatPanel />
          </section>
          <aside className="overflow-hidden rounded-[1.4rem] border border-slate-800/70 bg-slate-900/40 shadow-[0_14px_50px_-26px_rgba(2,8,23,0.9)] backdrop-blur-xl">
            <InspectorPanel />
          </aside>
        </main>
      </div>
    </div>
  );
}

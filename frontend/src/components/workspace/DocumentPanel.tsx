"use client";
import { useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import { api } from "@/lib/api";
import { DropZone } from "@/components/upload/DropZone";
import { FileText } from "lucide-react";

export function DocumentPanel() {
  const { documents, setDocuments } = useAppStore();

  useEffect(() => {
    api.listDocuments().then((res: any) => setDocuments(res.documents ?? [])).catch(() => {});
  }, [setDocuments]);

  const handleClear = async () => {
    if (!confirm("Clear all documents?")) return;
    await api.clearDocuments();
    setDocuments([]);
  };

  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-5 rounded-[1.35rem] border border-slate-800/80 bg-slate-950/75 p-4 shadow-[0_10px_30px_-20px_rgba(2,8,23,0.95)]">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="panel-heading">Documents</p>
            <h2 className="section-title mt-2 text-xl">Knowledge base</h2>
          </div>
          <button
            onClick={handleClear}
            className="rounded-2xl border border-slate-700/80 bg-slate-900/80 px-3 py-2 text-xs font-semibold text-slate-300 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
            disabled={documents.length === 0}
          >
            Clear all
          </button>
        </div>
        <p className="mt-3 text-sm text-slate-400">Upload legal documents to build a searchable review workspace.</p>
      </div>

      <div className="rounded-[1.35rem] border border-sky-400/20 bg-gradient-to-br from-slate-900/90 to-slate-950/90 p-4 shadow-[0_12px_40px_-24px_rgba(2,8,23,0.95)]">
        <DropZone />
      </div>

      <div className="mt-5 rounded-[1.35rem] border border-slate-800/80 bg-slate-950/75 p-4 shadow-[0_10px_30px_-20px_rgba(2,8,23,0.95)]">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-200">Indexed files</p>
          <span className="rounded-full border border-slate-700/80 bg-slate-900/80 px-2.5 py-1 text-[11px] font-medium text-slate-400">
            {documents.length} {documents.length === 1 ? "file" : "files"}
          </span>
        </div>
        <div className="space-y-2 overflow-y-auto">
          {documents.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-700/80 bg-slate-900/70 p-4 text-sm text-slate-400">
              No documents loaded yet. Drop a PDF or image to start.
            </div>
          ) : (
            documents.map((d, index) => (
              <div
                key={d.id || d.filename || index}
                className="flex items-center gap-3 rounded-2xl border border-slate-800/80 bg-slate-900/80 px-3 py-3"
              >
                <div className="rounded-xl bg-sky-500/15 p-2 text-sky-300">
                  <FileText size={15} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-white">{d.filename || "Untitled document"}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    {d.chunks_created ? `${d.chunks_created} chunks indexed` : "Added to index"}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

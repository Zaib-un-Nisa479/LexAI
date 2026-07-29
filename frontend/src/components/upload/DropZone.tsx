"use client";
import { useDropzone } from "react-dropzone";
import { api } from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";
import { useState } from "react";
import { UploadCloud, Loader2 } from "lucide-react";

export function DropZone() {
  const setDocuments = useAppStore((s) => s.setDocuments);
  const [uploading, setUploading] = useState(false);

  const onDrop = async (files: File[]) => {
    setUploading(true);
    try {
      for (const file of files) {
        const isImage = file.type.startsWith("image/");
        if (isImage) {
          await api.analyzeVision(file, "Extract and summarize all text from this document", true);
        } else {
          await api.ingestPdf(file);
        }
      }
      const res: any = await api.listDocuments();
      setDocuments(res.documents ?? []);
    } catch (e) {
      console.error(e);
      alert("Upload failed — check the backend terminal for details.");
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "image/*": [".png", ".jpg", ".jpeg"] },
  });

  return (
    <div
      {...getRootProps()}
      className={`cursor-pointer rounded-[1.25rem] border-2 border-dashed p-6 text-center transition-all ${
        isDragActive
          ? "border-sky-400 bg-sky-500/10 shadow-[0_0_0_1px_rgba(56,189,248,0.2)]"
          : "border-slate-700/80 bg-slate-950/60 hover:border-slate-500 hover:bg-slate-900/70"
      }`}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <div className="flex flex-col items-center gap-2 text-sm text-slate-300">
          <Loader2 className="animate-spin text-sky-300" size={20} />
          Ingesting documents…
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2 text-sm text-slate-300">
          <div className="rounded-2xl bg-sky-500/15 p-3 text-sky-300">
            <UploadCloud size={22} />
          </div>
          <p className="font-semibold text-white">Drop a PDF or image here</p>
          <p className="text-xs text-slate-400">Supported formats: PDF, PNG, JPG, JPEG</p>
        </div>
      )}
    </div>
  );
}
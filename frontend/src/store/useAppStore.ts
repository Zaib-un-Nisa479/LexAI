import { create } from "zustand";
import { AnalysisMode } from "@/lib/types";

export interface DocumentItem {
  id: string;
  filename: string;
  chunks_created?: number;
  [key: string]: unknown;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  confidence?: string;
  sources?: string[];
  searchUsed?: string;
}

interface AppState {
  mode: AnalysisMode;
  setMode: (mode: AnalysisMode) => void;
  documents: DocumentItem[];
  setDocuments: (documents: DocumentItem[]) => void;
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;
  sessionId: string;
  setSessionId: (sessionId: string) => void;
  isThinking: boolean;
  setThinking: (isThinking: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  mode: "qa",
  setMode: (mode) => set({ mode }),
  documents: [],
  setDocuments: (documents) => set({ documents }),
  messages: [],
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  sessionId: "default",
  setSessionId: (sessionId) => set({ sessionId }),
  isThinking: false,
  setThinking: (isThinking) => set({ isThinking }),
}));

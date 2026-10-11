export function listen(onText: (t: string) => void, onError: (m: string) => void) {
  const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (!SR) return onError("Voice input needs Chrome or Edge.");
  const rec = new SR();
  rec.lang = "en-US";
  rec.onresult = (e: any) => onText(e.results[0][0].transcript);
  rec.onerror = (e: any) => onError(e.error);
  rec.start();
}

export function speak(text: string) {
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "en-US";
  window.speechSynthesis.speak(u);
}
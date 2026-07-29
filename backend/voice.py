import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from gtts import gTTS
from config import WHISPER_MODEL_SIZE
import os, tempfile

# load once at module level — cached in memory after first load
print(f"Loading Whisper {WHISPER_MODEL_SIZE} model...")
whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
print("Whisper ready.")

def transcribe_audio_file(audio_path: str) -> dict:
    """
    Transcribe an audio file to text using Whisper.
    Accepts: WAV, MP3, M4A, FLAC, OGG — Whisper handles all formats.
    Returns transcription + detected language + confidence.
    WHY: Core of voice input — converts speech to text for the agent.
    """
    result = whisper_model.transcribe(
        audio_path,
        language=None,  # auto-detect language — handles Urdu, Arabic, etc.
        task="transcribe",
        verbose=False
    )
    return {
        "text": result["text"].strip(),
        "language": result.get("language", "unknown"),
        "segments": len(result.get("segments", []))
    }

def transcribe_audio_bytes(audio_bytes: bytes, suffix: str = ".wav") -> dict:
    """
    Transcribe audio from bytes (received from FastAPI upload).
    FastAPI gives you bytes — save to temp file, transcribe, clean up.
    WHY: FastAPI receives uploaded files as bytes objects, not file paths.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        result = transcribe_audio_file(tmp_path)
        return result
    finally:
        os.unlink(tmp_path)  # always clean up temp file

def text_to_speech(text: str, output_path: str = "response.mp3") -> str:
    """
    Convert text to speech using gTTS.
    Returns path to the generated audio file.
    WHY: Voice output completes the voice loop — answer is spoken back.
    """
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(output_path)
    return output_path

def record_from_microphone(seconds: int = 8, output_path: str = "input.wav") -> str:
    """
    Record audio from system microphone.
    Used for local testing — Streamlit frontend handles this in browser.
    WHY: Lets you test voice pipeline without the frontend running.
    """
    sample_rate = 16000
    print(f"Recording {seconds} seconds... speak now")
    audio = sd.rec(int(seconds * sample_rate), samplerate=sample_rate,
        channels=1, dtype=np.int16)
    sd.wait()
    wav.write(output_path, sample_rate, audio)
    print("Recording complete.")
    return output_path
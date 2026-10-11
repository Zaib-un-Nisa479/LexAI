import os

from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
except Exception as exc:
    Groq = None
    groq_import_error = exc
else:
    groq_import_error = None

try:
    from gtts import gTTS
except Exception as exc:
    TTS = None
    gtts_import_error = exc
else:
    TTS = gTTS
    gtts_import_error = None

# Speech-to-text runs on Groq's servers, so nothing heavy loads on Render.
GROQ_STT_MODEL = os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo")

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if Groq is None:
        raise RuntimeError(f"groq package is not installed: {groq_import_error}")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in the environment")
    _client = Groq(api_key=api_key, timeout=45.0, max_retries=1)
    return _client


def transcribe_audio_bytes(audio_bytes: bytes, suffix: str = ".webm") -> dict:
    """
    Transcribe uploaded audio using Groq's hosted Whisper.
    Accepts flac, mp3, mp4, m4a, ogg, opus, wav, webm.
    The file extension matters: Groq uses it to detect the format.
    Returns the same shape as before: text, language, segments.
    """
    if not suffix.startswith("."):
        suffix = "." + suffix

    client = _get_client()
    result = client.audio.transcriptions.create(
        file=(f"audio{suffix}", audio_bytes),
        model=GROQ_STT_MODEL,
        response_format="verbose_json",  # includes detected language
        temperature=0.0,
    )
    text = (getattr(result, "text", "") or "").strip()
    return {
        "text": text,
        "language": getattr(result, "language", None) or "unknown",
        "segments": len(getattr(result, "segments", None) or []),
    }


def transcribe_audio_file(audio_path: str) -> dict:
    """Transcribe an audio file on disk (same Groq call as the bytes version)."""
    with open(audio_path, "rb") as f:
        data = f.read()
    suffix = os.path.splitext(audio_path)[1] or ".wav"
    return transcribe_audio_bytes(data, suffix=suffix)


def text_to_speech(text: str, output_path: str = "response.mp3") -> str:
    """
    Convert text to speech using gTTS.
    Returns the path to the generated audio file.
    """
    if TTS is None:
        raise RuntimeError(f"Text-to-speech is not available: {gtts_import_error}")

    tts = TTS(text=text, lang="en", slow=False)
    tts.save(output_path)
    return output_path
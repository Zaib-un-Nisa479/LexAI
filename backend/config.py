from dotenv import load_dotenv
import os

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Paths
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")

# Model settings
# Use a Gemini Developer API model that is supported for generateContent.
# Newer models like gemini-2.5-flash and gemini-2.1 may not be available to all keys.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2-preview")
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")

# RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_CHUNKS = 4
RELEVANCE_THRESHOLD = 0.65  # below this = relevant, above = fallback to web
MAX_RETRIES = 2

# create upload dir if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# validate critical config on startup
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env file")
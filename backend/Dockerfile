FROM python:3.11-slim

WORKDIR /app

# system deps needed by torch/onnxruntime/chromadb
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces expects the app on port 7860
RUN useradd -m -u 1000 appuser
RUN mkdir -p /app/chroma_db /app/uploads && chown -R appuser:appuser /app
USER appuser

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
from config import EMBEDDING_MODEL
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os, traceback

print('EMBEDDING_MODEL=', EMBEDDING_MODEL)
emb = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
print('resolved model=', emb.model)
print('use_vertexai=', emb._use_vertexai)
print('vertexai field=', emb.vertexai)
print('api_version=', emb.api_version)
print('GOOGLE_GENAI_USE_VERTEXAI=', os.getenv('GOOGLE_GENAI_USE_VERTEXAI'))
print('GOOGLE_API_KEY=', bool(os.getenv('GOOGLE_API_KEY')))
print('GEMINI_API_KEY=', bool(os.getenv('GEMINI_API_KEY')))
print('client type=', type(emb.client))
try:
    res = emb.embed_query('hello world')
    print('embed_query succeeded, len=', len(res))
except Exception:
    traceback.print_exc()

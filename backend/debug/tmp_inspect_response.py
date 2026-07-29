from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_MODEL, GEMINI_API_KEY
import inspect

print('model', GEMINI_MODEL)
print('api_key set', bool(GEMINI_API_KEY))
llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY, temperature=0.1)
print('llm type', type(llm))
print('has invoke', hasattr(llm, 'invoke'))
print('invoke source snippet:')
print(inspect.getsource(llm.invoke)[:1000])

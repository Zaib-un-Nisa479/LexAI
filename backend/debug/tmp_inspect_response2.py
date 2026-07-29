from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_MODEL, GEMINI_API_KEY

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY, temperature=0.1)
print('llm type', type(llm))
resp = llm.invoke('Hello')
print('response type', type(resp))
print('has content', hasattr(resp, 'content'))
print('content type', type(resp.content))
print('content repr', repr(resp.content))
print('response dir sample', [x for x in dir(resp) if 'content' in x or 'message' in x or 'text' in x][:40])
try:
    print('to_dict', resp.to_dict())
except Exception as e:
    print('to_dict error', repr(e))

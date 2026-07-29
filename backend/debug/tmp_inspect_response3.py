from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_MODEL, GEMINI_API_KEY

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY, temperature=0.1)
resp = llm.invoke('Hello')
print('response type', type(resp))
print('has text', hasattr(resp, 'text'))
if hasattr(resp,'text'): print('text prop', repr(resp.text))
print('has content_blocks', hasattr(resp, 'content_blocks'))
if hasattr(resp,'content_blocks'): print('content_blocks', repr(resp.content_blocks))
print('content', repr(resp.content))
print('content type', type(resp.content))
print('dir filtered', [x for x in dir(resp) if x in ('text','content','content_blocks','role') or 'content' in x or 'text' in x])

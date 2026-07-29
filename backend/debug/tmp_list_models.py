from config import GEMINI_API_KEY
from google.genai import Client

print('GEMINI_API_KEY set=', bool(GEMINI_API_KEY))
client = Client(api_key=GEMINI_API_KEY)
print('client type', type(client))
print('has list_models', hasattr(client.models, 'list_models'))
if hasattr(client.models, 'list_models'):
    models = client.models.list_models()
    for i, m in enumerate(models):
        if i >= 100:
            break
        try:
            print(i+1, getattr(m, 'name', m))
        except Exception:
            print(i+1, m)
else:
    print('list_models not available')

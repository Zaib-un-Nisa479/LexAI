import langchain_chroma
from langchain_chroma.chroma import Chroma
import inspect

print('Chroma class cleanup methods:')
print([n for n in dir(Chroma) if any(k in n for k in ['close','persist','delete','drop','reset','shutdown','dispose'])])
print('close exists', hasattr(Chroma, 'close'))
print('persist exists', hasattr(Chroma, 'persist'))
print('delete exists', hasattr(Chroma, 'delete'))
print('drop exists', hasattr(Chroma, 'drop'))
print('dispose exists', hasattr(Chroma, 'dispose'))
if hasattr(Chroma, 'close'):
    print('close source:')
    try:
        print(inspect.getsource(Chroma.close))
    except Exception as e:
        print('close source error:', e)

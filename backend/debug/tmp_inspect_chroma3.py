import langchain_chroma
from langchain_chroma.vectorstores import Chroma
import inspect
print('vectorstores module file:', langlangchain_chroma.__file__)
print('chroma attrs:', [n for n in dir(Chroma) if any(k in n for k in ['close','persist','delete','drop','reset','shutdown','dispose'])])
print('has close', hasattr(Chroma, 'close'))
print('has persist', hasattr(Chroma, 'persist'))
print('has delete', hasattr(Chroma, 'delete'))
print('has drop', hasattr(Chroma, 'drop'))
print('has dispose', hasattr(Chroma, 'dispose'))
if hasattr(Chroma, 'close'):
    print(inspect.getsource(Chroma.close))

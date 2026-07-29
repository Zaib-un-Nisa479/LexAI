import langchain_chroma
import os
print('package file:', langchain_chroma.__file__)
package_dir = os.path.dirname(langchain_chroma.__file__)
print('package dir contents:')
for entry in sorted(os.listdir(package_dir)):
    print(' ', entry)
print('\nmodule attrs:')
for name in sorted(dir(langchain_chroma)):
    if 'Chroma' in name or 'chroma' in name.lower():
        print(' ', name)

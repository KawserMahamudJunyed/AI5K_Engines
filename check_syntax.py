import py_compile
import glob
import os

files = sorted(glob.glob('app/**/*.py', recursive=True) + glob.glob('tests/**/*.py', recursive=True))

broken = []
ok = []

for p in files:
    if p.endswith('__init__.py'):
        continue
    try:
        py_compile.compile(p, doraise=True)
        ok.append(p)
    except py_compile.PyCompileError as e:
        broken.append((p, str(e)))

print(f"OK: {len(ok)} files")
print(f"BROKEN: {len(broken)} files\n")
for path, err in broken:
    print(f"  {path}")
    # Print just the relevant line of the error
    for line in str(err).split('\n'):
        if 'Error' in line or 'indent' in line.lower() or 'syntax' in line.lower():
            print(f"    -> {line.strip()}")
    print()

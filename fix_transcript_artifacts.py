import glob
import re
import os


files = glob.glob('**/*.py', recursive=True)
fixed = 0

for p in files:
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if HEADER not in content:
        continue
    
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip the header line itself
        if HEADER in line:
            continue
        # Remove line number prefixes like "1: ", "42: ", "100: "
        cleaned = re.sub(r'^\d+: ', '', line)
        cleaned_lines.append(cleaned)
    
    # Also remove any trailing artifact lines like "45:" at the end
    while cleaned_lines and re.match(r'^\d+:?\s*$', cleaned_lines[-1]):
        cleaned_lines.pop()
    
    with open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    fixed += 1
    print(f"Fixed {p}")

print(f"\nTotal files cleaned: {fixed}")

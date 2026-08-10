import glob
import os

paths = glob.glob('**/*.py', recursive=True)
count = 0
for p in paths:
    if "AI5K_Agent" in os.path.abspath(p) and not p.startswith("recover_analyze"):
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        
        # 1. Update user.py to identity.py
        new_content = new_content.replace('app.models.identity', 'app.models.identity')
        
        # 2. Update all other model imports
        new_content = new_content.replace('from app.models.', 'from app.models.')
        new_content = new_content.replace('import app.models.', 'import app.models.')
        new_content = new_content.replace('from app.models ', 'from app.models ')
        new_content = new_content.replace('import app.models ', 'import app.models ')
        
        if new_content != content:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(new_content)
            count += 1
            
print(f"Updated imports in {count} files.")

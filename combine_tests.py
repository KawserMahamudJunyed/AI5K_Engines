import os

files_to_combine = [
    'tests/test_pipeline.py',
    'tests/test_opportunity.py',
    'tests/test_organization_capability.py',
    'tests/test_option_a_refinements.py'
]

combined_content = ""

for f in files_to_combine:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as src:
            combined_content += f"\n\n# --- {f} ---\n\n"
            combined_content += src.read()
            
if combined_content:
    with open('tests/test_trinity_engines.py', 'w', encoding='utf-8') as dst:
        dst.write(combined_content.strip())
    print("Combined tests into test_trinity_engines.py")
    
    # Remove old files
    for f in files_to_combine:
        if os.path.exists(f):
            os.remove(f)
            print(f"Removed {f}")

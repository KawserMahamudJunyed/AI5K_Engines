import json
import os

log_path = r"C:\Users\IT BD\.gemini\antigravity\brain\a96254e7-026e-48f8-b051-6185154dec3a\.system_generated\logs\transcript_full.jsonl"
file_content = None
found = False

with open(log_path, "r", encoding="utf-8") as f:
    for line in reversed(f.readlines()):
        try:
            entry = json.loads(line)
            if entry.get("type") == "PLANNER_RESPONSE":
                for tc in entry.get("tool_calls", []):
                    args = tc.get("arguments", {})
                    target = args.get("TargetFile", "")
                    if "test_trinity_engines.py" in target:
                        print("Found tool call:", tc["name"])
                        if tc["name"] == "write_to_file":
                            file_content = args["CodeContent"]
                            found = True
                            break
                        elif tc["name"] == "replace_file_content":
                            # The agent might have replaced chunks.
                            print("Replacement Chunk:", args.get("ReplacementContent", "")[:100])
        except Exception as e:
            print("Error parsing line:", e)
        
        if found:
            break

if found and file_content:
    with open("tests/test_trinity_engines.py", "w", encoding="utf-8") as out:
        out.write(file_content)
    print("Recovered test_trinity_engines.py from write_to_file!")
else:
    print("Could not find a full write_to_file. Trying to find if the agent read it first.")

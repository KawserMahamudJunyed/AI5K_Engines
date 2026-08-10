import json
import re

log_path = r"C:\Users\IT BD\.gemini\antigravity\brain\a96254e7-026e-48f8-b051-6185154dec3a\.system_generated\logs\transcript_full.jsonl"
file_parts = []

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line)
            if entry.get("type") == "PLANNER_RESPONSE":
                # Maybe tool responses are in SYSTEM_RESPONSE?
                pass
            if entry.get("type") == "SYSTEM_RESPONSE":
                for tr in entry.get("tool_responses", []):
                    if tr["name"] == "view_file":
                        out = tr.get("response", {}).get("output", "")
                        # The output contains the lines.
                        # "1: import pytest\n2: ..."
                        if "test_trinity_engines.py" in out:
                            file_parts.append(out)
        except Exception as e:
            pass

if not file_parts:
    print("No view_file responses found in subagent log.")
else:
    print(f"Found {len(file_parts)} view_file parts.")
    # We can reconstruct it!
    # Write the parts to a temp file so I can inspect them.
    with open("view_parts.txt", "w", encoding="utf-8") as out:
        for p in file_parts:
            out.write(p)
            out.write("\n===========================\n")

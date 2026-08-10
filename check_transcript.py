import json
import os

log_path = r"C:\Users\IT BD\.gemini\antigravity\brain\a96254e7-026e-48f8-b051-6185154dec3a\.system_generated\logs\transcript_full.jsonl"
file_content = None

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line)
            if entry.get("type") == "PLANNER_RESPONSE":
                for tc in entry.get("tool_calls", []):
                    if tc["name"] in ("write_to_file", "replace_file_content"):
                        args = tc.get("arguments", {})
                        if "TargetFile" in args and "test_trinity_engines" in args["TargetFile"]:
                            # If they replaced chunks, this is harder.
                            # But if we can find the complete file from somewhere else?
                            print(tc["name"], "called")
        except:
            pass

import json
import re

log_path = r"C:\Users\IT BD\.gemini\antigravity\brain\061aea66-d29a-45cb-8a78-c49093243a1a\.system_generated\logs\transcript_full.jsonl"
file_content = None

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line)
            if entry.get("type") == "PLANNER_RESPONSE":
                for tc in entry.get("tool_calls", []):
                    args = tc.get("arguments", {})
                    # Look for the combination script or write_to_file
                    if tc["name"] == "write_to_file" and "test_trinity_engines" in args.get("TargetFile", ""):
                        file_content = args.get("CodeContent")
                        print("Found write_to_file for test_trinity_engines!")
                    if tc["name"] == "run_command" and "cat " in args.get("CommandLine", "") and ">" in args.get("CommandLine", ""):
                        print("Found cat combination script:", args.get("CommandLine"))
        except:
            pass

if file_content:
    with open("tests/test_trinity_engines.py", "w", encoding="utf-8") as out:
        out.write(file_content)
    print("Recovered!")
else:
    print("Not found via write_to_file.")

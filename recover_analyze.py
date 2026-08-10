import json
import os
import re

TRANSCRIPT_PATH = r"C:\Users\IT BD\.gemini\antigravity\brain\061aea66-d29a-45cb-8a78-c49093243a1a\.system_generated\logs\transcript_full.jsonl"

file_states = {}

def process_transcript():
    print("Reading transcript...")
    with open(TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line)
            except:
                continue
            
            # 1. Capture full contents from view_file if it's the first time we see it
            if entry.get("type") == "VIEW_FILE" or (entry.get("type") == "TOOL_RESPONSE" and "File Path:" in str(entry.get("content", ""))):
                # Actually, VIEW_FILE might be the tool call, let's just parse TOOL_RESPONSE
                content_str = str(entry.get("content", ""))
                path_match = re.search(r"File Path: `file:///([^`]+)`", content_str)
                if path_match:
                    path = path_match.group(1).replace('%20', ' ').replace('/', '\\')
                    if len(path) > 1 and path[1] == ':':
                        path = path[0].upper() + path[1:]
                    
                    lines_match = re.search(r"Showing lines \d+ to \d+\n(.*?)\n(?:The above content|$)", content_str, re.DOTALL)
                    if lines_match:
                        raw_lines = lines_match.group(1).strip().split('\n')
                        clean_lines = [re.sub(r'^\d+: ', '', l) for l in raw_lines]
                        if path not in file_states:
                            file_states[path] = clean_lines

            # 2. Replay all write_to_file and replace_file_content mutations
            if entry.get("type") == "PLANNER_RESPONSE":
                tool_calls = entry.get("tool_calls", [])
                for tc in tool_calls:
                    name = tc.get("name", "")
                    args = tc.get("args", {})
                    
                    if name in ("default_api:write_to_file", "write_to_file"):
                        path = args.get("TargetFile")
                        code = args.get("CodeContent")
                        if path and code:
                            if len(path) > 1 and path[1] == ':':
                                path = path[0].upper() + path[1:]
                            file_states[path] = code.split('\n')
                            
                    elif name in ("default_api:replace_file_content", "replace_file_content"):
                        path = args.get("TargetFile")
                        if path:
                            if len(path) > 1 and path[1] == ':':
                                path = path[0].upper() + path[1:]
                            if path in file_states:
                                start = args.get("StartLine", 1) - 1
                                end = args.get("EndLine", 1)
                                replacement = args.get("ReplacementContent", "").split('\n')
                                file_states[path] = file_states[path][:start] + replacement + file_states[path][end:]

    # Now write the files out
    count = 0
    for path, lines in file_states.items():
        if "AI5K_Agent" in path and path.endswith('.py'):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as out:
                out.write('\n'.join(lines))
            print(f"Recovered {path}: {len(lines)} lines")
            count += 1
            
    print(f"Total Python files recovered: {count}")

if __name__ == "__main__":
    process_transcript()

import re
from pathlib import Path
content = Path("orion_tool_loop.py").read_text(encoding='utf-8', errors='ignore')
match = re.search(r'SYSTEM_PROMPT\s*=\s*"""(.*?)"""', content, re.DOTALL)
if match:
    print(match.group(1)[:1200])

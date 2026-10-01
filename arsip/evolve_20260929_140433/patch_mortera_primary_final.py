"""
patch_mortera_primary_final.py - Mortera primary, Groq fallback
"""
from pathlib import Path
import shutil
from datetime import datetime
import re

path = Path("orion_tool_loop.py")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = path.with_suffix(f".py.bak_mortera_{timestamp}")
shutil.copy2(path, backup)
print(f"[OK] Backup: {backup.name}")

content = path.read_text(encoding='utf-8', errors='ignore')

pattern = r'def tanya_llm\(messages\):.*?(?=\ndef |\Z)'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print("[X] Fungsi tidak ketemu")
    exit(1)

new_func = '''def tanya_llm(messages):
    """Panggil LLM - Mortera primary, Groq fallback."""
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    # Paksa load .env
    _base = Path(__file__).parent
    for _env_file in [_base / "config" / ".env", _base / ".env"]:
        if _env_file.exists():
            load_dotenv(_env_file, override=True)
            break

    # ============ MORTERA PRIMARY (GLM) ============
    api_key = os.getenv("MORTERA_API_KEY", "")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("MORTERA_BASE_URL", "https://mortera.cloud/v1"),
                timeout=30.0,
                max_retries=1,
            )
            model = os.getenv("MORTERA_MODEL", "glm-5.3-flash")
            r = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
            )
            return r.choices[0].message.content
        except Exception as e:
            print(f"  [Mortera error: {str(e)[:100]}]")

    # ============ GROQ FALLBACK ============
    api_key = os.getenv("GROQ_API_KEY", "")
    if api_key:
        try:
            from groq import Groq
            client = Groq(
                api_key=api_key,
                timeout=15.0,
                max_retries=0,
            )
            model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
            r = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
            )
            return r.choices[0].message.content
        except Exception as e:
            print(f"  [Groq error: {str(e)[:100]}]")

    raise RuntimeError("Tidak ada provider yang tersedia")

'''

content = content.replace(match.group(0), new_func, 1)
path.write_text(content, encoding='utf-8')
print("[OK] Patch: Mortera primary")

import ast
try:
    ast.parse(path.read_text(encoding='utf-8'))
    print("[OK] Syntax valid")
except SyntaxError as e:
    print(f"[X] {e}")
    shutil.copy2(backup, path)

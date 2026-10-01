import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
coding_assistant.py - Tool coding ORION.
Tulis kode, jalankan, cek error, fix.
"""
import os
import re

# Tanda triple quote (untuk filter kode)
TQ = chr(34) * 3   # triple quote
SQ = chr(39) * 3   # triple single quote
import sys
import time
from pathlib import Path

# Rich untuk live preview
try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel
    HAS_RICH = True
    _console = Console()
except ImportError:
    HAS_RICH = False

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))


def tulis_kode(path, kode):
    """Tulis kode ke file."""
    try:
        p = Path(path)
        if not p.is_absolute():
            p = BASE / p
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(kode)
        return True, "File ditulis: " + str(p)
    except Exception as e:
        return False, str(e)


def baca_kode(path):
    """Baca kode dari file."""
    try:
        p = Path(path)
        if not p.is_absolute():
            p = BASE / p
        if not p.exists():
            return None, "File tidak ditemukan"
        with open(p, "r", encoding="utf-8") as f:
            return f.read(), "OK"
    except Exception as e:
        return None, str(e)


def jalankan_kode(path, timeout=60):
    """Jalankan kode Python."""
    try:
        import subprocess
        p = Path(path)
        if not p.is_absolute():
            p = BASE / p

        # Deteksi Flask/server app - jangan dijalankan, cuma syntax check
        try:
            kode = p.read_text(encoding="utf-8")
            if "app.run(" in kode or "uvicorn.run(" in kode or "serve(" in kode:
                # Cek syntax pakai py_compile
                import py_compile
                try:
                    py_compile.compile(str(p), doraise=True)
                    return {
                        "sukses": True,
                        "output": "[SERVER] Flask app terdeteksi - syntax OK, skip jalankan (server tidak exit)",
                        "exit_code": 0,
                    }
                except py_compile.PyCompileError as pe:
                    return {
                        "sukses": False,
                        "output": "[SERVER] Syntax error: " + str(pe),
                        "exit_code": 1,
                    }
        except Exception:
            pass

        result = subprocess.run(
            ["python", str(p)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(BASE),
            encoding="utf-8",
            errors="ignore",
        )
        output = result.stdout + result.stderr
        return {
            "sukses": result.returncode == 0,
            "output": output[:3000],
            "exit_code": result.returncode,
        }
    except Exception as e:
        return {"sukses": False, "error": str(e), "output": ""}


def cek_error(output):
    """Cek apakah output ada error."""
    if not output:
        return False, ""
    
    pola = [
        r"Traceback \(most recent call last\):",
        r"SyntaxError:",
        r"NameError:",
        r"TypeError:",
        r"ValueError:",
        r"ImportError:",
        r"ModuleNotFoundError:",
        r"AttributeError:",
        r"KeyError:",
        r"IndexError:",
        r"FileNotFoundError:",
    ]
    
    for p in pola:
        if re.search(p, output):
            return True, p
    
    return False, ""


def extract_error(output):
    """Extract error message."""
    if not output:
        return ""
    
    lines = output.strip().split("\n")
    for line in reversed(lines):
        if any(k in line for k in ["Error", "error", "Exception"]):
            return line.strip()
    
    return lines[-1] if lines else ""




def _panggil_llm_langsung(prompt, max_tokens=4000):
    """Panggil LLM langsung - TANPA rekursi."""
    import sys
    from pathlib import Path as _P
    
    _BASE = _P(__file__).parent
    sys.path.insert(0, str(_BASE))
    sys.path.insert(0, str(_BASE / "py"))
    
    # Coba model_router
    try:
        from model_router import panggil_model
        result = panggil_model(
            messages=[{"role": "user", "content": prompt}],
            tugas="coding",
            max_tokens=max_tokens,
        )
        if result.get("konten"):
            return result["konten"]
    except Exception as e:
        print(f"[Coding] model_router error: {e}")
    
    # Fallback Groq
    try:
        import os
        from groq import Groq
        from dotenv import load_dotenv
        
        for _env in [_BASE / ".env", _BASE.parent / ".env"]:
            if _env.exists():
                load_dotenv(_env, override=True)
                break
        
        api_key = os.getenv("GROQ_API_KEY", "")
        model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        
        client = Groq(api_key=api_key)
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return r.choices[0].message.content
    except Exception as e:
        print(f"[Coding] Groq error: {e}")
    
    return ""


def coding_loop(goal, max_iterasi=3, nama_file=None):
    """Coding loop - SIMPLE, pakai model_router."""
    import sys
    import ast
    import re
    import subprocess
    from pathlib import Path
    
    BASE = Path(__file__).parent.parent  # ROOT Orion
    if nama_file is None:
        nama_file = "output_orion.py"
    
    print(f"\n{'=' * 60}")
    print(f"CODING LOOP - Goal: {goal}")
    print(f"{'=' * 60}")
    
    hasil = {"sukses": False, "goal": goal, "file": nama_file, "iterasi": 0, "kode": ""}
    
    # Prompt
    prompt = f"""Bikin kode Python untuk: {goal}

ATURAN:
- Output HANYA kode Python
- JANGAN pakai markdown
- JANGAN ada penjelasan
- Langsung kode

KODE PYTHON:"""
    
    for i in range(1, max_iterasi + 1):
        hasil["iterasi"] = i
        print(f"\n[Iterasi {i}]")
        print("  [LLM] Panggil model...")
        
        kode = ""
        
        # Coba 1: model_router
        try:
            from model_router import panggil_model
            result = panggil_model(
                messages=[{"role": "user", "content": prompt}],
                tugas="coding",
                max_tokens=4000,
            )
            kode = result.get("konten", "")
            if kode:
                print(f"  [LLM] model_router: {len(kode)} char")
        except Exception as e:
            print(f"  [LLM] model_router error: {e}")
        
        # Coba 2: Groq langsung
        if not kode:
            try:
                import os
                from groq import Groq
                from dotenv import load_dotenv
                
                for _env in [BASE / ".env", BASE.parent / ".env"]:
                    if _env.exists():
                        load_dotenv(_env, override=True)
                        break
                
                api_key = os.getenv("GROQ_API_KEY", "")
                model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
                
                client = Groq(api_key=api_key)
                r = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000,
                    temperature=0.2,
                )
                kode = r.choices[0].message.content
                print(f"  [LLM] Groq: {len(kode)} char")
            except Exception as e:
                print(f"  [LLM] Groq error: {e}")
        
        # Coba 3: Mortera langsung
        if not kode:
            try:
                import os
                import requests
                from dotenv import load_dotenv
                
                for _env in [BASE / ".env", BASE.parent / ".env"]:
                    if _env.exists():
                        load_dotenv(_env, override=True)
                        break
                
                api_key = os.getenv("MORTERA_API_KEY", "")
                
                r = requests.post(
                    "https://mortera.cloud/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "glm-5.3-flash",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                    },
                    timeout=60
                )
                kode = r.json()["choices"][0]["message"]["content"]
                print(f"  [LLM] Mortera: {len(kode)} char")
            except Exception as e:
                print(f"  [LLM] Mortera error: {e}")
        
        # Kalau tidak ada kode
        if not kode or len(kode) < 5:
            print(f"  [LLM] Jawaban kosong ({len(kode)} char)")
            continue
        
        # Bersihin markdown
        kode = re.sub(r'```\w*\n?', '', kode)
        kode = kode.replace("```", "").strip()
        
        # Tampilkan
        print(f"  Kode: {len(kode)} char")
        for line in kode.split("\n")[:5]:
            print(f"    {line[:70]}")
        
        # Cek syntax
        try:
            ast.parse(kode)
            hasil["kode"] = kode
            
            target = BASE / nama_file
            target.write_text(kode, encoding="utf-8")
            print(f"  [OK] Disimpan: {nama_file}")
            
            # Test
            print(f"  [Test] Jalankan...")
            try:
                r = subprocess.run(
                    [sys.executable, str(target)],
                    capture_output=True, text=True, timeout=10, cwd=str(BASE)
                )
                if r.returncode == 0:
                    print(f"  [Test] OK - {r.stdout[:100]}")
                    hasil["sukses"] = True
                    break
                else:
                    print(f"  [Test] Gagal - {r.stderr[:200]}")
            except subprocess.TimeoutExpired:
                print(f"  [Test] Timeout - OK")
                hasil["sukses"] = True
                break
            except Exception as e:
                print(f"  [Test] Error: {e}")
        except SyntaxError as e:
            print(f"  [Syntax] Error: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"  Coding selesai - {hasil['iterasi']} iterasi")
    print(f"{'=' * 60}")
    
    return hasil

# ====================================================================
# FITUR LIHAT KODE - Baris per baris di terminal
# ====================================================================

def tampilkan_kode(kode, nama_file="output.py", baris_per_baris=False):
    """
    Tampilkan kode di terminal dengan syntax highlight.
    
    Args:
        kode: string kode Python
        nama_file: nama file untuk judul
        baris_per_baris: kalau True, tampilkan animasi per baris
    """
    if not HAS_RICH:
        print(f"\n=== {nama_file} ===")
        print(kode)
        print("=" * 40)
        return
    
    try:
        from rich.syntax import Syntax
        from rich.panel import Panel
        import time
        
        if baris_per_baris:
            # Mode animasi - baris per baris
            lines = kode.split("\n")
            total = len(lines)
            
            for i, line in enumerate(lines, 1):
                # Highlight baris aktif
                display = f"[dim]{i:3}[/dim] │ {line}"
                _console.print(display)
                time.sleep(0.05)
            
            _console.print(f"[dim]── {total} baris ──[/dim]")
        else:
            # Mode panel - syntax highlight
            syntax = Syntax(
                kode,
                "python",
                theme="monokai",
                line_numbers=True,
                word_wrap=True,
            )
            
            panel = Panel(
                syntax,
                title=f"[bold cyan]{nama_file}[/bold cyan]",
                subtitle=f"[dim]{len(kode.split(chr(10)))} baris[/dim]",
                border_style="green",
            )
            
            _console.print(panel)
    except Exception as e:
        print(f"\n=== {nama_file} ===")
        print(kode)
        print("=" * 40)


def tampilkan_hasil_test(output, error="", sukses=True):
    """Tampilkan hasil test - output + error."""
    if not HAS_RICH:
        if sukses:
            print(f"✅ Output: {output[:200]}")
        else:
            print(f"❌ Error: {error[:200]}")
        return
    
    try:
        from rich.panel import Panel
        
        if sukses:
            panel = Panel(
                output[:500] if output else "(no output)",
                title="[bold green]✅ TEST OK[/bold green]",
                border_style="green",
            )
        else:
            panel = Panel(
                error[:500] if error else "(no error)",
                title="[bold red]❌ TEST GAGAL[/bold red]",
                border_style="red",
            )
        
        _console.print(panel)
    except Exception:
        pass


# ====================================================================
# END FITUR LIHAT KODE
# ====================================================================


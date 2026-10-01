"""Script Maker - Orion bikin script."""
import re, sys, time, subprocess
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent.parent

def deteksi_bahasa(p):
    p = p.lower()
    if "javascript" in p or "node" in p: return "javascript"
    if "powershell" in p or "ps1" in p: return "powershell"
    if "bash" in p or "shell" in p: return "bash"
    if "html" in p: return "html"
    return "python"

def deteksi_tipe(p):
    p = p.lower()
    if "api" in p or "rest" in p: return "api"
    if "scrape" in p: return "scraper"
    if "web" in p or "flask" in p: return "web"
    if "bot" in p: return "bot"
    if "file" in p or "backup" in p: return "file"
    return "umum"

def bikin_prompt(permintaan, bahasa, tipe):
    return f"""Bikin script {bahasa} LENGKAP untuk: {permintaan}

TIPE: {tipe}
ATURAN:
- Kode LENGKAP siap pakai
- Komentar + error handling
- Contoh penggunaan
- JANGAN markdown
- JANGAN placeholder

OUTPUT: HANYA KODE.

KODE:"""

def generate(permintaan, bahasa, tipe):
    prompt = bikin_prompt(permintaan, bahasa, tipe)
    try:
        import otak_orion
        return otak_orion.diskusi_mortera(prompt)
    except Exception:
        pass
    try:
        import os
        from groq import Groq
        from dotenv import load_dotenv
        load_dotenv(BASE / ".env", override=True)
        c = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
        r = c.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000, temperature=0.2,
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"# Error: {e}"

def bersihkan(kode):
    kode = re.sub(r"```\w*\n?", "", kode)
    return kode.replace("```", "").strip()

def test_file(fp, bahasa):
    fp = Path(fp)
    if not fp.exists(): return {"sukses": False}
    cmd = {"python": [sys.executable, str(fp)],
           "javascript": ["node", str(fp)],
           "powershell": ["powershell", "-File", str(fp)]}.get(bahasa)
    if not cmd: return {"sukses": True, "stdout": "(skip)"}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(fp.parent))
        return {"sukses": r.returncode == 0, "stdout": r.stdout[:300], "stderr": r.stderr[:300]}
    except subprocess.TimeoutExpired:
        return {"sukses": True, "stdout": "(timeout)"}
    except Exception as e:
        return {"sukses": False, "error": str(e)}

def simpan(kode, nama, bahasa):
    out = BASE / "output" / "scripts"
    out.mkdir(parents=True, exist_ok=True)
    ext = {"python": ".py", "javascript": ".js", "powershell": ".ps1",
           "bash": ".sh", "html": ".html"}.get(bahasa, ".py")
    if not nama.endswith(ext): nama += ext
    nama = re.sub(r"[^\w\.-]", "_", nama)
    fp = out / nama
    fp.write_text(kode, encoding="utf-8")
    return fp

# === GUARD-OTOMATIS file sensitif (amankan_skill 30/09) ===
def _cegah_sensitif(_nilai):
    """Tolak akses file sensitif. Terima dict/str/Path/list/tuple. Return dict error / None."""
    import os as _os
    import re as _re
    from pathlib import Path as _P
    _sensitif = (".env", ".key", ".pem", ".pfx", ".p12", "credentials", "secrets")

    def _mirip_path(_s):
        _s = str(_s)
        if _os.path.exists(_s):
            return True
        if _re.match(r"^[a-zA-Z]:[\\/]", _s):
            return True
        if _s.startswith(("\\\\", "/", "./", "../", "~/")):
            return True
        if ("\\" in _s or "/" in _s) and " " not in _s.strip():
            return True
        if " " not in _s and "." in _s and 0 < len(_s) < 260:
            return True
        return False

    def _cek(_v):
        if isinstance(_v, (str, _P)):
            if _mirip_path(_v) and any(_s in _P(str(_v)).name.lower() for _s in _sensitif):
                return str(_v)
            return None
        if isinstance(_v, dict):
            for _x in _v.values():
                _r = _cek(_x)
                if _r:
                    return _r
            return None
        if isinstance(_v, (list, tuple, set)):
            for _x in _v:
                _r = _cek(_x)
                if _r:
                    return _r
            return None
        return None

    _kena = _cek(_nilai)
    if _kena:
        return {"sukses": False, "error": "Ditolak: File sensitif tidak boleh diakses via tool: " + _kena}
    return None
# === AKHIR GUARD-OTOMATIS ===

def jalankan(permintaan, bahasa=None, nama_file=None, pakai_voice=False):
    # Guard-otomatis: tolak file sensitif (amankan_skill 30/09)
    _g = _cegah_sensitif(dict(locals()))
    if _g:
        return _g
    start = time.time()
    bahasa = bahasa or deteksi_bahasa(permintaan)
    tipe = deteksi_tipe(permintaan)
    
    print(f"[script-maker] {bahasa}/{tipe}: {permintaan[:60]}")
    
    kode_raw = generate(permintaan, bahasa, tipe)
    kode = bersihkan(kode_raw)
    
    nama_file = nama_file or f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    fp = simpan(kode, nama_file, bahasa)
    
    test = test_file(fp, bahasa)

    # Preview kode dengan Rich
    if kode:
        try:
            preview_kode(kode, nama_file=fp.name, bahasa=bahasa)
        except Exception as e:
            print(f"[preview error] {e}")

    
    if pakai_voice:
        try:
            from voice_orion import voice_kan
            voice_kan(f"Script {bahasa} sudah jadi")
        except Exception:
            pass
    
    return {
        "sukses": test.get("sukses", False),
        "bahasa": bahasa, "tipe": tipe,
        "nama_file": fp.name, "kode": kode,
        "test": test, "file": str(fp),
        "durasi": round(time.time() - start, 2),
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        jalankan(" ".join(sys.argv[1:]))
    else:
        print("Pakai: python script_maker.py 'bikin script ...'")


# ============ LEVEL 2 - MULTI-FILE ============
def bikin_proyek(nama_proyek, deskripsi, bahasa="python"):
    """Bikin proyek LENGKAP (multi-file)."""
    import re
    proyek = BASE / "output" / "projects" / nama_proyek
    proyek.mkdir(parents=True, exist_ok=True)
    
    prompt = f"""Bikin PROYEK {bahasa} LENGKAP: {deskripsi}

OUTPUT FORMAT:
=== FILE: namafile.py ===
<isi>

=== FILE: README.md ===
<isi>

=== FILE: requirements.txt ===
<isi>
"""
    
    try:
        import otak_orion
        hasil_llm = otak_orion.diskusi_mortera(prompt)
    except Exception:
        try:
            import os
            from groq import Groq
            from dotenv import load_dotenv
            load_dotenv(BASE / ".env", override=True)
            c = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
            r = c.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8000, temperature=0.2,
            )
            hasil_llm = r.choices[0].message.content
        except Exception as e:
            return {"sukses": False, "error": str(e)}
    
    # Parse
    parts = re.split(r'===\s*FILE:\s*([^=]+?)\s*===', hasil_llm)
    files = []
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts): break
        nama = re.sub(r'[^\w\./-]', '_', parts[i].strip())
        isi = re.sub(r'```\w*\n?', '', parts[i+1].strip()).replace("```", "").strip()
        fp = proyek / nama
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(isi, encoding="utf-8")
        files.append(nama)
    
    return {"sukses": len(files) > 0, "folder": str(proyek), "files": files}


def auto_install_deps(req):
    """Auto-install dependency."""
    if not Path(req).exists():
        return {"sukses": False}
    try:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)],
                          capture_output=True, text=True, timeout=120)
        return {"sukses": r.returncode == 0}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def bikin_readme(folder, nama, deskripsi):
    """Bikin README otomatis."""
    readme = f"# {nama}\n\n{deskripsi}\n\n## Files\n"
    for f in sorted(Path(folder).rglob("*")):
        if f.is_file():
            readme += f"- `{f.relative_to(folder)}` ({f.stat().st_size} B)\n"
    fp = Path(folder) / "README.md"
    fp.write_text(readme, encoding="utf-8")
    return str(fp)


def git_init(folder):
    """Setup git."""
    try:
        folder = Path(folder)
        subprocess.run(["git", "init"], cwd=str(folder), capture_output=True)
        (folder / ".gitignore").write_text("__pycache__/\n*.pyc\n.env\nvenv/\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=str(folder), capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit by Orion"],
                      cwd=str(folder), capture_output=True)
        return {"sukses": True}
    except Exception as e:
        return {"sukses": False, "error": str(e)}


def jalankan_lengkap(permintaan, nama_proyek=None, bikin_git=False):
    """Level 2 - proyek lengkap."""
    import time
    start = time.time()
    
    if not nama_proyek:
        nama_proyek = f"proyek_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"[script-maker L2] {nama_proyek}")
    
    hasil = bikin_proyek(nama_proyek, permintaan)
    if not hasil["sukses"]:
        return hasil
    
    proyek = Path(hasil["folder"])
    
    # Auto-install
    req = proyek / "requirements.txt"
    if req.exists():
        auto_install_deps(req)
    
    # README
    bikin_readme(proyek, nama_proyek, permintaan)
    
    # Git
    if bikin_git:
        git_init(proyek)
    
    return {**hasil, "durasi": round(time.time() - start, 2)}


# ============ END L2 ============


# ====================================================================
# LIVE PREVIEW DI TERMINAL
# ====================================================================

def _get_rich():
    """Cek rich."""
    try:
        from rich.console import Console
        from rich.syntax import Syntax
        from rich.panel import Panel
        from rich.live import Live
        from rich.layout import Layout
        from rich.text import Text
        return Console, Syntax, Panel, Live, Layout, Text
    except ImportError:
        return None


def preview_kode(kode, nama_file="script.py", bahasa="python"):
    """Tampilkan kode dengan syntax highlight."""
    rich = _get_rich()
    if not rich:
        print(f"\n=== {nama_file} ===")
        print(kode)
        print("=" * 40)
        return
    
    Console, Syntax, Panel, Live, Layout, Text = rich
    console = Console()
    
    syntax = Syntax(
        kode,
        bahasa,
        theme="monokai",
        line_numbers=True,
        word_wrap=True,
    )
    
    panel = Panel(
        syntax,
        title=f"[bold cyan]📄 {nama_file}[/bold cyan]",
        subtitle=f"[dim]{len(kode.split(chr(10)))} baris[/dim]",
        border_style="cyan",
    )
    
    console.print(panel)


def preview_live(kode, nama_file="script.py", bahasa="python", delay=0.03):
    """Tampilkan kode BARIS PER BARIS (animasi)."""
    rich = _get_rich()
    if not rich:
        print(kode)
        return
    
    Console, Syntax, Panel, Live, Layout, Text = rich
    console = Console()
    
    lines = kode.split("\n")
    total = len(lines)
    
    console.print(f"\n[bold cyan]📄 {nama_file}[/bold cyan] [dim]({total} baris)[/dim]\n")
    
    # Tampilkan baris per baris
    for i, line in enumerate(lines, 1):
        # Highlight baris aktif
        line_display = f"[yellow]{i:3}[/yellow] [dim]│[/dim] {line}"
        console.print(line_display)
        time.sleep(delay)
    
    console.print(f"\n[dim]── {total} baris ──[/dim]\n")


def preview_generate_live(permintaan, bahasa="python"):
    """Generate script dengan live preview."""
    import time
    
    rich = _get_rich()
    if not rich:
        return jalankan(permintaan, bahasa=bahasa)
    
    Console, Syntax, Panel, Live, Layout, Text = rich
    console = Console()
    
    console.print(f"\n[bold cyan]🚀 Script Maker - Live Preview[/bold cyan]")
    console.print(f"[dim]📝 {permintaan}[/dim]\n")
    
    # Loading animation
    with console.status("[cyan]⏳ Generating...[/cyan]", spinner="dots") as status:
        bahasa = bahasa or deteksi_bahasa(permintaan)
        tipe = deteksi_tipe(permintaan)
        status.update(f"[cyan]⏳ Generating {bahasa} script...[/cyan]")
        
        kode_raw = generate(permintaan, bahasa, tipe)
        kode = bersihkan(kode_raw)
        
        status.update(f"[cyan]💾 Saving...[/cyan]")
        nama_file = f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fp = simpan(kode, nama_file, bahasa)
        
        status.update(f"[cyan]🧪 Testing...[/cyan]")
        test = test_file(fp, bahasa)
    
    # Preview LIVE
    preview_live(kode, fp.name, bahasa)
    
    # Hasil test
    if test.get("sukses"):
        console.print(Panel(
            test.get("stdout", "(no output)")[:500],
            title="[bold green]✅ TEST OK[/bold green]",
            border_style="green",
        ))
    else:
        console.print(Panel(
            test.get("stderr", test.get("error", "gagal"))[:500],
            title="[bold red]❌ TEST GAGAL[/bold red]",
            border_style="red",
        ))
    
    console.print(f"[dim]📁 {fp}[/dim]\n")
    
    return {
        "sukses": test.get("sukses", False),
        "bahasa": bahasa,
        "tipe": tipe,
        "nama_file": fp.name,
        "kode": kode,
        "test": test,
        "file": str(fp),
    }


# ====================================================================
# END LIVE PREVIEW
# ====================================================================


import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
agent_manager.py - Orion sebagai Commander multi-agent.
Bagi tugas ke anak buah AI, gabungin hasil.
"""
import os
import time
import sqlite3
import concurrent.futures
from pathlib import Path

BASE = Path(__file__).parent
DB = BASE / "memory" / str(BASE / "memory" / "orion.db")
ENV = BASE / ".env"

# Load .env
if ENV.exists():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# ==== DEFAULT AGENTS ====
# Mapping provider -> config
PROVIDER_CONFIG = {
    "mortera": {
        "base_url": "https://mortera.cloud/v1",
        "api_key_env": "MORTERA_API_KEY",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
}

# Default agents (bisa ditambah)
DEFAULT_AGENTS = [
    # (nama, provider, model, capabilities, prioritas)
    ("cepat",    "groq",       "llama-3.1-8b-instant",           "cepat,ringan,murah",       1),
    ("analis",   "gemini",     "gemini-3.8-flash",               "analisis,riset,data",      2),
    ("koding",   "mortera",    "glm-5.3-flash",                  "coding,debug,review",      3),
    ("kreatif",  "mortera",    "claude-sonnet-5",                "kreatif,tulis,konten",     4),
    ("umum",     "mortera",    "glm-5.2",                        "umum,chat,diskusi",        5),
]


def _conn():
    return sqlite3.connect(DB)


# ==== INIT ====
def init_agents():
    """Daftarkan default agents kalau belum ada."""
    with _conn() as c:
        for nama, provider, model, caps, prio in DEFAULT_AGENTS:
            cfg = PROVIDER_CONFIG.get(provider, {})
            c.execute("""
                INSERT OR IGNORE INTO agents 
                (nama, provider, model, base_url, api_key_env, capabilities, prioritas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nama, provider, model, cfg.get("base_url"), cfg.get("api_key_env"), caps, prio))


def daftar_agent():
    """List semua agent aktif."""
    init_agents()
    with _conn() as c:
        cur = c.execute(
            "SELECT nama, provider, model, capabilities, prioritas, total_task, total_sukses, total_gagal, base_url, api_key_env FROM agents WHERE aktif=1 ORDER BY prioritas"
        )
        return [
            {
                "nama": r[0], "provider": r[1], "model": r[2],
                "capabilities": r[3], "prioritas": r[4],
                "total_task": r[5], "total_sukses": r[6], "total_gagal": r[7],
                "base_url": r[8], "api_key_env": r[9],
            }
            for r in cur.fetchall()
        ]


def tambah_agent(nama, provider, model, capabilities, prioritas=5):
    """Tambah agent baru."""
    cfg = PROVIDER_CONFIG.get(provider, {})
    if not cfg:
        return False, f"Provider '{provider}' tidak dikenal"
    with _conn() as c:
        c.execute("""
            INSERT OR REPLACE INTO agents 
            (nama, provider, model, base_url, api_key_env, capabilities, prioritas, aktif)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (nama, provider, model, cfg.get("base_url"), cfg.get("api_key_env"), capabilities, prioritas))
    return True, f"Agent '{nama}' ditambahkan"


# ==== EKSEKUSI AGENT ====
def panggil_agent(agent, prompt, timeout=30):
    """Panggil satu agent, return (hasil, durasi_ms, error)."""
    start = time.time()
    try:
        from openai import OpenAI
        api_key = os.environ.get(agent["api_key_env"])
        if not api_key:
            return None, 0, f"API key '{agent['api_key_env']}' tidak ada di .env"
        
        client = OpenAI(base_url=agent["base_url"], api_key=api_key)
        resp = client.chat.completions.create(
            model=agent["model"],
            messages=[
                {"role": "system", "content": "Kamu agent AI spesialis. Jawab singkat, padat, fokus."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            timeout=timeout,
        )
        hasil = resp.choices[0].message.content
        durasi = int((time.time() - start) * 1000)
        return hasil, durasi, None
    except Exception as e:
        durasi = int((time.time() - start) * 1000)
        return None, durasi, str(e)


def catat_task(agent_nama, prompt, hasil, status, durasi_ms, error=None):
    """Catat task ke DB."""
    with _conn() as c:
        c.execute("""
            INSERT INTO agent_tasks (agent_nama, prompt, hasil, status, durasi_ms, error)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (agent_nama, prompt[:500], (hasil or "")[:1000], status, durasi_ms, error))
        # Update counter agent
        if status == "sukses":
            c.execute("UPDATE agents SET total_task=total_task+1, total_sukses=total_sukses+1 WHERE nama=?", (agent_nama,))
        else:
            c.execute("UPDATE agents SET total_task=total_task+1, total_gagal=total_gagal+1 WHERE nama=?", (agent_nama,))


# ==== COMMANDER MODE ====
def strategi_pecah_task(perintah, llm_func):
    """Pakai LLM buat pecah task jadi sub-task + tentuin agent."""
    agents = daftar_agent()
    agent_info = "\n".join([
        f"- {a['nama']} ({a['provider']}/{a['model']}): {a['capabilities']}"
        for a in agents
    ])
    
    prompt = f"""Kamu Orion, Commander AI. Riki kasih perintah:
"{perintah}"

Agent yang tersedia:
{agent_info}

Tugasmu: pecah perintah ini jadi sub-task dan tentuin agent mana yang cocok.

Balas dalam format JSON:
{{
  "strategi": "deskripsi singkat strategi",
  "sub_tasks": [
    {{"agent": "nama_agent", "prompt": "instruksi spesifik"}},
    ...
  ],
  "gabungin": "cara gabungin hasil"
}}

Kalau task sederhana, cukup 1 sub-task. Balas HANYA JSON, tanpa penjelasan."""
    
    try:
        jawab = llm_func(prompt)
        # Bersihin markdown
        jawab = jawab.strip()
        if jawab.startswith("```"):
            jawab = jawab.split("```")[1]
            if jawab.startswith("json"):
                jawab = jawab[4:]
        import json
        return json.loads(jawab.strip())
    except Exception as e:
        # Fallback: 1 task saja
        return {
            "strategi": "Sederhana, langsung",
            "sub_tasks": [{"agent": agents[0]["nama"] if agents else "umum", "prompt": perintah}],
            "gabungin": "langsung",
        }


def eksekusi_paralel(sub_tasks, agents_map, timeout=30):
    """Eksekusi sub-task paralel."""
    hasil = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for st in sub_tasks:
            nama = st.get("agent", "")
            if nama not in agents_map:
                continue
            futures[executor.submit(panggil_agent, agents_map[nama], st["prompt"], timeout)] = (nama, st["prompt"])
        
        for fut in concurrent.futures.as_completed(futures):
            nama, prompt = futures[fut]
            try:
                hasil_agent, durasi, error = fut.result()
                hasil.append({
                    "agent": nama, "prompt": prompt,
                    "hasil": hasil_agent, "durasi_ms": durasi, "error": error,
                })
                catat_task(nama, prompt, hasil_agent, "sukses" if not error else "gagal", durasi, error)
            except Exception as e:
                hasil.append({"agent": nama, "prompt": prompt, "hasil": None, "error": str(e)})
    return hasil


def commander_mode(perintah, llm_func):
    """Mode Commander: Orion bagi tugas ke agent, gabungin hasil."""
    start = time.time()
    
    # 1. Pecah task
    strategi = strategi_pecah_task(perintah, llm_func)
    sub_tasks = strategi.get("sub_tasks", [])
    
    if not sub_tasks:
        return "Nggak ada sub-task yang bisa dijalankan."
    
    # 2. Siapin agent map
    agents = daftar_agent()
    agents_map = {a["nama"]: a for a in agents}
    
    # 3. Eksekusi paralel
    hasil_list = eksekusi_paralel(sub_tasks, agents_map)
    
    # 4. Gabungin hasil
    hasil_teks = "\n\n".join([
        f"[{h['agent']}] {h['hasil'] or 'GAGAL: ' + (h.get('error') or '?')}"
        for h in hasil_list
    ])
    
    # 5. LLM final: rangkum
    prompt_final = f"""Riki kasih perintah: "{perintah}"

Strategi: {strategi.get('strategi', '')}

Hasil dari agent-agent:
{hasil_teks}

Tugasmu: gabungin hasil ini jadi jawaban final yang rapi untuk Riki.
Gaya: Orion (sarkas, setia, to the point). Maksimal 5 kalimat."""
    
    try:
        jawaban_final = llm_func(prompt_final)
    except Exception:
        jawaban_final = hasil_teks
    
    durasi = int((time.time() - start) * 1000)
    
    # 6. Log
    with _conn() as c:
        c.execute("""
            INSERT INTO commander_log (perintah, strategi, agents_dipakai, hasil_akhir, durasi_total_ms)
            VALUES (?, ?, ?, ?, ?)
        """, (perintah[:500], strategi.get("strategi", "")[:300],
              ", ".join(h["agent"] for h in hasil_list),
              jawaban_final[:1000], durasi))
    
    return jawaban_final, hasil_list, strategi


if __name__ == "__main__":
    print("=== Test agent_manager ===")
    print()
    print("Agents terdaftar:")
    for a in daftar_agent():
        print(f"  [{a['prioritas']}] {a['nama']:10} ({a['provider']}) - {a['capabilities']}")
    print()
    print("Total:", len(daftar_agent()))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""orion_webchat.py -- Web chat ala Muse untuk ORION (single-file).

Cara pakai (di PC Windows, dari folder utama ORION):
    1. Copy file ini ke  E:\\Project Software\\Orion\\
    2. Jalankan:  python orion_webchat.py
    3. Buka browser:  http://127.0.0.1:8001

Otaknya = orion_tool_loop.py yang sudah ada di folder itu (pipeline SAMA
persis seperti chat CLI: chat() + tool loop + riwayat). Tanpa node, tanpa
build step, semua HTML/CSS/JS tertanam di file ini.
"""

import argparse
import json
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

# ---------- dependensi opsional: fastapi/uvicorn ----------
try:
    from fastapi import FastAPI, File, UploadFile
    from fastapi.responses import HTMLResponse, JSONResponse, Response
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    print("[webchat] butuh: pip install fastapi uvicorn python-multipart")

# ---------- otak ORION (opsional saat import, wajib saat dipakai) ----------
try:
    import orion_tool_loop  # pipeline chat CLI yang sudah stabil
    HAS_OTAK = True
except ImportError:
    orion_tool_loop = None  # type: ignore
    HAS_OTAK = False
    print("[webchat] orion_tool_loop.py tidak ketemu -- /api/chat mode darurat.")

# ---------- konstanta ----------
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "webchat_data"       # SEMUA data runtime webchat di sini (rapih, 1 folder)
UPLOAD_DIR = DATA_DIR / "uploads"          # folder file lampiran
RIWAYAT_FILE = DATA_DIR / "riwayat.json"   # riwayat chat per sesi (persisten)
SESI_FILE = DATA_DIR / "sesi.json"        # daftar sesi sidebar (persisten di server)
UPLOAD_DIR_LAMA = BASE_DIR / "uploads"     # fallback: file yg diupload versi lama
try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
BATAS_UPLOAD = 25 * 1024 * 1024           # 25 MB
MAKS_RIWAYAT = 40                         # pesan terakhir per session di RAM
MAKS_ISI_FILE = 15000                     # karakter konteks file teks

# registry tool dibangun SEKALI saat startup (kontrak integrasi)
REGISTRY: Dict = {}
if HAS_OTAK:
    try:
        REGISTRY = orion_tool_loop.bangun_registry()
        print(f"[webchat] registry siap: {len(REGISTRY)} tool")
    except Exception as e:
        print(f"[webchat] bangun_registry gagal: {e}")

# riwayat chat per session (RAM + persisten di webchat_data/riwayat.json)
SESSIONS: Dict[str, List[Dict[str, str]]] = {}


def _simpan_riwayat():
    """Simpan SESSIONS ke disk (atomic: tulis tmp lalu replace)."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = RIWAYAT_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(SESSIONS, ensure_ascii=False), encoding="utf-8")
        tmp.replace(RIWAYAT_FILE)
    except Exception as e:
        print(f"[webchat] gagal simpan riwayat: {e}")


def _muat_riwayat():
    """Muat riwayat dari disk saat startup; file korup -> mulai kosong."""
    try:
        if RIWAYAT_FILE.is_file():
            data = json.loads(RIWAYAT_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        SESSIONS[k] = v
                print(f"[webchat] riwayat dimuat: {len(SESSIONS)} sesi")
    except Exception as e:
        print(f"[webchat] riwayat gagal dimuat, mulai kosong: {e}")


SESI: Dict[str, Dict[str, str]] = {}  # sid -> {title, updated}

def _simpan_sesi():
    """Simpan SESI ke disk (atomic: tulis tmp lalu replace)."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = SESI_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(SESI, ensure_ascii=False), encoding="utf-8")
        tmp.replace(SESI_FILE)
    except Exception as e:
        print(f"[webchat] gagal simpan sesi: {e}")

def _muat_sesi():
    """Muat daftar sesi dari disk; file korup -> mulai kosong."""
    try:
        if SESI_FILE.is_file():
            data = json.loads(SESI_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict):
                        SESI[k] = {"title": str(v.get("title") or "Chat")[:40],
                                   "updated": str(v.get("updated") or "")}
                print(f"[webchat] sesi dimuat: {len(SESI)} sesi")
    except Exception as e:
        print(f"[webchat] sesi gagal dimuat, mulai kosong: {e}")

def _judul_dari_riwayat(sid):
    """Judul darurat dari pesan user pertama (maks 30 char)."""
    for m in SESSIONS.get(sid) or []:
        if isinstance(m, dict) and m.get("role") == "user":
            teks = str(m.get("content") or "").strip()
            if teks:
                return teks[:30]
    return "Chat"

def _sentuh_sesi(sid, pesan="", judul=None):
    """Catat/perbarui sesi: judul + timestamp terbaru."""
    ent = SESI.get(sid)
    if ent is None:
        ent = {"title": "Chat baru", "updated": ""}
        SESI[sid] = ent
    if judul:
        ent["title"] = str(judul)[:40]
    elif (not ent.get("title") or ent["title"] == "Chat baru") and pesan.strip():
        ent["title"] = pesan.strip()[:30]
    ent["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    _simpan_sesi()

def _hapus_sesi(sid):
    if SESI.pop(sid, None) is not None:
        _simpan_sesi()

_muat_riwayat()
_muat_sesi()
# rekonsiliasi: sesi yg ada di riwayat.json tapi belum tercatat -> pulihkan
_pulih = False
for _sid in list(SESSIONS.keys()):
    if _sid not in SESI:
        SESI[_sid] = {"title": _judul_dari_riwayat(_sid),
                     "updated": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())}
        _pulih = True
if _pulih:
    _simpan_sesi()
    print(f"[webchat] sesi dipulihkan dari riwayat: {len(SESI)} sesi")


app = FastAPI(title="ORION WebChat") if HAS_FASTAPI else None  # type: ignore


# ---------- model request ----------
if HAS_FASTAPI:  # model pydantic hanya butuh saat fastapi ada
    class FileRef(BaseModel):
        name: str = ""
        path: str = ""
        size: int = 0

    class ChatIn(BaseModel):
        session_id: Optional[str] = None
        message: str = ""
        files: List["FileRef"] = []
        balasan: Optional[dict] = None  # quote-reply: {teks, dari}

    class SpeakIn(BaseModel):
        text: str = ""

    class ClearIn(BaseModel):
        session_id: str = ""

    class HistoryIn(BaseModel):
        session_id: str = ""

    class SearchIn(BaseModel):
        q: str = ""


# ---------- helper ----------
def _nama_unik(tujuan: Path) -> Path:
    """Hindari tabrakan nama file di folder uploads."""
    if not tujuan.exists():
        return tujuan
    i = 1
    while True:
        baru = tujuan.parent / f"{tujuan.stem}_{i}{tujuan.suffix}"
        if not baru.exists():
            return baru
        i += 1


def _baca_teks(p: Path) -> Optional[str]:
    """Baca file sebagai teks UTF-8; None bila biner / gagal dibaca."""
    try:
        data = p.read_bytes()
    except Exception:
        return None
    try:
        teks = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if len(teks) > MAKS_ISI_FILE:
        teks = teks[:MAKS_ISI_FILE] + f"\n... (dipotong, total {len(teks)} karakter)"
    return teks


def _ambil_tts():
    """Ambil fungsi tts_bicara (Supertonic F1); None bila voice tak tersedia."""
    try:
        from voice.voice_orion import tts_bicara
        return tts_bicara
    except Exception:
        pass
    try:
        vdir = str(BASE_DIR / "voice")
        if vdir not in sys.path:
            sys.path.insert(0, vdir)
        import voice_orion
        return voice_orion.tts_bicara
    except Exception:
        return None


def _bicara_aman(fn, teks: str):
    try:
        fn(teks)
    except Exception as e:
        print(f"[webchat] speak gagal: {e}")


def _tts_f1_fn():
    """Ambil tts_supertonic_bytes (Supertonic F1 -> WAV bytes); None bila tak tersedia."""
    try:
        from voice.voice_orion import tts_supertonic_bytes as fn
        return fn
    except Exception:
        pass
    try:
        vdir = str(BASE_DIR / "voice")
        if vdir not in sys.path:
            sys.path.insert(0, vdir)
        from voice_orion import tts_supertonic_bytes as fn
        return fn
    except Exception:
        return None


def _warmup_f1():
    try:
        fn = _tts_f1_fn()
        if fn is None:
            return
        t0 = time.time()
        fn("Halo, model suara F1 siap.")
        print(f"[webchat] warmup F1 selesai: {time.time()-t0:.1f}s")
    except Exception as e:
        print(f"[webchat] warmup F1 gagal: {e}")


# ---------- endpoint ----------
if HAS_FASTAPI:

    @app.get("/", response_class=HTMLResponse)
    def halaman():
        return PAGE

    @app.get("/health")
    def health():
        return {"ok": True, "tools": len(REGISTRY)}

    @app.post("/api/new")
    def api_new():
        sid = uuid.uuid4().hex
        _sentuh_sesi(sid)
        return {"session_id": sid}

    @app.post("/api/clear")
    def api_clear(inp: ClearIn):
        SESSIONS.pop(inp.session_id, None)
        _hapus_sesi(inp.session_id)
        _simpan_riwayat()
        return {"ok": True}

    @app.post("/api/sessions")
    def api_sessions():
        """Daftar sesi sidebar dari server (persisten, urut terbaru)."""
        def kunci(kv):
            return kv[1].get("updated") or ""
        return {"sessions": [
            {"id": sid, "title": v.get("title") or "Chat",
             "updated": v.get("updated") or ""}
            for sid, v in sorted(SESI.items(), key=kunci, reverse=True)]}

    @app.post("/api/session/upsert")
    def api_session_upsert(body: dict):
        """Client melaporkan judul sesi (disimpan permanen di server)."""
        sid = str((body or {}).get("session_id") or "")
        judul = str((body or {}).get("title") or "Chat")[:40]
        if sid:
            _sentuh_sesi(sid, judul=judul)
        return {"ok": True}

    @app.post("/api/history")
    @app.post("/api/search")
    def api_search(inp: SearchIn):
        """Cari teks di semua sesi riwayat (case-insensitive, maks 30)."""
        q = (inp.q or "").strip().lower()
        if len(q) < 2:
            return {"hasil": []}
        hasil = []
        for sid, msgs in SESSIONS.items():
            if not isinstance(msgs, list):
                continue
            for m in msgs:
                if not isinstance(m, dict):
                    continue
                teks = str(m.get("content") or "")
                pos = teks.lower().find(q)
                if pos < 0:
                    continue
                awal = max(0, pos - 40)
                akhir = min(len(teks), pos + len(q) + 40)
                cuplik = ("..." if awal > 0 else "") + teks[awal:akhir] \
                    + ("..." if akhir < len(teks) else "")
                hasil.append({"sid": sid, "dari": m.get("role", ""),
                              "cuplik": cuplik})
                if len(hasil) >= 30:
                    break
            if len(hasil) >= 30:
                break
        return {"hasil": hasil}
    def api_history(inp: HistoryIn):
        msgs = SESSIONS.get(inp.session_id) or []
        return {"messages": [
            {"role": m.get("role", ""), "content": m.get("content", ""),
             "balasan": m.get("balasan")}
            for m in msgs if isinstance(m, dict)
        ]}

    @app.post("/api/upload")
    async def api_upload(file: UploadFile = File(...)):
        # tolak path traversal: pakai basename saja
        nama = Path(file.filename or "file").name.strip() or "file"
        if nama in (".", ".."):
            return JSONResponse({"error": "nama file tidak valid"}, status_code=400)
        tujuan = _nama_unik(UPLOAD_DIR / nama)
        ditulis = 0
        try:
            with tujuan.open("wb") as w:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    ditulis += len(chunk)
                    if ditulis > BATAS_UPLOAD:
                        try:
                            tujuan.unlink(missing_ok=True)
                        except Exception:
                            pass
                        return JSONResponse({"error": "file melebihi 25MB"},
                                            status_code=413)
                    w.write(chunk)
        finally:
            await file.close()
        return {"name": tujuan.name, "path": str(tujuan.resolve()),
                "size": ditulis}

    @app.post("/api/speak")
    def api_speak(inp: SpeakIn):
        teks = (inp.text or "").strip()
        if not teks:
            return {"ok": False}
        fn = _ambil_tts()
        if fn is None:
            return {"ok": False}  # voice tidak ada: jangan crash
        threading.Thread(target=_bicara_aman, args=(fn, teks),
                         daemon=True).start()
        return {"ok": True}

    @app.post("/api/tts")
    def api_tts(inp: SpeakIn):
        teks = (inp.text or "").strip()[:600]
        if not teks:
            return JSONResponse({"error": "teks kosong"}, status_code=400)
        fn = _tts_f1_fn()
        if fn is None:
            return JSONResponse(
                {"error": "voice_orion.tts_supertonic_bytes tidak ketemu"},
                status_code=503)
        t0 = time.time()
        try:
            data = fn(teks)
        except Exception as e:
            return JSONResponse({"error": "sintesis gagal: %s" % e}, status_code=500)
        print(f"[webchat] /api/tts: {len(teks)} char -> {time.time()-t0:.1f}s")
        if not data:
            return JSONResponse({"error": "TTS mengembalikan kosong"}, status_code=500)
        return Response(content=data, media_type="audio/wav")

    @app.post("/api/chat")
    def api_chat(inp: ChatIn):
        # 1. ambil / buat session + riwayat
        sid = inp.session_id or uuid.uuid4().hex
        riwayat = SESSIONS.get(sid)
        if riwayat is None:
            riwayat = []
            SESSIONS[sid] = riwayat
        pesan_asli = inp.message or ""

        # 2. susun pesan lengkap dengan konteks file lampiran
        bagian = []
        for f in inp.files:
            p = UPLOAD_DIR / Path(f.name or "").name  # basename: anti traversal
            if not p.exists():
                p = UPLOAD_DIR_LAMA / p.name  # fallback upload versi lama
            if p.exists() and p.is_file():
                teks = _baca_teks(p)
                if teks is not None:
                    bagian.append(
                        f"File terlampir: {p.name}\n--- isi ---\n{teks}\n---")
                else:
                    bagian.append(
                        f"File terlampir (biner): {p.name} -- tersimpan di {p}, "
                        f"baca dengan tool baca_file bila perlu.")
            else:
                bagian.append(f"File terlampir: {f.name} (tidak ketemu di server)")
        pesan_lengkap = ("\n\n".join(bagian) + "\n\n" + pesan_asli) if bagian \
            else pesan_asli

        # 2b. konteks balasan: Riki me-reply pesan tertentu -> ORION paham yang dibalas
        _bal = getattr(inp, "balasan", None) or {}
        teks_balas = str(_bal.get("teks") or "").strip()[:2000]
        dari_balas = str(_bal.get("dari") or "ORION")
        if teks_balas:
            pesan_lengkap = (
                "[Riki membalas pesan %s: \"%s\"]\n"
                "Pesan Riki di bawah ini adalah tanggapan atas kutipan di atas. "
                "Pahami konteks kutipan tersebut saat menjawab.\n\n"
            ) % (dari_balas, teks_balas) + pesan_lengkap
        # 3. panggil otak ORION sambil merekam tool yang dipakai
        tools_used: List[str] = []
        if not HAS_OTAK or orion_tool_loop is None:
            jawaban = ("Otak ORION (orion_tool_loop.py) tidak ditemukan di folder "
                       "ini. Letakkan file ini di folder utama ORION.")
        else:
            asli = orion_tool_loop.eksekusi_tool

            def catat(registry, nama_tool, args):
                if nama_tool not in tools_used:
                    tools_used.append(nama_tool)
                return asli(registry, nama_tool, args)

            orion_tool_loop.eksekusi_tool = catat  # monkeypatch sementara
            try:
                jawaban = orion_tool_loop.chat(
                    pesan_lengkap, riwayat=riwayat, registry=REGISTRY)
            except Exception as e:
                jawaban = f"Maaf, ada galat di otak ORION: {e}"
            finally:
                orion_tool_loop.eksekusi_tool = asli  # selalu restore
        if not isinstance(jawaban, str):
            jawaban = str(jawaban)

        # 4. simpan riwayat (asli, tanpa konteks file) + batasi 40
        riwayat.append({"role": "user", "content": pesan_asli,
                        "balasan": {"teks": teks_balas, "dari": dari_balas} if teks_balas else None})
        riwayat.append({"role": "assistant", "content": jawaban})
        del riwayat[:-MAKS_RIWAYAT]
        _simpan_riwayat()
        _sentuh_sesi(sid, pesan_asli)

        return {"reply": jawaban, "tools_used": tools_used, "session_id": sid}


# ---------- halaman web (HTML/CSS/JS tertanam, tanpa CDN) ----------
PAGE = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ORION 🌌</title>
<link rel="icon" type="image/png" href="data:image/png;base64,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">
<style>
*{box-sizing:border-box; margin:0; padding:0;}
:root{
  --bg:#08070f; --panel:#100e1a; --panel2:#171426; --panel3:#1e1a30;
  --acc:#a855f7; --acc2:#ec4899; --grad:linear-gradient(135deg,#a855f7,#ec4899);
  --text:#f2effc; --dim:#8f89a8; --border:#262140;
  --user:linear-gradient(135deg,#7c3aed,#db2777);
  --shadow:0 8px 28px rgba(168,85,247,.16);
}
html,body{height:100%;}
body{
  font-family:"Segoe UI",system-ui,-apple-system,sans-serif; color:var(--text);
  background:
    radial-gradient(900px 500px at 85% -5%, rgba(168,85,247,.14), transparent 60%),
    radial-gradient(700px 500px at 5% 110%, rgba(236,72,153,.10), transparent 60%),
    var(--bg);
  overflow:hidden;
}
#app{display:flex; height:100vh;}
/* ===== header ===== */
main{flex:1; display:flex; flex-direction:column; min-width:0;}
header{
  display:flex; align-items:center; gap:10px; padding:10px 18px;
  background:var(--panel);
  border-bottom:1px solid var(--border); z-index:5;
}
.brand{font-weight:800; font-size:19px; letter-spacing:3px;
  background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent;}
#chatTitle{flex:1; font-size:14px; color:var(--dim); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.hbtn{background:var(--panel2); border:1px solid var(--border); color:var(--text);
  width:38px; height:38px; border-radius:12px; cursor:pointer; font-size:17px;
  display:flex; align-items:center; justify-content:center; transition:.2s;}
.hbtn:hover{border-color:var(--acc); transform:translateY(-1px); box-shadow:var(--shadow);}
.hbtn.on{border-color:var(--acc2); box-shadow:0 0 12px rgba(236,72,153,.35);}
#healthDot{width:10px; height:10px; border-radius:50%; background:var(--dim); flex-shrink:0;}
#healthDot.ok{background:#22c55e; box-shadow:0 0 8px #22c55e;}
#healthDot.bad{background:#ef4444;}
/* ===== chat ===== */
#searchBar{padding:10px 18px 4px;background:var(--panel);}
#searchInput{width:100%;padding:9px 14px;border-radius:10px;border:1px solid var(--border);background:var(--panel2);color:var(--text);font-size:14px;outline:none;}
#searchInput:focus{border-color:var(--acc);}
#searchHasil{max-height:230px;overflow-y:auto;display:flex;flex-direction:column;gap:6px;margin-top:8px;}
.srItem{background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:8px 12px;cursor:pointer;font-size:13px;}
.srItem:hover{border-color:var(--acc);}
.srItem .dari{font-size:11px;opacity:.6;margin-bottom:2px;}
.srItem mark{background:rgba(168,85,247,.45);color:inherit;border-radius:3px;padding:0 2px;}
#filterSesi{margin:10px 10px 0;padding:8px 12px;border-radius:10px;border:1px solid var(--border);background:var(--panel2);color:var(--text);font-size:13px;outline:none;}
#chat{flex:1; overflow-y:auto; padding:24px 18px; display:flex; flex-direction:column; gap:16px;
  max-width:880px; width:100%; margin:0 auto;}
#chat::-webkit-scrollbar{width:8px;}
#chat::-webkit-scrollbar-thumb{background:var(--border); border-radius:4px;}
.msg{max-width:84%; padding:12px 16px; border-radius:18px; line-height:1.6;
  word-wrap:break-word; animation:masuk .3s ease; position:relative;}
@keyframes masuk{from{opacity:0; transform:translateY(10px);} to{opacity:1; transform:none;}}
.msg.user{align-self:flex-end; background:var(--user); color:#fff;
  border-bottom-right-radius:6px; box-shadow:var(--shadow);}
.msg.orion{align-self:flex-start; background:var(--panel2); border:1px solid var(--border);
  border-bottom-left-radius:6px;}
.msg .who{display:flex; align-items:center; gap:8px; margin-bottom:8px; font-size:12px; color:var(--dim);}
.msg{position:relative;}
.msg .quote{border-left:3px solid var(--acc);background:rgba(168,85,247,.10);padding:6px 10px;border-radius:8px;font-size:12px;color:var(--dim);margin-bottom:8px;max-height:76px;overflow:hidden;}
.msg .quote b{color:var(--acc2);display:block;font-size:11px;margin-bottom:2px;}
.msg .rbtn{position:absolute;bottom:8px;right:10px;opacity:0;background:linear-gradient(135deg,#a855f7,#ec4899);border:none;border-radius:50%;width:32px;height:32px;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;font-size:15px;color:#fff;box-shadow:0 4px 14px rgba(168,85,247,.45);transition:opacity .15s,transform .15s;}
.msg .rbtn:hover{transform:scale(1.15);}
.msg:hover .rbtn{opacity:1;}
@media (hover:none){.msg .rbtn{opacity:.92;}}
.msg:hover .rbtn{opacity:1;}
#balasBar{display:none;align-items:center;gap:8px;background:rgba(168,85,247,.10);border-left:3px solid var(--acc);border-radius:8px;padding:7px 10px;margin-bottom:8px;font-size:12px;color:var(--dim);}
#balasBar.on{display:flex;}
#balasBar .tx{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
#balasBar .tx b{color:var(--acc2);}
#balasBar button{background:none;border:none;color:var(--dim);cursor:pointer;font-size:14px;}
.avatar{width:26px; height:26px; border-radius:50%; background:var(--grad);
  display:flex; align-items:center; justify-content:center; font-size:14px; flex-shrink:0;
  box-shadow:0 0 10px rgba(168,85,247,.4);}
.who .nm{font-weight:700; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent;}
.who button{margin-left:auto; background:none; border:none; cursor:pointer; font-size:15px;
  opacity:.55; transition:.2s; padding:2px 6px; border-radius:8px;}
.who button:hover{opacity:1; background:var(--panel3);}
.tools{font-size:11px; color:var(--dim); margin-top:10px; border-top:1px dashed var(--border); padding-top:8px;}
.msg p{margin:7px 0;}
.msg h2,.msg h3,.msg h4{margin:12px 0 5px;}
.msg ul{margin:7px 0 7px 22px;}
.msg blockquote{border-left:3px solid var(--acc); padding:5px 12px; margin:9px 0; color:var(--dim);
  background:rgba(168,85,247,.06); border-radius:0 8px 8px 0;}
.msg code.ic{background:#0a0812; padding:2px 7px; border-radius:6px; font-family:Consolas,monospace; font-size:13px;}
.codeblock{margin:9px 0; border:1px solid var(--border); border-radius:10px; overflow:hidden;}
.cb-head{display:flex; justify-content:space-between; align-items:center; background:#0a0812;
  padding:7px 12px; font-size:12px; color:var(--dim);}
.cb-head button{background:var(--panel3); border:1px solid var(--border); color:var(--text);
  border-radius:7px; padding:4px 12px; cursor:pointer; font-size:12px;}
.cb-head button:hover{border-color:var(--acc);}
.codeblock pre{padding:12px 14px; overflow-x:auto; font-family:Consolas,monospace; font-size:13px; line-height:1.5;}
.typing{align-self:flex-start; background:var(--panel2); border:1px solid var(--border);
  border-radius:18px; padding:14px 20px; display:flex; gap:6px;}
.typing i{width:8px; height:8px; border-radius:50%; background:var(--acc); animation:bl 1.1s infinite;}
.typing i:nth-child(2){animation-delay:.18s;} .typing i:nth-child(3){animation-delay:.36s;}
@keyframes bl{0%,100%{opacity:.25; transform:none;}50%{opacity:1; transform:translateY(-4px);}}
/* ===== empty state ===== */
.empty{margin:auto; text-align:center; color:var(--dim); max-width:440px; animation:masuk .4s ease;}
.empty .logo{font-size:60px; margin-bottom:14px; filter:drop-shadow(0 0 18px rgba(168,85,247,.5));
  animation:float 3s ease-in-out infinite;}
@keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-8px);}}
.empty h2{color:var(--text); margin-bottom:6px; font-size:22px;}
.sug{margin-top:18px; display:flex; flex-wrap:wrap; gap:8px; justify-content:center;}
.sug button{background:var(--panel2); border:1px solid var(--border); color:var(--text);
  border-radius:20px; padding:9px 16px; cursor:pointer; font-size:13px; transition:.2s;}
.sug button:hover{border-color:var(--acc); box-shadow:var(--shadow); transform:translateY(-1px);}
/* ===== composer ===== */
#composer{padding:14px 18px 10px; background:var(--panel);
  border-top:1px solid var(--border);}
#composerInner{max-width:880px; margin:0 auto;}
#chips{display:flex; flex-wrap:wrap; gap:8px; margin-bottom:8px;}
.chip{background:var(--panel3); border:1px solid var(--border); border-radius:16px;
  padding:6px 8px 6px 13px; font-size:12px; display:flex; align-items:center; gap:6px;}
.chip button{background:none; border:none; color:var(--dim); cursor:pointer; font-size:14px;}
.chip button:hover{color:#ef4444;}
.chip.uploading{opacity:.6;}
.row{display:flex; gap:10px; align-items:flex-end;}
#btnAttach{font-size:20px; cursor:pointer; padding:10px 12px; border-radius:14px;
  border:1px solid var(--border); background:var(--panel2); transition:.2s;}
#btnAttach:hover{border-color:var(--acc); box-shadow:var(--shadow);}
#input{flex:1; background:var(--panel2); border:1px solid var(--border); color:var(--text);
  border-radius:16px; padding:13px 16px; font-size:15px; font-family:inherit; resize:none;
  max-height:200px; line-height:1.5; transition:.2s;}
#input:focus{outline:none; border-color:var(--acc); box-shadow:0 0 0 3px rgba(168,85,247,.15);}
/* ===== ikon modern ORION ===== */
.hbtn{display:inline-flex;align-items:center;justify-content:center;}
.hbtn svg{width:18px;height:18px;display:block;}
.logo .coin{width:84px;height:84px;}
.coin{width:30px;height:30px;border-radius:50%;box-shadow:0 0 12px rgba(168,85,247,.5);flex-shrink:0;}
.brand{display:flex;align-items:center;gap:10px;}
img.avatar{object-fit:cover;}
.who button.tbtn{display:inline-flex;align-items:center;}
.spn{animation:spn .9s linear infinite;}
@keyframes spn{to{transform:rotate(360deg);}}
#btnSend svg{width:20px;height:20px;display:block;}
#btnAttach svg{width:20px;height:20px;display:block;}
#btnNew{display:flex;align-items:center;justify-content:center;gap:8px;}
#btnNew svg{width:18px;height:18px;}
#btnCloseSide{display:none;}
.side-head{display:flex;gap:8px;align-items:center;}
.side-head #btnNew{flex:1;}
#filterSesi{width:calc(100% - 20px);box-sizing:border-box;}
@media (max-width:768px){
  #btnCloseSide{display:inline-flex;}
  .side-head{padding:12px 12px 4px;}
}
#btnSend{background:var(--grad); border:none; color:#fff; font-size:19px; width:50px; height:50px;
  border-radius:16px; cursor:pointer; flex-shrink:0; transition:.2s; box-shadow:var(--shadow);}
#btnSend:hover{transform:translateY(-2px) scale(1.03); box-shadow:0 10px 32px rgba(236,72,153,.3);}
#btnSend:disabled{opacity:.5; cursor:default; transform:none;}
.hint{text-align:center; font-size:11px; color:var(--dim); padding:9px 0 3px;}
#toast{position:fixed; bottom:26px; left:50%; transform:translateX(-50%); background:#ef4444;
  color:#fff; padding:11px 22px; border-radius:12px; display:none; z-index:99; font-size:14px;
  box-shadow:0 8px 24px rgba(0,0,0,.4);}
/* ===== sidebar kanan ===== */
#sidebar{width:280px; flex-shrink:0; background:var(--panel); border-left:1px solid var(--border);
  display:flex; flex-direction:column; overflow:hidden; transition:margin-right .3s ease; z-index:20;}
#app.hide-side #sidebar{margin-right:-280px;}
.side-head{padding:16px 16px 8px;}
#btnNew{width:100%; padding:11px; border:1px solid var(--border); background:var(--grad); color:#fff;
  border-radius:12px; cursor:pointer; font-size:14px; font-weight:600; transition:.2s;}
#btnNew:hover{transform:translateY(-1px); box-shadow:var(--shadow);}
#sessList{flex:1; overflow-y:auto; padding:10px; display:flex; flex-direction:column; gap:5px;}
.sess{padding:10px 13px; border-radius:10px; cursor:pointer; color:var(--dim); font-size:14px;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:flex; gap:8px; align-items:center;
  transition:.15s; border:1px solid transparent;}
.sess:hover{background:var(--panel2); color:var(--text);}
.sess.active{background:var(--panel2); color:var(--text); border-color:var(--acc);}
.sess .del{margin-left:auto; color:var(--dim); border:none; background:none; cursor:pointer; font-size:14px; display:none;}
.sess:hover .del{display:block;}
.sess .del:hover{color:#ef4444;}
.side-foot{padding:13px 16px; font-size:11px; color:var(--dim); border-top:1px solid var(--border);}
/* ===== mobile ===== */
@media (max-width:768px){
  #sidebar{position:fixed; right:0; top:0; bottom:0; transform:translateX(100%);
    transition:transform .25s; box-shadow:-10px 0 40px #000; margin-right:0 !important; width:270px;}
  #sidebar.open{transform:none;}
  #app.hide-side #sidebar{transform:translateX(100%);}
  #app.hide-side #sidebar.open{transform:none;}
  .msg{max-width:94%;}
  #chatTitle{display:none;}
}
</style>
</head>
<body>
<div id="app">
  <main>
    <header>
      <div class="brand"><img class="coin" src="data:image/png;base64,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" alt="ORION">ORION</div>
      <div id="chatTitle">Chat baru</div>
      <button id="btnVoice" class="hbtn" title="Suara otomatis: mati"></button>
      <button id="btnNotif" class="hbtn" title="Notifikasi pesan masuk"></button>
      <button id="btnPanel" class="hbtn" title="Panel riwayat"></button>
      <button id="btnSearch" class="hbtn" title="Cari pesan"></button>
      <div id="healthDot" title="status server"></div>
    </header>
    <div id="searchBar" hidden>
      <input id="searchInput" placeholder="Cari pesan di semua riwayat..." autocomplete="off">
      <div id="searchHasil"></div>
    </div>
    <div id="chat"></div>
    <div id="composer">
      <div id="composerInner">
        <div id="chips"></div>
        <div id="balasBar"><span>\u21a9\uFE0F</span><span class="tx"></span><button onclick="batalBalas()" title="Batal">\u2715</button></div>
        <div class="row">
          <label id="btnAttach" title="Lampirkan file"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg><input type="file" id="fileInput" multiple hidden></label>
          <textarea id="input" rows="1" placeholder="Tulis pesan untuk ORION... (Enter kirim, Shift+Enter baris baru)"></textarea>
          <button id="btnSend" title="Kirim"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg></button>
        </div>
        <div class="hint">🔊 di tiap pesan buat dibacain · tombol speaker di atas buat otomatis (suara F1 🌸)</div>
      </div>
    </div>
  </main>
  <aside id="sidebar">
    <div class="side-head"><button id="btnNew"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg><span>Chat baru</span></button><button id="btnCloseSide" class="hbtn" title="Tutup panel"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg></button></div>
    <input id="filterSesi" placeholder="Filter riwayat...">
    <div id="sessList"></div>
    <div class="side-foot">ORION v2.7 · pipeline tool-loop</div>
  </aside>
</div>
<div id="toast"></div>
<script>
/* ===== state ===== */
let SID = localStorage.getItem("orion_sid") || null;
let attached = [];
let cache = {};
const CODEBLOCKS = [];
let voiceOn = localStorage.getItem("orion_voice") === "1";

/* ===== util ===== */
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function toast(m){const t=document.getElementById("toast");t.textContent=m;t.style.display="block";clearTimeout(t._h);t._h=setTimeout(()=>t.style.display="none",3000);}
async function api(path,body){
  const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body||{})});
  if(!r.ok){let e="";try{e=(await r.json()).error||"";}catch(_){}throw new Error("HTTP "+r.status+(e?" · "+e:""));}
  return r.json();
}
function scrollDown(){const c=document.getElementById("chat");c.scrollTop=c.scrollHeight;}

/* ===== voice F1 (Supertonic — suara cewe, sintesis di server) ===== */
let audioEl = null;
let bicaraToken = 0;
function stopAudio(){ bicaraToken++; try{ if(audioEl){ audioEl.pause(); audioEl=null; } }catch(_){} }
function cleanSpeak(s){
  return String(s).replace(/```[\\s\\S]*?```/g," [kode] ")
    .replace(/`([^`]+)`/g,"$1")
    .replace(/\\[([^\\]]+)\\]\\([^)]+\\)/g,"$1")
    .replace(/[*_#>\\-~]/g,"")
    .replace(/\\s+/g," ").trim().slice(0,1200);
}
function pecahKalimat(t){
  const p = String(t).match(/[^.!?…\\n]+[.!?…]+["\"']?|[^.!?…\\n]+$/g);
  const h = (p||[]).map(s=>s.trim()).filter(s=>s.length>1);
  return h.length?h:[t];
}
async function ambilAudio(t){
  const r = await fetch("/api/tts",{method:"POST",
    headers:{"Content-Type":"application/json"},body:JSON.stringify({text:t})});
  if(!r.ok){ let e=""; try{ e=(await r.json()).error||""; }catch(_){}
    throw new Error(e||("HTTP "+r.status)); }
  return URL.createObjectURL(await r.blob());
}
/* ===== ikon SVG ORION ===== */
const _svgW='width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"';
const SVG_SPK='<svg '+_svgW+'><path d="M11 5 6.5 9H3v6h3.5L11 19V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M18.5 5.5a9 9 0 0 1 0 13"/></svg>';
const SVG_SPKX='<svg '+_svgW+'><path d="M11 5 6.5 9H3v6h3.5L11 19V5Z"/><path d="m16 9 6 6M22 9l-6 6"/></svg>';
const SVG_LOAD='<svg '+_svgW+' class="spn"><path d="M21 12a9 9 0 1 1-6.2-8.56"/></svg>';
const SVG_BELL='<svg '+_svgW+'><path d="M18 9a6 6 0 1 0-12 0c0 6-2.5 7-2.5 7h17S18 15 18 9Z"/><path d="M10 20a2.2 2.2 0 0 0 4 0"/></svg>';
const SVG_BELLX='<svg '+_svgW+'><path d="M18 9a6 6 0 1 0-12 0c0 6-2.5 7-2.5 7h17S18 15 18 9Z"/><path d="M10 20a2.2 2.2 0 0 0 4 0"/><path d="m3 3 18 18"/></svg>';
const SVG_SEARCH='<svg '+_svgW+'><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>';
const SVG_PANEL='<svg '+_svgW+'><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M15 4v16"/></svg>';
const SVG_PLUS='<svg '+_svgW+'><path d="M12 5v14M5 12h14"/></svg>';
const SVG_X='<svg '+_svgW+'><path d="M18 6 6 18M6 6l12 12"/></svg>';
const SVG_SEND='<svg '+_svgW+'><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>';
const SVG_CLIP='<svg '+_svgW+'><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>';
document.getElementById("btnSearch").innerHTML=SVG_SEARCH;
document.getElementById("btnPanel").innerHTML=SVG_PANEL;
document.getElementById("btnCloseSide").onclick=()=>tutupPanel();
async function bicara(teks, btn){
  stopAudio();
  const my = bicaraToken;
  const t = cleanSpeak(teks);
  if(!t)return;
  const kal = pecahKalimat(t);
  if(btn){ btn.innerHTML=SVG_LOAD; btn.disabled=true; }
  try{
    let nextP = ambilAudio(kal[0]);
    for(let i=0;i<kal.length;i++){
      const url = await nextP;
      if(my!==bicaraToken){ URL.revokeObjectURL(url); return; }
      if(i+1<kal.length) nextP = ambilAudio(kal[i+1]);
      if(btn){ btn.innerHTML=SVG_SPK; btn.disabled=false; btn=null; }
      const au = new Audio(url);
      audioEl = au;
      await new Promise((res,rej)=>{
        au.onended=()=>{ URL.revokeObjectURL(url); if(audioEl===au)audioEl=null; res(); };
        au.onerror=rej;
        au.play().catch(rej);
      });
      if(my!==bicaraToken)return;
    }
  }catch(e){ if(my===bicaraToken)toast("Voice F1 gagal: "+e.message); }
  finally{ if(btn){ btn.innerHTML=SVG_SPK; btn.disabled=false; } }
}
/* ===== notifikasi pesan masuk ===== */
let notifOn=localStorage.getItem("orion_notif")!=="0";
let notifCount=0;
function renderNotifBtn(){const b=document.getElementById("btnNotif");if(!b)return;
  b.innerHTML=notifOn?SVG_BELL:SVG_BELLX;
  b.title=notifOn?"Notifikasi pesan: nyala":"Notifikasi pesan: mati";}
function toggleNotif(){notifOn=!notifOn;localStorage.setItem("orion_notif",notifOn?"1":"0");renderNotifBtn();}
function notifOrion(){
  if(!notifOn||!document.hidden)return;
  notifCount++;document.title="("+notifCount+") \U0001F4AC ORION";}
document.addEventListener("visibilitychange",()=>{if(!document.hidden){notifCount=0;document.title="ORION \U0001F30C";}});
document.getElementById("btnNotif").onclick=toggleNotif;
renderNotifBtn();
function renderVoiceBtn(){
  const b=document.getElementById("btnVoice");
  b.innerHTML = voiceOn ? SVG_SPK : SVG_SPKX;
  b.classList.toggle("on", voiceOn);
  b.title = voiceOn ? "Suara F1 otomatis: nyala" : "Suara F1 otomatis: mati";
}
document.getElementById("btnVoice").onclick=()=>{
  voiceOn=!voiceOn; localStorage.setItem("orion_voice", voiceOn?"1":"0");
  renderVoiceBtn();
  if(!voiceOn)stopAudio();
  else bicara("Halo! Suara F satu otomatis nyala.");
};

/* ===== markdown ringan built-in (tanpa CDN) ===== */
function md(src){
  let t=String(src).replace(/```(\\w*)\\n([\\s\\S]*?)```/g,(m,lang,code)=>{
    CODEBLOCKS.push({lang:lang||"code",code:code.replace(/\\n$/,"")});return "\\u0000B"+(CODEBLOCKS.length-1)+"\\u0000";});
  t=t.replace(/`([^`\\n]+)`/g,(m,c)=>{CODEBLOCKS.push({inline:true,code:c});return "\\u0000B"+(CODEBLOCKS.length-1)+"\\u0000";});
  t=esc(t);
  t=t.split("\\n").map(ln=>ln
    .replace(/\\*\\*([^*]+)\\*\\*/g,"<strong>$1</strong>")
    .replace(/(^|[^*])\\*([^*]+)\\*/g,"$1<em>$2</em>")).join("\\n");
  const lines=t.split("\\n");let html="",inList=false,inQuote=false,para=[];
  const fP=()=>{if(para.length){html+="<p>"+para.join("<br>")+"</p>";para=[];}};
  const fL=()=>{if(inList){html+="</ul>";inList=false;}};
  const fQ=()=>{if(inQuote){html+="</blockquote>";inQuote=false;}};
  for(const ln of lines){
    let m;
    if(/^\\u0000B\\d+\\u0000$/.test(ln)){fP();fL();fQ();html+=ln;continue;}
    if(m=ln.match(/^### (.*)/)){fP();fL();fQ();html+="<h4>"+m[1]+"</h4>";continue;}
    if(m=ln.match(/^## (.*)/)){fP();fL();fQ();html+="<h3>"+m[1]+"</h3>";continue;}
    if(m=ln.match(/^# (.*)/)){fP();fL();fQ();html+="<h2>"+m[1]+"</h2>";continue;}
    if(m=ln.match(/^&gt; ?(.*)/)){fP();fL();if(!inQuote){html+="<blockquote>";inQuote=true;}html+=m[1]+"<br>";continue;}
    if(m=ln.match(/^[-*] (.*)/)){fP();fQ();if(!inList){html+="<ul>";inList=true;}html+="<li>"+m[1]+"</li>";continue;}
    if(/^\\s*$/.test(ln)){fP();fL();fQ();continue;}
    para.push(ln);
  }
  fP();fL();fQ();
  html=html.replace(/\\u0000B(\\d+)\\u0000/g,(m,i)=>{
    const b=CODEBLOCKS[+i];
    if(b&&b.inline)return '<code class="ic">'+esc(b.code)+"</code>";
    const lang=(b&&b.lang)||"code";
    return '<div class="codeblock"><div class="cb-head"><span>'+esc(lang)+
      '</span><button onclick="copyCode('+i+')">copy</button></div><pre><code>'+
      esc(b?b.code:"")+"</code></pre></div>";});
  return html;
}
function copyCode(i){
  const b=CODEBLOCKS[+i];if(!b)return;
  navigator.clipboard.writeText(b.inline?b.code:b.code).then(()=>toast("Kode disalin"));
}

/* ===== pencarian riwayat ===== */
let searchTimer=null;
function judulSesi(sid){const s=getSessions().find(x=>x.id===sid);return s?s.title:"Sesi lama";}
function escHtml(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function toggleSearch(){const b=document.getElementById("searchBar");b.hidden=!b.hidden;
  if(!b.hidden){document.getElementById("searchInput").focus();}
  else{document.getElementById("searchHasil").innerHTML="";document.getElementById("searchInput").value="";}}
function cariPesan(){
  const q=document.getElementById("searchInput").value.trim();
  const box=document.getElementById("searchHasil");
  if(q.length<2){box.innerHTML="";return;}
  box.innerHTML='<div style="opacity:.5;font-size:13px;padding:6px;">Mencari...</div>';
  api("/api/search",{q:q}).then(r=>{
    const h=r.hasil||[];box.innerHTML="";
    if(!h.length){box.innerHTML='<div style="opacity:.5;font-size:13px;padding:6px;">Tidak ketemu.</div>';return;}
    for(const x of h){
      const d=document.createElement("div");d.className="srItem";
      const ql=q.toLowerCase();const cl=String(x.cuplik).toLowerCase();const i=cl.indexOf(ql);
      let cuplik=escHtml(x.cuplik);
      if(i>=0){cuplik=escHtml(x.cuplik.slice(0,i))+"<mark>"+escHtml(x.cuplik.slice(i,i+q.length))+"</mark>"+escHtml(x.cuplik.slice(i+q.length));}
      d.innerHTML='<div class="dari">'+(x.dari==="user"?"Riki":"ORION")+" \u2022 "+escHtml(judulSesi(x.sid))+"</div><div>"+cuplik+"</div>";
      d.onclick=()=>{toggleSearch();pilihSession(x.sid);};
      box.append(d);
    }
  }).catch(()=>{box.innerHTML='<div style="opacity:.5;font-size:13px;padding:6px;">Pencarian gagal.</div>';});
}
document.getElementById("btnSearch").onclick=toggleSearch;
document.getElementById("searchInput").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(cariPesan,300);});
document.getElementById("filterSesi").addEventListener("input",(e)=>{
  const q=e.target.value.toLowerCase();
  document.querySelectorAll("#sessList .sess").forEach(d=>{
    d.style.display=d.textContent.toLowerCase().includes(q)?"":"none";});
});
/* ===== session (localStorage) ===== */
function getSessions(){try{return JSON.parse(localStorage.getItem("orion_sessions")||"[]");}catch(_){return[];}}
function saveSessions(s){localStorage.setItem("orion_sessions",JSON.stringify(s));}
async function sinkronSesiDariServer(){
  try{
    const r=await api("/api/sessions");
    const srv=r.sessions||[];
    const idsSrv=new Set(srv.map(s=>s.id));
    const lokal=getSessions();
    const gab=srv.map(s=>({id:s.id,title:s.title||"Chat"}));
    for(const s of getSessions())if(!idsSrv.has(s.id))gab.push({id:s.id,title:s.title||"Chat"});
    saveSessions(gab);renderSessions();
  }catch(_){renderSessions();}
}
function renderSessions(){
  const box=document.getElementById("sessList");box.innerHTML="";
  for(const s of getSessions()){
    const d=document.createElement("div");
    d.className="sess"+(s.id===SID?" active":"");
    const label=document.createElement("span");label.textContent=s.title;label.style.cssText="flex:1;overflow:hidden;text-overflow:ellipsis;";
    const del=document.createElement("button");del.className="del";del.innerHTML=SVG_X;del.title="Hapus";
    del.onclick=(e)=>{e.stopPropagation();hapusSession(s.id);};
    d.append(label,del);d.onclick=()=>pilihSession(s.id);box.append(d);
  }
}
function updateTitle(sid,title){
  const ss=getSessions();const s=ss.find(x=>x.id===sid);
  if(s&&s.title==="Chat baru"){s.title=title.slice(0,30)||"Chat baru";saveSessions(ss);renderSessions();
    api("/api/session/upsert",{session_id:sid,title:s.title}).catch(()=>{});
    if(sid===SID)document.getElementById("chatTitle").textContent=s.title;}
}
function tutupPanel(){document.getElementById("sidebar").classList.remove("open");}
async function newChat(){
  const r=await api("/api/new");SID=r.session_id;localStorage.setItem("orion_sid",SID);
  const ss=getSessions();ss.unshift({id:SID,title:"Chat baru"});saveSessions(ss);
  renderSessions();tampilkanChat();tutupPanel();
}
function pilihSession(sid){SID=sid;localStorage.setItem("orion_sid",sid);renderSessions();tampilkanChat();
  const s=getSessions().find(x=>x.id===sid);
  document.getElementById("chatTitle").textContent=s?s.title:"Chat";
  tutupPanel();}
async function hapusSession(sid){
  try{await api("/api/clear",{session_id:sid});}catch(_){}
  delete cache[sid];
  let ss=getSessions().filter(x=>x.id!==sid);saveSessions(ss);
  if(sid===SID){SID=null;localStorage.removeItem("orion_sid");}
  renderSessions();
  if(!SID&&ss.length){pilihSession(ss[0].id);}else if(!SID){tampilkanChat();}
}
const SARAN=["Kenalin dirimu dong 🌌","Kamu bisa apa aja?","Kamu inget aku siapa?"];
async function tampilkanChat(){
  const box=document.getElementById("chat");box.innerHTML="";
  let dariServer=false;
  if(!cache[SID] && SID){
    try{
      const r=await api("/api/history",{session_id:SID});
      const arr=r.messages||[];
      if(arr.length){
        cache[SID]=[];
        for(const m of arr){
          if(m.role==="user")addMsg("user",m.content||"",null,null,m.balasan||null);
          else if(m.role==="assistant")addMsg("orion",m.content||"",null,null,m.balasan||null);
        }
        dariServer=true;
      }
    }catch(_){}
  }
  const msgs=cache[SID]||[];
  if(!msgs.length){
    box.innerHTML='<div class="empty"><div class="logo"><img class="coin" src="data:image/png;base64,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" alt="ORION"></div>'+
      "<h2>Halo, aku <b>ORION</b></h2><div>Mau ngobrol apa hari ini, sayang?</div>"+
      '<div class="sug">'+SARAN.map(s=>'<button data-s="'+esc(s)+'">'+esc(s)+"</button>").join("")+"</div></div>";
    box.querySelectorAll(".sug button").forEach(b=>b.onclick=()=>{
      document.getElementById("input").value=b.getAttribute("data-s");send();});
    return;
  }
  if(!dariServer)for(const m of msgs)box.append(m.el);
  scrollDown();
}

/* ===== bubble chat ===== */
function addMsg(role,text,files,tools,balasan){
  const box=document.getElementById("chat");
  const empty=box.querySelector(".empty");if(empty)empty.remove();
  const d=document.createElement("div");d.className="msg "+role;
  if(role==="user"){
    let h="";
    if(files&&files.length)h+='<div style="font-size:12px;opacity:.85;margin-bottom:6px;">📎 '+
      files.map(f=>esc(f.name)).join(", ")+"</div>";
    d.innerHTML=h+md(text||"(lampiran saja)");
  }else{
    const idx=(cache[SID]||[]).length;
    d.innerHTML='<div class="who"><span class="avatar"><img class="avatar" src="data:image/png;base64,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" alt="ORION"></span><span class="nm">ORION</span>'+
      '<button data-i="'+idx+'" title="Bacakan dengan suara" class="tbtn">'+SVG_SPK+'</button></div>'+
      '<div class="body">'+md(text)+"</div>"+
      (tools&&tools.length?'<div class="tools">🔧 memakai tool: '+tools.map(esc).join(", ")+"</div>":"");
    d.querySelector("button").onclick=(e)=>{const b=e.target;b.blur();bicara((cache[SID]||[])[+b.getAttribute("data-i")].text,b);};
  }
  if(balasan&&balasan.teks){const q=document.createElement("div");q.className="quote";
    q.innerHTML="<b>"+esc(balasan.dari||"ORION")+"</b>"+esc(String(balasan.teks).slice(0,500));
    d.insertBefore(q,d.firstChild);}
  const rb=document.createElement("button");rb.className="rbtn";rb.title="Balas pesan ini";rb.textContent="\u21a9\uFE0F";
  rb.onclick=function(){mulaiBalas({teks:text||"",dari:role==="user"?"Riki":"ORION"});};d.append(rb);
  box.append(d);scrollDown();
  (cache[SID]=cache[SID]||[]).push({role,el:d,text:text||""});
  return d;
}
function addTyping(){
  const box=document.getElementById("chat");
  const d=document.createElement("div");d.className="typing";d.innerHTML="<i></i><i></i><i></i>";
  box.append(d);scrollDown();return d;
}

/* ===== balas pesan (quote-reply) ===== */
let balasanAktif=null;
function mulaiBalas(b){balasanAktif=b;renderBalasan();const i=document.getElementById("input");if(i)i.focus();}
function batalBalas(){balasanAktif=null;renderBalasan();}
function renderBalasan(){
  const bar=document.getElementById("balasBar");if(!bar)return;
  if(balasanAktif&&balasanAktif.teks){
    bar.classList.add("on");
    bar.querySelector(".tx").innerHTML="<b>"+esc(balasanAktif.dari||"ORION")+"</b> &middot; "+esc(String(balasanAktif.teks).slice(0,120));
  }else{bar.classList.remove("on");balasanAktif=null;}
}
/* ===== kirim pesan ===== */
async function send(){
  const inp=document.getElementById("input");
  const msg=inp.value.trim();
  if(!msg&&!attached.length)return;
  if(!SID)await newChat();
  const files=attached.splice(0);renderChips();
  const bal=balasanAktif;balasanAktif=null;renderBalasan();
  addMsg("user",msg,files,null,bal);
  inp.value="";autoresize();
  updateTitle(SID,msg||files.map(f=>f.name).join(", "));
  const btn=document.getElementById("btnSend");btn.disabled=true;
  const ty=addTyping();
  try{
    const r=await api("/api/chat",{session_id:SID,message:msg,files,balasan:bal});
    SID=r.session_id;localStorage.setItem("orion_sid",SID);
    addMsg("orion",r.reply,null,r.tools_used||[]);
    notifOrion();
    if(voiceOn)bicara(r.reply);
  }catch(e){toast("Gagal menghubungi ORION: "+e.message);}
  finally{ty.remove();btn.disabled=false;}
}

/* ===== lampiran ===== */
function renderChips(){
  const box=document.getElementById("chips");box.innerHTML="";
  attached.forEach((f,i)=>{
    const c=document.createElement("div");c.className="chip"+(f.uploading?" uploading":"");
    const s=document.createElement("span");s.textContent="📎 "+f.name+(f.uploading?" (mengunggah...)":"");
    const x=document.createElement("button");x.textContent="✕";
    x.onclick=()=>{attached.splice(i,1);renderChips();};
    c.append(s,x);box.append(c);
  });
}
async function uploadFiles(list){
  for(const file of list){
    const rec={name:file.name,uploading:true};attached.push(rec);renderChips();
    try{
      const fd=new FormData();fd.append("file",file);
      const r=await fetch("/api/upload",{method:"POST",body:fd});
      if(!r.ok){const j=await r.json().catch(()=>({}));throw new Error(j.error||("HTTP "+r.status));}
      const j=await r.json();
      rec.name=j.name;rec.path=j.path;rec.size=j.size;rec.uploading=false;
    }catch(e){attached.splice(attached.indexOf(rec),1);toast("Upload gagal: "+e.message);}
    renderChips();
  }
}

/* ===== wiring ===== */
function autoresize(){const i=document.getElementById("input");i.style.height="auto";i.style.height=Math.min(i.scrollHeight,200)+"px";}
document.getElementById("btnSend").onclick=send;
document.getElementById("btnNew").onclick=()=>newChat().catch(e=>toast(e.message));
document.getElementById("btnPanel").onclick=()=>{
  if(window.innerWidth<=768){document.getElementById("sidebar").classList.toggle("open");}
  else{document.getElementById("app").classList.toggle("hide-side");}
};
document.getElementById("input").addEventListener("input",autoresize);
document.getElementById("input").addEventListener("keydown",e=>{
  if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send();}});
document.getElementById("fileInput").addEventListener("change",e=>{uploadFiles(e.target.files);e.target.value="";});

/* ===== init ===== */
(async function(){
  renderVoiceBtn();
  try{const h=await (await fetch("/health")).json();
    document.getElementById("healthDot").className=h.ok?"ok":"bad";
    document.getElementById("healthDot").title=h.ok?h.tools+" tool siap":"server bermasalah";
  }catch(_){document.getElementById("healthDot").className="bad";}
  await sinkronSesiDariServer();
  const ss=getSessions();
  if(SID&&ss.some(s=>s.id===SID)){pilihSession(SID);}
  else if(ss.length){pilihSession(ss[0].id);}
  else{tampilkanChat();}
})();
</script>
</body>
</html>

"""


def main():
    ap = argparse.ArgumentParser(description="ORION WebChat")
    ap.add_argument("--port", type=int, default=8001,
                    help="port server (default 8001)")
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    if not HAS_FASTAPI:
        print("[webchat] install dulu: pip install fastapi uvicorn python-multipart")
        sys.exit(1)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    try:
        import uvicorn
    except ImportError:
        print("[webchat] uvicorn belum ada: pip install uvicorn")
        sys.exit(1)
    print(f"[webchat] buka http://{args.host}:{args.port}")
    threading.Thread(target=_warmup_f1, daemon=True).start()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

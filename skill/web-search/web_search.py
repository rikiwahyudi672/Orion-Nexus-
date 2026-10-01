"""Web Search - Orion cari di internet."""
import urllib.request, urllib.parse, json, re
from datetime import datetime


# ============ KAMUS SINGKATAN ============
SINGKATAN = {
    "ai": "kecerdasan buatan",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "llm": "large language model",
    "iot": "internet of things",
    "ui": "user interface",
    "ux": "user experience",
    "api": "application programming interface",
    "db": "database",
}


def expand_query(query):
    """Expand singkatan."""
    words = query.lower().split()
    expanded = []
    for w in words:
        if w in SINGKATAN:
            expanded.append(SINGKATAN[w])
        else:
            expanded.append(w)
    return " ".join(expanded)


def search_wikipedia(query, limit=5):
    """Search Wikipedia - dengan pre-processing."""
    try:
        # Expand singkatan
        query_expanded = expand_query(query)
        print(f"[web] Query asli: {query}")
        print(f"[web] Query expand: {query_expanded}")
        
        url = "https://id.wikipedia.org/w/api.php"
        params = {
            "action": "query", "list": "search",
            "srsearch": query_expanded, "format": "json", "srlimit": limit,
        }
        req = urllib.request.Request(
            f"{url}?{urllib.parse.urlencode(params)}",
            headers={"User-Agent": "Orion/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        
        results = []
        for item in data.get("query", {}).get("search", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": re.sub(r'<[^>]+>', '', item.get("snippet", "")),
                "url": f"https://id.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', ''))}",
                "sumber": "wikipedia",
            })
        return results
    except Exception as e:
        print(f"[web] Wikipedia error: {e}")
        return []


def baca_url(url, max_chars=3000):
    """Baca halaman web."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="ignore")
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_chars]
    except Exception as e:
        return f"Error: {e}"


def ringkas_artikel(url, max_kalimat=5):
    """Ringkas artikel dari URL."""
    text = baca_url(url, max_chars=5000)
    
    # Split kalimat
    kalimat = re.split(r'(?<=[.!?])\s+', text)
    
    # Ambil kalimat yang informatif
    hasil = []
    for k in kalimat:
        if len(k) > 50 and not k.startswith(("Lompat", "Menu", "Navigasi")):
            hasil.append(k.strip())
            if len(hasil) >= max_kalimat:
                break
    
    return " ".join(hasil)


def jalankan(query, limit=5):
    """Cari di internet."""
    print(f"[web-search] Cari: {query}")
    
    hasil = {
        "sukses": True,
        "query": query,
        "wikipedia": search_wikipedia(query, limit),
        "waktu": datetime.now().isoformat(),
    }
    
    hasil["total"] = len(hasil["wikipedia"])
    print(f"  ✅ {hasil['total']} hasil")
    return hasil


def format_hasil(hasil):
    """Format hasil."""
    lines = [f"🔍 {hasil['query']}", ""]
    
    if hasil.get("wikipedia"):
        lines.append("📚 Hasil:")
        for i, r in enumerate(hasil["wikipedia"], 1):
            lines.append(f"  {i}. {r['title']}")
            lines.append(f"     {r.get('snippet', '')[:200]}")
            lines.append(f"     {r.get('url', '')}")
    
    return "\n".join(lines)


def cari_dan_baca(query, limit=3):
    """Cari + baca artikel pertama."""
    hasil = jalankan(query, limit)
    
    if hasil["wikipedia"]:
        first = hasil["wikipedia"][0]
        print(f"\n[web] Baca: {first['title']}")
        ringkasan = ringkas_artikel(first["url"])
        return {
            "sukses": True,
            "hasil": hasil,
            "artikel_utama": first,
            "ringkasan": ringkasan,
        }
    
    return {"sukses": False, "error": "Tidak ada hasil"}


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) or "AI 2026"
    hasil = cari_dan_baca(query)
    print(format_hasil(hasil["hasil"]))
    print(f"\n📄 Ringkasan:\n{hasil.get('ringkasan', '')[:500]}")

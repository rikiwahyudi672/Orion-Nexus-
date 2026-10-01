import sys
from pathlib import Path
_BASE = Path(__file__).parent.parent if Path(__file__).parent.name in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"] else Path(__file__).parent
sys.path.insert(0, str(_BASE))
for _f in ["core", "memory", "skill", "voice", "coding", "emotion", "support", "dashboard"]:
    _p = _BASE / _f
    if _p.exists():
        sys.path.insert(0, str(_p))

"""
model_router.py - Model router via Groq.
"""
import os
from dotenv import load_dotenv

load_dotenv()

MODELS = {
    "fast": {
        "id": "openai/gpt-oss-20b",
        "provider": "groq",
        "max_tokens": 500,
        "temperature": 0.2,
    },
    "balanced": {
        "id": "openai/gpt-oss-20b",
        "provider": "groq",
        "max_tokens": 1000,
        "temperature": 0.7,
    },
    "smart": {
        "id": "openai/gpt-oss-120b",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0.3,
    },
    "coding": {
        "id": "openai/gpt-oss-120b",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0.2,
    },
    "creative": {
        "id": "openai/gpt-oss-120b",
        "provider": "groq",
        "max_tokens": 1500,
        "temperature": 0.85,
    },
}

TUGAS_MODEL = {
    "routing": "fast",
    "sapaan": "fast",
    "coding": "coding",
    "code": "coding",
    "program": "coding",
    "konten": "creative",
    "riset": "balanced",
    "email": "balanced",
    "analisis": "smart",
    "laporan": "smart",
    "kreatif": "creative",
    "jarvis": "creative",
    "jarvis_smart": "smart",
    "smart": "smart",
    "default": "balanced",
}

_groq_client = None


def _get_groq():
    """Lazy load Groq client."""
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise Exception("GROQ_API_KEY tidak ada di .env")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def panggil_model(messages, tugas="default", max_tokens=None, temperature=None):
    """Panggil model via Groq."""
    nama = TUGAS_MODEL.get(tugas, "balanced")
    cfg = MODELS[nama]
    
    try:
        client = _get_groq()
        result = client.chat.completions.create(
            model=cfg["id"],
            messages=messages,
            max_tokens=max_tokens or cfg["max_tokens"],
            temperature=temperature if temperature is not None else cfg["temperature"],
        )
        return {
            "konten": result.choices[0].message.content,
            "model": cfg["id"],
            "provider": cfg["provider"],
        }
    except Exception as e:
        return {"konten": "", "error": str(e)}


if __name__ == "__main__":
    print("=== Test model_router ===")
    print("GROQ_API_KEY: " + ("ADA" if os.getenv("GROQ_API_KEY") else "TIDAK ADA"))
    print()
    
    # Test panggil
    result = panggil_model(
        messages=[{"role": "user", "content": "print('hello')"}],
        tugas="coding",
    )
    print("Hasil: " + str(result)[:200])

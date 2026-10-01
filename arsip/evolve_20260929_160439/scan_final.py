import sys
from pathlib import Path
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

import builtins
_orig = builtins.print
logs = []
def patched(*args, **kwargs):
    text = ' '.join(str(a) for a in args)
    logs.append(text)
    _orig(*args, **kwargs)
builtins.print = patched

import orion_tool_loop as otl

# Monkey-patch _load_jalankan
_orig_load = otl._load_jalankan
def patched_load(folder):
    result = _orig_load(folder)
    if 'script' in folder.name.lower():
        _orig(f"[LOAD] {folder.name} → {'OK' if result else 'None'}")
    return result
otl._load_jalankan = patched_load

reg = otl.bangun_registry()

builtins.print = _orig

_orig(f"Total: {len(reg)}")
_orig(f"script_maker: {'script_maker' in reg}")
_orig()
_orig("Logs:")
for log in logs:
    _orig(f"  {log}")

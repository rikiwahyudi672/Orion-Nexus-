import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import chat as tool_loop_chat

print("=== Test: baca VALUES.md ===")
hasil = tool_loop_chat("baca file _data/md/VALUES.md", riwayat=[], verbose=True)
print()
print("Hasil:", hasil[:800])

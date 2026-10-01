import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import chat as tool_loop_chat

# Test 1: Baca SOUL
print("=== Test 1: Baca SOUL.md ===")
hasil = tool_loop_chat("baca file config/SOUL.md", riwayat=[], verbose=True)
print(hasil[:600])
print()
print("=" * 70)
print()

# Test 2: Kamu siapa?
print("=== Test 2: Kamu siapa? ===")
hasil = tool_loop_chat("kamu siapa?", riwayat=[], verbose=True)
print(hasil[:500])

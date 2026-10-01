import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import chat as tool_loop_chat

# Test 1: Ngobrol
print("=== Test 1: Ngobrol ===")
hasil = tool_loop_chat("halo orion", riwayat=[], verbose=True)
print(hasil[:400])
print()

# Test 2: Kenal diri
print("=== Test 2: Kamu siapa? ===")
hasil = tool_loop_chat("kamu siapa?", riwayat=[], verbose=True)
print(hasil[:400])
print()

# Test 3: Baca file
print("=== Test 3: Baca SOUL.md ===")
hasil = tool_loop_chat("baca file config/SOUL.md", riwayat=[], verbose=True)
print(hasil[:400])

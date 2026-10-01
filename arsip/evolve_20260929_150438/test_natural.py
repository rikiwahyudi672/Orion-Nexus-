import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import chat as tool_loop_chat

# Test 1: Membantah
print("=== Test: kamu bodoh ===")
hasil = tool_loop_chat("kamu bodoh", riwayat=[], verbose=True)
print(hasil[:400])
print()

# Test 2: Tegas
print("=== Test: menurutmu aku salah? ===")
hasil = tool_loop_chat("menurutmu aku salah?", riwayat=[], verbose=True)
print(hasil[:400])
print()

# Test 3: Natural - tidak tawarin
print("=== Test: aku capek ===")
hasil = tool_loop_chat("aku capek", riwayat=[], verbose=True)
print(hasil[:400])

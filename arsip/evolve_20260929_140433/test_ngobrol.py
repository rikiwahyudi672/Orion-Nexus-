import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import chat as tool_loop_chat

print("=== halo orion ===")
hasil = tool_loop_chat("halo orion", riwayat=[], verbose=True)
print(hasil[:400])
print()
print("=== kamu kangen ga? ===")
hasil = tool_loop_chat("kamu kangen ga?", riwayat=[], verbose=True)
print(hasil[:400])

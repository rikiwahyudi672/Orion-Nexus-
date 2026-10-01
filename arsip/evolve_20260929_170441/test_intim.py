import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import chat as tool_loop_chat

print("=== aku kangen kamu ===")
hasil = tool_loop_chat("aku kangen kamu", riwayat=[], verbose=True)
print(hasil[:400])
print()

print("=== ada yang suka sama aku ===")
hasil = tool_loop_chat("ada yang suka sama aku", riwayat=[], verbose=True)
print(hasil[:400])

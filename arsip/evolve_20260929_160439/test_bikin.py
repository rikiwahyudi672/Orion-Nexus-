import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import chat as tool_loop_chat

print("=== bikin program kangen meter ===")
hasil = tool_loop_chat("bikin program kangen meter", riwayat=[], verbose=True)
print(hasil[:500])

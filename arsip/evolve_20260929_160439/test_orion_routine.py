import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')
from orion_tool_loop import chat as tool_loop_chat
print("=== baca ROUTINE.md ===")
hasil = tool_loop_chat("baca file _data/md/ROUTINE.md", riwayat=[], verbose=True)
print(hasil[:800])

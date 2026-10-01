import agent_manager as A
print("Agents terdaftar:")
for a in A.daftar_agent():
    print(f"  [{a['prioritas']}] {a['nama']:10} ({a['provider']}) - {a['capabilities']}")
print()
print("Total:", len(A.daftar_agent()))

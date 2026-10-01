import agent_manager as A

print("=== Agents ===")
for a in A.daftar_agent():
    print(f"  {a['nama']:10} | api_key_env={a.get('api_key_env')} | base_url={str(a.get('base_url'))[:40]}")

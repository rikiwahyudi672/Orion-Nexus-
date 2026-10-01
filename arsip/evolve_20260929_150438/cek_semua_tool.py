import sys
sys.path.insert(0, 'core')
sys.path.insert(0, '.')

from orion_tool_loop import bangun_registry

reg = bangun_registry()
print(f"Total: {len(reg)}")
print()
for name in sorted(reg.keys()):
    schema = reg[name].get('schema', {})
    if isinstance(schema, dict):
        params = list(schema.get('parameters', {}).keys())
    else:
        params = []
    print(f"  {name}({', '.join(params)})")

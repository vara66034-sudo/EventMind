import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from app.api.routes.agent import get_api
api = get_api()
result = api.get_events()
print(f"Success: {result.get('success')}")
print(f"Total: {result.get('data', {}).get('total', 0)}")
items = result.get('data', {}).get('items', [])
print(f"Items count: {len(items)}")
if items:
    print(f"First event: {json.dumps(items[0], ensure_ascii=False, default=str)}")

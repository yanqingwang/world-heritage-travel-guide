import base64, hashlib, json, subprocess, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

TOKEN = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True).stdout.strip()
API = 'https://api.github.com'
REPO = 'yanqingwang/world-heritage-travel-guide'

def api(method, path, payload=None, binary=None, tries=6, timeout=180):
    req = urllib.request.Request(f'{API}{path}', method=method)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Accept', 'application/vnd.github+json')
    body = None
    if binary is not None:
        body = json.dumps({'content': base64.b64encode(binary).decode(), 'encoding': 'base64'}).encode()
    elif payload is not None:
        body = json.dumps(payload).encode()
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, data=body, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            print(f'HTTP {e.code} {path} attempt {a+1}', flush=True)
            if e.code in (409, 422, 500, 502, 503, 504) and a < tries - 1:
                time.sleep(4 * (a + 1)); continue
            raise
        except Exception as e:
            print(f'{type(e).__name__} {path} attempt {a+1}', flush=True)
            time.sleep(4 * (a + 1))
    raise RuntimeError(path)

# Full-tree comparison against local HEAD — no git-diff against unfetchable shas.
local = {}
for line in subprocess.run(['git', 'ls-tree', '-r', 'HEAD', '--format=%(objectname) %(path)'],
                           capture_output=True, text=True).stdout.splitlines():
    sha, path = line.split(' ', 1)
    local[path] = sha

remote = api('GET', f'/repos/{REPO}/commits/main')
print('remote head:', remote['sha'][:10], flush=True)
tree = api('GET', f"/repos/{REPO}/git/trees/{remote['commit']['tree']['sha']}?recursive=1")
remote_blobs = {e['path']: e['sha'] for e in tree.get('tree', []) if e['type'] == 'blob'}

todo = sorted(p for p in local if remote_blobs.get(p) != local[p])
print(f'{len(todo)} blobs to upload ({len(local)-len(todo)} match)', flush=True)

def upload(path):
    content = open(path, 'rb').read()
    assert hashlib.sha1(b'blob %d\x00' % len(content) + content).hexdigest() == local[path], path
    for _ in range(5):
        try:
            blob = api('POST', f'/repos/{REPO}/git/blobs', binary=content, tries=3)
            return {'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']}
        except Exception as e:
            print(f'retry {path}: {type(e).__name__}', flush=True)
            time.sleep(3)
    raise RuntimeError(f'blob failed: {path}')

items = []
with ThreadPoolExecutor(max_workers=4) as pool:
    for n, item in enumerate(pool.map(upload, todo), 1):
        items.append(item)
        if n % 50 == 0:
            print(f'{n}/{len(todo)} blobs', flush=True)

base_tree = remote['commit']['tree']['sha']
for i in range(0, len(items), 400):
    t = api('POST', f'/repos/{REPO}/git/trees', payload={'base_tree': base_tree, 'tree': items[i:i+400]})
    base_tree = t['sha']
    print(f'batch {i//400+1}: tree {base_tree[:10]}', flush=True)
msg = subprocess.run(['git', 'log', '-1', '--format=%B', 'HEAD'], capture_output=True, text=True).stdout
new_commit = api('POST', f'/repos/{REPO}/git/commits', payload={
    'message': msg, 'tree': base_tree, 'parents': [remote['sha']]})
api('PATCH', f'/repos/{REPO}/git/refs/heads/main', payload={'sha': new_commit['sha']})
print('PUSHED-VIA-API', new_commit['sha'])

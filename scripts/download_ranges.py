"""Download public, pinned HF artifacts using HTTPS ranges and published SHA-256."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib
import json
import shutil
import time
import requests

root = Path('/workspace/Musica_Ditadura/tools/ACE-Step-1.5/checkpoints')
manifest = json.loads(Path('/workspace/music-runtime/model-manifest.json').read_text())
parts_root = Path('/workspace/music-runtime/download-parts')
chunk = 64 * 1024 * 1024

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(8*1024*1024), b''):
            h.update(data)
    return h.hexdigest()

def fetch(task):
    url, start, end, out = task
    if out.exists() and out.stat().st_size == end-start+1:
        return end-start+1
    for attempt in range(3):
        try:
            tmp = out.with_suffix('.tmp')
            offset = tmp.stat().st_size if tmp.exists() else 0
            if offset == end-start+1:
                tmp.replace(out)
                return offset
            request_start = start + offset
            with requests.get(url, headers={'Range': f'bytes={request_start}-{end}'}, stream=True, timeout=(20,60)) as r:
                r.raise_for_status()
                expected = f'bytes {request_start}-{end}/'
                if r.status_code != 206 or not r.headers.get('Content-Range','').startswith(expected):
                    raise RuntimeError('Server did not honor byte range')
                tmp = out.with_suffix('.tmp')
                with tmp.open('ab' if offset else 'wb') as f:
                    for data in r.iter_content(1024*1024):
                        f.write(data)
                if tmp.stat().st_size != end-start+1:
                    raise RuntimeError('Incomplete byte range')
                tmp.replace(out)
                return end-start+1
        except Exception as e:
            if attempt == 2:
                # Do not expose signed redirect URLs in logs.
                raise RuntimeError(f'Range {start}-{end} failed: {type(e).__name__}') from None
            time.sleep(1+attempt)

jobs=[]
assemblies=[]
for info in manifest['files']:
    target=root/info['path']
    size=info['size']; sha=info['sha256']
    if target.exists() and target.stat().st_size==size and digest(target)==sha:
        print('Verified existing',info['path'],flush=True)
        continue
    work=parts_root/sha
    work.mkdir(parents=True,exist_ok=True)
    prefix=work/'prefix'
    if not prefix.exists():
        candidates=list((root/'.cache/huggingface/download').rglob(f'*.{sha}.incomplete'))
        if candidates and 0<candidates[0].stat().st_size<size:
            shutil.copyfile(candidates[0],prefix)
    offset=prefix.stat().st_size if prefix.exists() else 0
    pieces=[prefix] if offset else []
    url=f"https://huggingface.co/{manifest['repository']}/resolve/{manifest['revision']}/{info['path']}"
    for start in range(offset,size,chunk):
        end=min(size-1,start+chunk-1)
        out=work/f'{start:012d}-{end:012d}.part'
        jobs.append((url,start,end,out)); pieces.append(out)
    assemblies.append((info,target,pieces))
    print('Resume',info['path'],'from',offset,'of',size,flush=True)
completed=0
with ThreadPoolExecutor(max_workers=24) as pool:
    futures=[pool.submit(fetch,job) for job in jobs]
    for future in as_completed(futures):
        future.result(); completed+=1
        print('Parts',completed,'/',len(futures),flush=True)
for info,target,pieces in assemblies:
    target.parent.mkdir(parents=True,exist_ok=True)
    tmp=target.with_suffix(target.suffix+'.assembling')
    with tmp.open('wb') as out:
        for piece in pieces:
            with piece.open('rb') as src:
                shutil.copyfileobj(src,out,8*1024*1024)
    if tmp.stat().st_size != info['size'] or digest(tmp)!=info['sha256']:
        raise RuntimeError('SHA-256 mismatch: '+info['path']+'; do not use this artifact')
    tmp.replace(target)
    print('Verified SHA-256',info['path'],flush=True)
    shutil.rmtree(parts_root/info['sha256'])
print('All model artifacts verified',flush=True)

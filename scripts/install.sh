#!/usr/bin/env bash
set -euo pipefail
export UV_CACHE_DIR=/workspace/music-runtime/cache
export HF_HOME=/workspace/music-runtime/huggingface
export XDG_CACHE_HOME=/workspace/music-runtime/cache
mkdir -p /workspace/Musica_Ditadura/tools /workspace/music-runtime /workspace/music-output
# Bootstrap project metadata without overwriting retained runtime files.
project=/workspace/Musica_Ditadura
for artifact in model-manifest.json lm-small-manifest.json; do
    if [ ! -f "/workspace/music-runtime/$artifact" ]; then
        cp "$project/config/$artifact" "/workspace/music-runtime/$artifact"
    fi
done
if [ ! -f /workspace/music-runtime/download_ranges.py ]; then
    cp "$project/scripts/download_ranges.py" /workspace/music-runtime/download_ranges.py
fi
# Preserve existing checkouts. Only a fresh tool clone is checked out to the recorded version.
clone_tool() {
    local name="$1" url="$2" commit="$3"
    local target="/workspace/Musica_Ditadura/tools/$name"
    if [ ! -d "$target" ]; then
        git clone "$url" "$target"
        git -C "$target" checkout --detach "$commit"
    fi
    test "$(git -C "$target" rev-parse HEAD)" = "$commit"
}
clone_tool claude-music https://github.com/AgriciDaniel/claude-music.git 5aa0173a6b329e059568bef4253e2a62efe8b412
clone_tool ACE-Step-1.5 https://github.com/ace-step/ACE-Step-1.5.git ca1e85fe9430179831e6bc6be790c332190a3866
if [ ! -x /workspace/music-runtime/venv/bin/python ]; then
    uv venv /workspace/music-runtime/venv --python python3
fi
uv pip install --python /workspace/music-runtime/venv/bin/python --index-url https://download.pytorch.org/whl/cpu torch==2.10.0 torchaudio==2.10.0 torchvision==0.25.0
cat > /workspace/music-runtime/cpu-inference-pinned.txt <<'REQUIREMENTS'
accelerate==1.15.0
anyio==4.15.1
certifi==2026.10.18
cffi==2.1.1
charset-normalizer==3.5.2
diffusers==0.39.0
einops==0.8.2
einx==0.4.3
filelock==3.32.3
frozendict==2.4.7
fsspec==2026.7.0
h11==0.16.0
hf-xet==1.7.0
httpcore==1.0.9
httpx==0.28.1
huggingface-hub==0.36.2
idna==3.20
importlib-metadata==9.0.1
iniconfig==2.3.1
jinja2==3.1.6
llvmlite==0.50.0
loguru==0.7.3
markupsafe==3.0.3
mpmath==1.3.0
networkx==3.6.1
numba==0.68.0
numpy==2.5.2
packaging==26.3
pillow==12.3.0
pluggy==1.7.0
psutil==7.2.2
pycparser==3.11
pygments==2.21.0
pytest==9.1.1
pytorch-wavelets==1.3.0
pywavelets==1.10.0
pyyaml==6.0.3
regex==2026.9.29
requests==2.34.2
safetensors==0.8.0
scipy==1.18.1
setuptools==71.1.0
six==1.17.0
soundfile==0.14.0
sympy==1.14.0
tokenizers==0.22.2
toml==0.10.2
torch-einops-utils==0.1.36
tqdm==4.70.1
transformers==4.57.6
typing-extensions==4.16.0
urllib3==2.8.0
vector-quantize-pytorch==1.31.6
zipp==4.1.1
REQUIREMENTS
uv pip install --python /workspace/music-runtime/venv/bin/python -r /workspace/music-runtime/cpu-inference-pinned.txt
uv pip install --python /workspace/music-runtime/venv/bin/python gradio_client==2.7.1 huggingface-hub==0.36.2
python3 - <<'CONFIG'
from pathlib import Path
import json
p = Path('/workspace/Musica_Ditadura/tools/claude-music/skills/claude-music/config.json')
if not p.exists():
    c = json.loads(p.with_name('config.example.json').read_text())
    c.update(ace_step_dir='/workspace/Musica_Ditadura/tools/ACE-Step-1.5', checkpoint_dir='/workspace/Musica_Ditadura/tools/ACE-Step-1.5/checkpoints', output_dir='/workspace/music-output')
    c['defaults'].update(quality='standard', language='pt', offload_to_cpu=False, offload_dit_to_cpu=False, use_flash_attention=False)
    p.write_text(json.dumps(c, indent=2)+'\n')
CONFIG
cd /workspace/Musica_Ditadura/tools/claude-music
/workspace/music-runtime/venv/bin/python -m pytest tests/ -q
# Retained snapshot files: model-manifest.json and download_ranges.py in /workspace/music-runtime.
# The prepared checkpoint files were verified against the published SHA-256 manifest.
export HF_HUB_DISABLE_XET=1
export ACESTEP_GENERATION_TIMEOUT=7200
/workspace/music-runtime/venv/bin/python - <<'MODELS'
from pathlib import Path
import json, subprocess, sys
runtime=Path('/workspace/music-runtime')
manifest=json.loads((runtime/'model-manifest.json').read_text())
root=Path('/workspace/Musica_Ditadura/tools/ACE-Step-1.5/checkpoints')
if any(not (root/f['path']).is_file() or (root/f['path']).stat().st_size != f['size'] for f in manifest['files']):
    from huggingface_hub import snapshot_download
    snapshot_download(manifest['repository'], revision=manifest['revision'], local_dir=str(root), allow_patterns=['*.json','*.py','*.pt','*.txt','*.jinja','.gitattributes','README.md'], max_workers=4)
    subprocess.run([sys.executable,str(runtime/'download_ranges.py')],check=True)
small=json.loads((runtime/'lm-small-manifest.json').read_text())
small_root=root/'acestep-5Hz-lm-0.6B'
if any(not (small_root/f['path']).is_file() or (small_root/f['path']).stat().st_size != f['size'] for f in small['files']):
    from huggingface_hub import snapshot_download
    snapshot_download(small['repo'], revision=small['revision'], local_dir=str(small_root), max_workers=4)
print('Prepared ACE-Step and 0.6B LM files present; no duplicate download when sizes match.')
MODELS

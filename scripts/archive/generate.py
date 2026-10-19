"""Codex adapter: invokes the upstream claude-music Python entry point unchanged."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--test', action='store_true', help='Generate a 25-second chorus before attempting the complete song')
args = parser.parse_args()
plan = json.loads(Path('/workspace/music-output/composicao.json').read_text())
base = Path('/workspace/Musica_Ditadura/tools')
engine = base / 'claude-music/skills/claude-music/scripts/music_engine.py'
ace = base / 'ACE-Step-1.5'
# Fail clearly before upstream automatic retries when model access is blocked.
checks = [ace / 'checkpoints' / x for x in ('acestep-v15-turbo', 'vae', 'Qwen3-Embedding-0.6B')]
if not all(p.is_dir() for p in checks):
    sys.exit('Modelos ausentes. O acesso ao Hugging Face precisa estar liberado antes do download oficial e da geração.')
lyrics = plan['lyrics']
if args.test:
    lyrics = '[Chorus]' + lyrics.split('[Chorus]', 1)[1].split('[Verse 2]', 1)[0]
output = Path('/workspace/music-output/teste' if args.test else '/workspace/music-output/completa')
output.mkdir(exist_ok=True)
env = os.environ.copy()
env.update(HF_HOME='/workspace/music-runtime/huggingface', XDG_CACHE_HOME='/workspace/music-runtime/cache', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', TOKENIZERS_PARALLELISM='false', ACESTEP_INIT_LLM='false')
cmd = [sys.executable, str(engine), '--ace-step-dir', str(ace), '--quality', 'standard', '--progress', '--batch', '1', '--format', 'flac', '--seed', str(plan['seed']), '--output-dir', str(output), 'generate', '--caption', plan['caption'], '--lyrics', lyrics, '--language', 'pt', '--bpm', '82', '--key', 'D minor', '--time-sig', '4', '--duration', '25' if args.test else str(plan['duration']), '--no-thinking']
result = subprocess.run(cmd, cwd=ace, env=env)
sys.exit(result.returncode)

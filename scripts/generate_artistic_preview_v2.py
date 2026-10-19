"""Generate exactly one original 30s male-MPB preview; never a full song."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess

PROJECT = Path(__file__).resolve().parents[1]
RUNTIME = Path('/workspace/music-runtime')
TOOLS = PROJECT / 'tools'
CONFIG = json.loads((PROJECT / 'config/artistic-preview-v2.json').read_text())
RESULT = RUNTIME / 'artistic-v2-preview-result.json'
if RESULT.exists():
    raise SystemExit('V2 preview result already exists; refusing another generation.')
if CONFIG['duration'] != 30 or CONFIG['full_generation_authorized']:
    raise SystemExit('This runner only supports the unapproved 30-second preview.')
os.environ.update(HF_HOME=str(RUNTIME / 'huggingface'), HF_HUB_DISABLE_XET='1',
                  HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                  XDG_CACHE_HOME=str(RUNTIME / 'cache'), OMP_NUM_THREADS='4',
                  MKL_NUM_THREADS='4', TOKENIZERS_PARALLELISM='false',
                  ACESTEP_INIT_LLM='false', ACESTEP_GENERATION_TIMEOUT='7200')
import torch
import numpy as np
import soundfile as sf

torch.set_num_threads(4)
spec = importlib.util.spec_from_file_location('claude_music_engine',
    TOOLS / 'claude-music/skills/claude-music/scripts/music_engine.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
original_output = engine.output_json
captured = None


def record(result):
    """Preserve the engine result separately from discarded V1 outputs."""
    global captured
    captured = result
    result['runtime_precision'] = 'Native FP32 CPU; planning LM 0.6B'
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    original_output(result)


engine.output_json = record
out = Path('/workspace/music-output/preview-v2-male-mpb')
subprocess.run(['bash', str(TOOLS / 'claude-music/skills/claude-music/scripts/preflight.sh'),
                '', str(out / 'generated.flac')], check=True)
argv = ['--ace-step-dir', str(TOOLS / 'ACE-Step-1.5'), '--quality', 'high',
        '--lm-model', CONFIG['lm_model'], '--batch', '1', '--format', 'flac',
        '--seed', str(CONFIG['seed']), '--progress', '--output-dir', str(out),
        'generate', '--caption', CONFIG['caption'], '--lyrics', CONFIG['lyrics'],
        '--language', 'pt', '--bpm', str(CONFIG['bpm']), '--key', CONFIG['key'],
        '--time-sig', '4', '--duration', '30', '--shift', '3.0', '--thinking']
engine.cmd_generate(engine.build_parser().parse_args(argv))
if not captured or not captured.get('success'):
    raise RuntimeError('Preview generation failed')
source = Path(captured['outputs'][0]['path'])
y, sr = sf.read(source, always_2d=True, dtype='float32')
if not np.isfinite(y).all() or np.max(np.abs(y)) < 0.001 or abs(len(y) / sr - 30) > 1:
    raise RuntimeError('Invalid preview waveform or duration')
flac = PROJECT / 'samples/mpb-masculina-v2-preview-30s.flac'
mp3 = PROJECT / 'music/samples/mpb-masculina-v2-preview-30s.mp3'
shutil.copy2(source, flac)
subprocess.run(['ffmpeg', '-nostdin', '-y', '-v', 'error', '-i', str(source),
                '-ar', '48000', '-ac', '2', '-c:a', 'libmp3lame', '-b:a', '320k',
                '-id3v2_version', '3', '-metadata',
                'title=O Peso da Minha Mão — Prévia V2 masculina', str(mp3)], check=True)
shutil.copy2(RESULT, PROJECT / 'config/artistic-v2-preview-result.json')
state_path = PROJECT / 'config/production-state.json'
state = json.loads(state_path.read_text())
state.update(v2_status='preview_ready_awaiting_user_artistic_approval', full_generation_authorized=False)
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
print('V2 PREVIEW EXPORTED. STOPPED: WAITING FOR USER ARTISTIC APPROVAL.', flush=True)

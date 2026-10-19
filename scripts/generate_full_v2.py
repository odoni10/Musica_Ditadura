"""Generate the user-approved full V2 once and export audio with complete lyrics."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
RUNTIME = Path('/workspace/music-runtime')
TOOLS = PROJECT / 'tools'
CONFIG = json.loads((PROJECT / 'config/full-v2.json').read_text())
STATE = PROJECT / 'config/production-state.json'
RESULT = RUNTIME / 'artistic-v2-full-result.json'
if RESULT.exists():
    raise SystemExit('Full V2 result already exists; recover it rather than rerendering.')
if not CONFIG['full_generation_authorized'] or not json.loads(STATE.read_text())['full_generation_authorized']:
    raise SystemExit('Explicit user approval is required for the complete song.')
os.environ.update(HF_HOME=str(RUNTIME / 'huggingface'), HF_HUB_DISABLE_XET='1',
                  HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                  XDG_CACHE_HOME=str(RUNTIME / 'cache'), OMP_NUM_THREADS='4',
                  MKL_NUM_THREADS='4', TOKENIZERS_PARALLELISM='false',
                  ACESTEP_INIT_LLM='false', ACESTEP_GENERATION_TIMEOUT='7200')
import torch
from export_final import export

torch.set_num_threads(4)
spec = importlib.util.spec_from_file_location('claude_music_engine',
    TOOLS / 'claude-music/skills/claude-music/scripts/music_engine.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
original_output = engine.output_json
original_init = engine.initialize_acestep
captured = None


def initialize(args):
    """Expose real progress without changing the approved generation settings."""
    initialized = original_init(args)
    handler, lm, _ = initialized
    if handler is None or lm is None:
        raise RuntimeError('Expected CPU DiT and planning LM')
    handler.disable_tqdm = False
    lm.disable_tqdm = False
    return initialized


def record(result):
    """Keep the full render separate from approved and discarded previews."""
    global captured
    captured = result
    result['runtime_precision'] = 'Native FP32 CPU; planning LM 0.6B'
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    original_output(result)


engine.initialize_acestep = initialize
engine.output_json = record
out = Path('/workspace/music-output/full-v2-male-mpb')
subprocess.run(['bash', str(TOOLS / 'claude-music/skills/claude-music/scripts/preflight.sh'),
                '', str(out / 'generated.flac')], check=True)
argv = ['--ace-step-dir', str(TOOLS / 'ACE-Step-1.5'), '--quality', CONFIG['quality'],
        '--lm-model', CONFIG['lm_model'], '--batch', '1', '--format', 'flac',
        '--seed', str(CONFIG['seed']), '--progress', '--output-dir', str(out),
        'generate', '--caption', CONFIG['caption'], '--lyrics', CONFIG['lyrics'],
        '--language', CONFIG['language'], '--bpm', str(CONFIG['bpm']), '--key', CONFIG['key'],
        '--time-sig', CONFIG['time_sig'], '--duration', str(CONFIG['duration']),
        '--shift', str(CONFIG['shift']), '--thinking']
engine.cmd_generate(engine.build_parser().parse_args(argv))
if not captured or not captured.get('success'):
    raise RuntimeError('Full V2 generation failed')
source = Path(captured['outputs'][0]['path'])
final = PROJECT / 'final'
final.mkdir(exist_ok=True)
shutil.copy2(source, final / 'O_Peso_da_Minha_Mao.flac')
shutil.copy2(RESULT, PROJECT / 'config/final-engine-result.json')
report = export(source, final)
if abs(report['source_measurements']['duration_seconds'] - CONFIG['duration']) > 1:
    raise RuntimeError('Full render duration mismatch')
shutil.copy2(PROJECT / 'lyrics/letra.txt', final / 'O_Peso_da_Minha_Mao_LETRA.txt')
shutil.copy2(PROJECT / 'config/full-v2.json', final / 'parametros-v2.json')
with zipfile.ZipFile(final / 'O_Peso_da_Minha_Mao_MP3_e_Letra.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for name in ['O_Peso_da_Minha_Mao.mp3', 'O_Peso_da_Minha_Mao_LETRA.txt', 'parametros-v2.json']:
        archive.write(final / name, arcname=name)
state = json.loads(STATE.read_text())
state.update(v2_status='complete_audio_and_lyrics_exported', next_allowed_action='Verify and publish final deliverables')
STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
print('FULL V2 EXPORTED: MP3, WAV, FLAC, COMPLETE LYRICS AND ZIP. NO FURTHER GENERATION.', flush=True)

"""Codex adapter: upstream claude-music with CPU dynamic INT8 on the DiT decoder and language model.
Uses PyTorch quantize_dynamic, leaves text encoder/VAE FP32 and keeps original
source and checkpoint weights unchanged. Reuses loaded models after sample QA.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

runtime=Path('/workspace/music-runtime')
outputs=Path('/workspace/music-output')
base=Path('/workspace/Musica_Ditadura/tools')
os.environ.update(HF_HOME=str(runtime/'huggingface'), XDG_CACHE_HOME=str(runtime/'cache'), OMP_NUM_THREADS='4', MKL_NUM_THREADS='4', TOKENIZERS_PARALLELISM='false', ACESTEP_INIT_LLM='false', ACESTEP_GENERATION_TIMEOUT='7200')
spec=importlib.util.spec_from_file_location('claude_music_engine',base/'claude-music/skills/claude-music/scripts/music_engine.py')
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
import torch
torch.set_num_threads(4)
original_init=engine.initialize_acestep
cached=None

def initialize(args):
    global cached
    if cached is None:
        cached=original_init(args)
        handler=cached[0]
        if handler is not None:
            handler.disable_tqdm=False
            if handler.device!='cpu':
                raise RuntimeError('This adapter is for CPU only')
            handler.model.decoder=torch.ao.quantization.quantize_dynamic(handler.model.decoder,{torch.nn.Linear},dtype=torch.qint8,inplace=True)
            lm=cached[1]
            if lm is None or lm.llm_backend!='pt':
                raise RuntimeError('CPU thinking requires the PyTorch LM backend')
            lm.llm=torch.ao.quantization.quantize_dynamic(lm.llm,{torch.nn.Linear},dtype=torch.qint8,inplace=True)
            print('CPU dynamic INT8 enabled on DiT decoder and 1.7B LM; text encoder and VAE remain FP32.',file=sys.stderr,flush=True)
    return cached
engine.initialize_acestep=initialize
last_result=None
phase='sample'
original_output=engine.output_json

def record(result):
    global last_result
    last_result=result
    result['runtime_precision']='CPU dynamic INT8 on DiT decoder and 1.7B LM; FP32 text encoder and VAE'
    (runtime/f'high-{phase}-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    original_output(result)
engine.output_json=record

def generate(sample):
    global phase,last_result
    phase='sample' if sample else 'full'
    plan=json.loads((outputs/'composicao.json').read_text())
    lyrics=plan['lyrics']
    if sample:
        lyrics='[Chorus]'+lyrics.split('[Chorus]',1)[1].split('[Verse 2]',1)[0]
    out=outputs/('teste_high' if sample else 'completa')
    subprocess.run(['bash',str(base/'claude-music/skills/claude-music/scripts/preflight.sh'),'',str(out/'generated.flac')],check=True)
    argv=['--ace-step-dir',str(base/'ACE-Step-1.5'),'--quality','high','--batch','1','--format','flac','--seed',str(plan['seed']),'--progress','--output-dir',str(out),'generate','--caption',('Brazilian MPB protest ballad, expressive female lead singing in Brazilian Portuguese from the start, nylon-string acoustic guitar, piano, organic bass, pandeiro, warm natural studio sound' if sample else plan['caption']),'--lyrics',lyrics,'--language','pt','--bpm','82','--key','D minor','--time-sig','4','--duration','30' if sample else '180','--thinking']
    args=engine.build_parser().parse_args(argv)
    engine.cmd_generate(args)
    if not last_result or not last_result.get('success'):
        raise RuntimeError('Generation did not complete successfully')

if __name__=='__main__':
    generate(True)
    gate=runtime/'high-quality-gate.json'
    if gate.exists():
        raise RuntimeError('Stale quality gate: inspect and remove it before a new production run')
    print('Sample complete. Waiting for internal technical quality check.',file=sys.stderr,flush=True)
    for _ in range(1800):
        if gate.exists():
            decision=json.loads(gate.read_text())
            if decision.get('proceed') is True:
                generate(False)
                print('Complete song generated.',file=sys.stderr,flush=True)
                break
            raise RuntimeError('Quality gate did not authorize the full generation')
        time.sleep(1)
    else:
        raise RuntimeError('Internal quality-check timeout')

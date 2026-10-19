"""Technical intelligibility check with Whisper; no reference lyrics in input."""
import argparse
import json
import math
import os
from pathlib import Path
os.environ.setdefault('HF_HOME','/workspace/music-runtime/huggingface')
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
os.environ.setdefault('OMP_NUM_THREADS','4')
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('audio')
parser.add_argument('--output',required=True)
parser.add_argument('--language',default='portuguese')
parser.add_argument('--model',default='openai/whisper-base')
args=parser.parse_args()
torch.set_num_threads(4)
processor=WhisperProcessor.from_pretrained(args.model)
model=WhisperForConditionalGeneration.from_pretrained(args.model,use_safetensors=True)
model.eval()
audio,sr=sf.read(args.audio,always_2d=True,dtype='float32')
y=audio.mean(axis=1)
g=math.gcd(sr,16000)
y=resample_poly(y,16000//g,sr//g).astype(np.float32)
results=[]
for start in range(0,len(y),30*16000):
    chunk=y[start:start+30*16000]
    features=processor(chunk,sampling_rate=16000,return_tensors='pt',return_attention_mask=True)
    with torch.inference_mode():
        output=model.generate(features.input_features,attention_mask=features.attention_mask,language=args.language,task='transcribe',max_new_tokens=220)
    text=processor.batch_decode(output,skip_special_tokens=True)[0]
    results.append({'start_seconds':start/16000,'text':text})
    print(json.dumps(results[-1],ensure_ascii=False),flush=True)
Path(args.output).write_text(json.dumps({'model':args.model,'language':args.language,'audio':args.audio,'segments':results,'limitations':'ASR is an imperfect intelligibility check for singing; no human listening was performed.'},ensure_ascii=False,indent=2)+'\n')

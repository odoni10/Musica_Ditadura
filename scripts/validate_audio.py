"""Check waveform and metadata; optional ASR is only an auxiliary indicator."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import soundfile as sf

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('result_json')
parser.add_argument('--asr-output',help='Optional auxiliary transcription; never a lyric-quality gate')
args=parser.parse_args()
result_path=Path(args.result_json)
result=json.loads(result_path.read_text())
if not result.get('success') or not result.get('outputs'):
    raise SystemExit('No successful generation to validate')
audio_path=Path(result['outputs'][0]['path'])
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(audio_path)],text=True))
y,sr=sf.read(audio_path,always_2d=True,dtype='float32')
assert np.isfinite(y).all(), 'Nonfinite samples'
assert np.max(np.abs(y))>0.001, 'Silent or invalid waveform'
duration=len(y)/sr
assert abs(duration-result['params']['duration'])<1, 'Unexpected duration'
blocks=[y[i:i+sr] for i in range(0,len(y),sr)]
rms=[float(20*np.log10(max(float(np.sqrt(np.mean(b*b))),1e-12))) for b in blocks]
report={'audio':str(audio_path),'duration_seconds':duration,'sample_rate':sr,'channels':y.shape[1],'sample_peak_dbfs':float(20*np.log10(np.max(np.abs(y)))),'rms_dbfs_per_second':rms,'ffprobe':probe,'auditory_evaluation':False}
result_path.with_name(result_path.stem+'-technical.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('ffprobe','rms_dbfs_per_second')},ensure_ascii=False),flush=True)
if args.asr_output:
    subprocess.run([sys.executable,str(Path(__file__).with_name('transcribe.py')),str(audio_path),'--output',args.asr_output],check=True)

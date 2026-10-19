"""Call the official ACE-Step Space using its published Gradio API schema."""
import argparse
import json
import time
from pathlib import Path
from gradio_client import Client
from huggingface_hub import get_token

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--full',action='store_true')
args=parser.parse_args()
runtime=Path('/workspace/music-runtime')
plan=json.loads(Path('/workspace/music-output/composicao.json').read_text())
info=json.loads((runtime/'space-api.json').read_text())['named_endpoints']['/generation_wrapper']
params={p['parameter_name']:p.get('parameter_default') for p in info['parameters']}
params.update(selected_model='acestep-v15-turbo',generation_mode='custom',simple_query_input='',simple_vocal_language='pt',param_4=plan['caption'],param_5=plan['lyrics'],param_6=82,param_7='D minor',param_8='4',param_9='pt',param_10=8,param_12=False,param_13=str(plan['seed']),param_14=None,param_15=210 if args.full else 30,param_16=1,param_17=None,param_18='',param_30='flac',param_32=False,param_37=False,param_38=False,param_39=False,param_11=0.0,param_47=None)
if not args.full:
    params['param_4']='Brazilian MPB protest ballad, expressive female lead singing in Brazilian Portuguese from the start, nylon-string acoustic guitar, piano, organic bass, pandeiro, warm natural studio sound'
    params['param_5']='[Chorus]'+plan['lyrics'].split('[Chorus]',1)[1].split('[Verse 2]',1)[0]
phase='full' if args.full else 'sample'
(runtime/f'remote-{phase}-request.json').write_text(json.dumps(params,ensure_ascii=False,indent=2)+'\n')
client=Client('https://ace-step-ace-step-v1-5.hf.space',verbose=False,hf_token=get_token(),download_files='/workspace/music-output/remote')
print('Submitting official free Space generation:',phase,flush=True)
job=client.submit(api_name='/generation_wrapper',**params)
last=None
while not job.done():
    status=job.status()
    current=str(status.code)+' '+str([getattr(p,'desc',None) for p in (status.progress_data or [])])
    if current!=last:
        print('Queue status:',current,flush=True)
        last=current
    time.sleep(2)
result=job.result()
(runtime/f'remote-{phase}-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str)+'\n')
print('Official Space response received.',flush=True)
for i,item in enumerate(result):
    if i<12:
        if isinstance(item,str):
            print(i,item[:1800],flush=True)
        else:
            print(i,repr(item)[:1000],flush=True)

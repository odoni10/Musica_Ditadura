"""Separate generated scene pairs and build a no-reuse editorial timeline."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
NAMES=["A chegada ao bairro","A distância à mesa","Antes de compartilhar","O alimento esquecido",
       "Abrir espaço para respirar","Uma porta entre nós","Certezas levadas pelo vento","A dúvida diante do espelho",
       "As pessoas da fila","O instante da escolha","A vida no ônibus","A espera e o cuidado",
       "A ponte interrompida","O que a água levou","O amigo atrás do portão","Caminhos que se afastam",
       "Conferir antes de acreditar","Aprender a escutar","Uma pergunta em comunidade","Acompanhar o que foi prometido",
       "Um pequeno reparo coletivo","O portão se abre","Repartir o pão","A casa por dentro, vista de fora"]
TARGETS=[0,8,16,24,32,40,48,56,65,74,83,92,101,110,119,128,137,146,155,164,173,182,191,201]


def main():
    manifest=[]
    sheets=json.loads((ROOT/"config/source-sheets.json").read_text())
    for sheet in sheets:
        source=Path(sheet["source"])
        image=Image.open(source).convert("RGB")
        w,h=image.size
        assert abs(w/(h/2)-16/9)<.04, (source,image.size)
        sheet["sha256"]=hashlib.sha256(source.read_bytes()).hexdigest()
        for half in range(2):
            n=(int(sheet["id"])-1)*2+half+1
            filename=f"assets/s{n:02}.png"
            panel=image.crop((0,h*half//2,w,h*(half+1)//2))
            panel.save(ROOT/filename,optimize=True)
            manifest.append({"id":f"s{n:02}","file":filename,"scene":NAMES[n-1],
                             "source_sheet":sheet["id"],"half":"top" if half==0 else "bottom",
                             "size":panel.size,"sha256":hashlib.sha256((ROOT/filename).read_bytes()).hexdigest(),
                             "uses_in_timeline":1})
    assert len({a["sha256"] for a in manifest})==24
    (ROOT/"config/source-sheets.json").write_text(json.dumps(sheets,ensure_ascii=False,indent=2)+"\n")
    (ROOT/"config/assets.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    features=json.loads((ROOT/"config/audio-features.json").read_text())
    attacks=np.array(features["attack_times"])
    shots=[]
    for i,target in enumerate(TARGETS):
        nearby=attacks[np.abs(attacks-target)<=.65]
        start=float(nearby[np.argmin(abs(nearby-target))]) if i and len(nearby) else target
        frame=round(start*24)
        cameras=[([.50,.50,1.025],[.515,.495,1.09]),([.49,.50,1.07],[.51,.50,1.07]),
                 ([.51,.50,1.10],[.50,.50,1.035]),([.50,.49,1.035],[.49,.51,1.085])]
        c0,c1=cameras[i%4]
        shots.append({"start":frame/24,"start_frame":frame,"asset":f"s{i+1:02}","narrative":NAMES[i],
                      "camera_start":c0,"camera_end":c1,"transition_seconds":.65 if i else 0})
    for i,shot in enumerate(shots):
        end=shots[i+1]["start_frame"] if i<23 else 5040
        shot.update(end_frame=end,end=end/24)
    master=ROOT.parent/"final/O_Peso_da_Minha_Mao.wav"
    config={"title":"O Peso da Minha Mão","version":"videoclipe-v2","duration":210,
            "width":1920,"height":1080,"fps":24,"seed":190102126,
            "audio":"../final/O_Peso_da_Minha_Mao.wav","audio_sha256":hashlib.sha256(master.read_bytes()).hexdigest(),
            "shots":shots,"unique_artworks":24,"reused_artworks":0,"named_credits":False,
            "sync_method":"Montagem narrativa, cortes próximos a ataques existentes (±0,65 s) e resposta suave à energia. Sem alinhamento palavra a palavra.",
            "audio_processing":"Master V2 integral, sem nova síntese, velocidade ou edição; AAC 256 kbps.",
            "render":{"codec":"libx264","preset":"veryfast","crf":21,"maxrate":"3200k","bufsize":"6400k","pixel_format":"yuv420p"}}
    (ROOT/"config/timeline.json").write_text(json.dumps(config,ensure_ascii=False,indent=2)+"\n")
    print("24 distinct assets; 24 shots; every artwork used once; no named credits.")


if __name__=="__main__":
    main()

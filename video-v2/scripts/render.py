"""Render the complete illustrated film, using only the existing music master."""
from pathlib import Path
import argparse
import bisect
import json
import subprocess
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from motion import Scene, ease

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Regular.ttf"
SMALL_FONT = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


class Film:
    def __init__(self):
        self.config = json.loads((ROOT/"config/timeline.json").read_text())
        self.shots = self.config["shots"]
        self.starts = [s["start"] for s in self.shots]
        self.size = (self.config["width"], self.config["height"])
        self.fps = self.config["fps"]
        self.duration = self.config["duration"]
        self.scenes = {s: Scene(s, ROOT/"assets"/f"{s}.png", self.size)
                       for s in {shot["asset"] for shot in self.shots}}
        features = json.loads((ROOT/"config/audio-features.json").read_text())
        self.energy = np.array(features["energy"])
        self.energy_interval = features["sample_interval"]
        self.title = self.make_title()

    def make_title(self):
        w,h = self.size
        layer = Image.new("RGBA", self.size, (0,0,0,0))
        draw = ImageDraw.Draw(layer)
        serif = ImageFont.truetype(FONT, int(h*.061))
        sans = ImageFont.truetype(SMALL_FONT, int(h*.018))
        # Title occupies the uninhabited wall between father and daughter.
        draw.text((w*.50,h*.225), "O PESO DA", font=sans, anchor="mm",
                  fill=(234,216,181,245), stroke_width=1, stroke_fill=(13,20,25,70))
        draw.text((w*.50,h*.284), "MINHA MÃO", font=serif, anchor="mm",
                  fill=(239,221,188,255), stroke_width=1, stroke_fill=(13,20,25,95))
        draw.line((w*.47,h*.338,w*.53,h*.338), fill=(199,151,90,190), width=1)
        rgba = np.asarray(layer)
        return rgba[:,:,:3][:,:,::-1].copy(), rgba[:,:,3:4].astype(np.float32)/255

    def scene_frame(self, index, t):
        shot = self.shots[index]
        p = float(np.clip((t-shot["start"])/(shot["end"]-shot["start"]), 0, 1))
        camera = (np.array(shot["camera_start"])*(1-ease(p))+
                  np.array(shot["camera_end"])*ease(p))
        half = .5/camera[2] + .004
        camera[:2] = np.clip(camera[:2], half, 1-half)
        energy = float(self.energy[min(int(t/self.energy_interval),len(self.energy)-1)])
        return self.scenes[shot["asset"]].draw(camera,t,p,energy)

    def frame(self, t):
        index = max(0,bisect.bisect_right(self.starts,t)-1)
        shot = self.shots[index]
        frame = self.scene_frame(index,t)
        transition = shot["transition_seconds"]
        if index and t-shot["start"] < transition:
            previous = self.scene_frame(index-1,t)
            mix = float(ease((t-shot["start"])/transition))
            frame = cv2.addWeighted(previous,1-mix,frame,mix,0)
        title_opacity = float(ease((t-1.0)/1.6)*(1-ease((t-7.5)/1.8)))
        if title_opacity > 0:
            color, alpha = self.title
            a = alpha*title_opacity
            frame = (frame*(1-a)+color*a).astype(np.uint8)
        fade = float(ease(t/1.1)*(1-ease((t-(self.duration-2.0))/1.9)))
        if fade < 1:
            frame = cv2.convertScaleAbs(frame,alpha=fade)
        return frame

    def contact_sheet(self):
        picks = [(s["start"]+s["end"])/2 for s in self.shots]
        tw,th = 400,225
        canvas = Image.new("RGB", (tw*4, (th+34)*6), "#101820")
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.truetype(SMALL_FONT,15)
        for i,t in enumerate(picks):
            frame = cv2.cvtColor(cv2.resize(self.frame(t),(tw,th)),cv2.COLOR_BGR2RGB)
            col,row = i%4,i//4
            canvas.paste(Image.fromarray(frame),(col*tw,row*(th+34)))
            shot = self.shots[max(0,bisect.bisect_right(self.starts,t)-1)]
            label=f"{int(t)//60:02d}:{int(t)%60:02d}  {shot['narrative']}"
            draw.text((col*tw+10,row*(th+34)+th+8),label,font=font,fill="#dec69e")
        canvas.save(ROOT/"docs/storyboard.jpg",quality=90)
        cv2.imwrite(str(ROOT/"output/cartaz.jpg"),self.frame(4),[cv2.IMWRITE_JPEG_QUALITY,94])

    def render(self):
        output = ROOT/"output/O_Peso_da_Minha_Mao_Videoclipe_V2.mp4"
        if output.exists():
            raise SystemExit(f"Preserving existing final video: {output}")
        partial = output.with_name(output.stem+".partial.mp4")
        if partial.exists():
            raise SystemExit(f"Partial file exists; inspect before resuming: {partial}")
        w,h = self.size
        command = ["ffmpeg","-hide_banner","-loglevel","warning","-y",
                   "-f","rawvideo","-pix_fmt","bgr24","-s",f"{w}x{h}",
                   "-r",str(self.fps),"-i","pipe:0","-i",str(ROOT/self.config["audio"]),
                   "-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","veryfast",
                   "-crf","21","-maxrate","3200k","-bufsize","6400k","-threads","3",
                   "-pix_fmt","yuv420p","-profile:v","high","-level","4.1",
                   "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
                   "-vf","scale=out_color_matrix=bt709:out_range=tv",
                   "-c:a","aac","-b:a","256k","-ar","48000","-ac","2",
                   "-t",str(self.duration),"-movflags","+faststart",
                   "-metadata","title=O Peso da Minha Mão — Videoclipe",
                   "-metadata","comment=Videoclipe V2, 24 cenas distintas em pintura; música integral preservada.",
                   str(partial)]
        started = time.monotonic()
        encoder = subprocess.Popen(command,stdin=subprocess.PIPE)
        frames = round(self.duration*self.fps)
        try:
            for i in range(frames):
                encoder.stdin.write(self.frame(i/self.fps).tobytes())
                if i % (self.fps*10) == 0:
                    elapsed=time.monotonic()-started
                    print(f"{i/frames:6.1%} | film {i/self.fps:6.1f}/{self.duration:.1f}s | elapsed {elapsed:.1f}s",flush=True)
            encoder.stdin.close()
            status = encoder.wait()
            if status:
                raise RuntimeError(f"ffmpeg exited with status {status}")
        except BaseException:
            if encoder.stdin and not encoder.stdin.closed:
                encoder.stdin.close()
            encoder.wait()
            raise
        partial.rename(output)
        result={"video":str(output),"frames":frames,"seconds":self.duration,
                "render_seconds":round(time.monotonic()-started,2),
                "bytes":output.stat().st_size,"audio_sha256":self.config["audio_sha256"],
                "width":w,"height":h,"fps":self.fps,"shots":len(self.shots)}
        (ROOT/"docs/render-result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
        print(json.dumps(result,ensure_ascii=False),flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyboard",action="store_true")
    args = parser.parse_args()
    cv2.setNumThreads(2)
    film = Film()
    if args.storyboard:
        film.contact_sheet()
    else:
        film.render()


if __name__ == "__main__":
    main()

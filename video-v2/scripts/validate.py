"""Verify the actual export, full decode, music timing and source preservation."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

import cv2
import numpy as np
from scipy.signal import correlate, correlation_lags

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "output/O_Peso_da_Minha_Mao_Videoclipe_V2.mp4"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def decode_audio(path):
    data = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path),
                                    "-map", "0:a:0", "-ac", "1", "-ar", "8000",
                                    "-f", "f32le", "pipe:1"])
    return np.frombuffer(data, dtype="<f4")


def atoms(path):
    found = []
    with path.open("rb") as file:
        while True:
            offset = file.tell()
            header = file.read(8)
            if len(header) != 8:
                break
            size, kind = struct.unpack(">I4s", header)
            if size == 1:
                size = struct.unpack(">Q", file.read(8))[0]
            found.append(kind.decode("ascii"))
            if size == 0:
                break
            file.seek(offset+size)
    return found


def main():
    config = json.loads((ROOT/"config/timeline.json").read_text())
    source = ROOT/config["audio"]
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(VIDEO)]))
    visual = next(s for s in info["streams"] if s["codec_type"] == "video")
    sound = next(s for s in info["streams"] if s["codec_type"] == "audio")
    assert visual["codec_name"] == "h264"
    assert (visual["width"], visual["height"]) == (1920, 1080)
    assert visual["pix_fmt"] == "yuv420p" and visual["avg_frame_rate"] == "24/1"
    assert int(visual["nb_frames"]) == 5040
    assert abs(float(info["format"]["duration"])-210) < .05
    assert sound["codec_name"] == "aac" and int(sound["sample_rate"]) == 48000
    assert int(sound["channels"]) == 2
    assert abs(float(sound["duration"])-float(visual["duration"])) < .05
    assert sha256(source) == config["audio_sha256"]
    assert len(config["shots"]) == 24
    assert len({s["asset"] for s in config["shots"]}) == 24
    assert VIDEO.stat().st_size < 100*1024*1024
    for entry in json.loads((ROOT/"config/assets.json").read_text()):
        assert sha256(ROOT/entry["file"]) == entry["sha256"]
    print("Container, duration, frame count, sources and size: OK",flush=True)
    subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(VIDEO),
                    "-f", "null", "-"], check=True)
    print("Full audio/video decode: OK",flush=True)
    original, exported = decode_audio(source), decode_audio(VIDEO)
    count = min(len(original), len(exported))
    assert np.isfinite(exported).all() and np.max(np.abs(exported)) > .01
    similarity = float(np.corrcoef(original[:count],exported[:count])[0,1])
    # 1 ms timing resolution; compressed AAC need not be bit-identical.
    a, b = original[:count:8], exported[:count:8]
    corr = correlate(b,a,mode="full",method="fft")
    lags = correlation_lags(len(b),len(a),mode="full")
    lag_ms = int(lags[np.argmax(corr)])
    assert similarity > .98 and abs(lag_ms) <= 2
    boxes = atoms(VIDEO)
    assert boxes.index("moov") < boxes.index("mdat")
    # Inspect every decoded frame for unexpected blank stretches, save samples.
    capture = cv2.VideoCapture(str(VIDEO), cv2.CAP_FFMPEG, [cv2.CAP_PROP_N_THREADS, 3])
    blank_inside, frame_count = [], 0
    sample_times = [round((s["start"]+s["end"])/2,3) for s in config["shots"]]
    sample_frames = {round(t*24): t for t in sample_times}
    contact = np.zeros((6*225,4*400,3),dtype=np.uint8)
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        t = frame_count/24
        if 1.5 < t < 207.8 and np.max(frame) < 8:
            blank_inside.append(frame_count)
        if frame_count in sample_frames:
            position = sample_times.index(sample_frames[frame_count])
            row,col=divmod(position,4)
            contact[row*225:(row+1)*225,col*400:(col+1)*400] = cv2.resize(frame,(400,225))
        frame_count += 1
    capture.release()
    assert frame_count == 5040 and not blank_inside
    cv2.imwrite(str(ROOT/"docs/export-frames.jpg"),contact,[cv2.IMWRITE_JPEG_QUALITY,92])
    result = {"status":"passed", "video":str(VIDEO), "sha256":sha256(VIDEO),
              "bytes":VIDEO.stat().st_size, "duration":float(info["format"]["duration"]),
              "width":1920,"height":1080,"fps":24,"frames_decoded":frame_count,
              "video_codec":"h264","pixel_format":"yuv420p","audio_codec":"aac",
              "audio_channels":2,"audio_sample_rate":48000,
              "full_decode_errors":0,"unexpected_blank_frames":blank_inside,
              "music_correlation_with_master":similarity,"music_offset_ms":lag_ms,
              "original_wav_unchanged":True,"all_original_artwork_hashes_match":True,
              "faststart":True,"below_github_100_mib_limit":True,
              "asr_used":False,"unique_artworks":24,"reused_artworks":0,"named_credits":False,"scope":"Full song, 210 s; technical verification and sampled visual inspection, no claim of word-level alignment."}
    (ROOT/"docs/validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    sums=[]
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.name != "SHA256SUMS.txt":
            sums.append(f"{sha256(path)}  {path.relative_to(ROOT)}")
    (ROOT/"SHA256SUMS.txt").write_text("\n".join(sums)+"\n")
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)


if __name__ == "__main__":
    main()

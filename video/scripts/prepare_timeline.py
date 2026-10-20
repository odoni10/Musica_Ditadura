"""Analyze the existing master; build editorial cues, never synthesize audio."""
from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, stft

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT.parent / "final/O_Peso_da_Minha_Mao.wav"

# Times describe visual narrative, not claimed word/verse alignment.
# Camera = normalized source center x/y, magnification.
SHOTS = [
    (0, "room", "A casa dividida", [.50, .50, 1.02], [.49, .48, 1.11]),
    (11, "room", "A luz que ocupa a mesa", [.32, .44, 1.55], [.30, .47, 1.70]),
    (20, "window", "O desejo de respirar", [.50, .50, 1.02], [.47, .49, 1.10]),
    (30, "room", "O pão esquecido", [.46, .57, 1.65], [.44, .57, 1.82]),
    (38, "window", "Um mundo além da tela", [.58, .45, 1.28], [.63, .46, 1.38]),
    (46, "hand", "O peso da escolha", [.50, .50, 1.02], [.52, .46, 1.17]),
    (57, "hand", "Um papel, uma consequência", [.51, .46, 1.42], [.53, .45, 1.64]),
    (67, "flood", "A promessa encontra a rua", [.50, .50, 1.02], [.52, .49, 1.12]),
    (79, "flood", "A ponte que não chega", [.66, .43, 1.45], [.68, .42, 1.58]),
    (89, "friends", "O espaço entre dois amigos", [.50, .50, 1.02], [.50, .49, 1.08]),
    (100, "friends", "A mão sem resposta", [.30, .46, 1.62], [.31, .43, 1.78]),
    (109, "hand", "A consciência permanece", [.52, .46, 1.45], [.50, .49, 1.12]),
    (121, "room", "Uma ausência à mesa", [.50, .56, 1.16], [.51, .54, 1.04]),
    (132, "reading", "Desligar e conferir", [.50, .50, 1.02], [.52, .51, 1.12]),
    (144, "reading", "A pergunta continua", [.59, .47, 1.40], [.57, .45, 1.57]),
    (154, "window", "Escutar de novo", [.47, .49, 1.12], [.49, .50, 1.03]),
    (164, "friends", "O outro ainda está aqui", [.50, .48, 1.12], [.50, .50, 1.02]),
    (176, "hand", "Escolher sem entregar o juízo", [.51, .46, 1.24], [.50, .50, 1.04]),
    (188, "reunion", "O gesto pequeno", [.50, .50, 1.02], [.49, .48, 1.12]),
    (199, "reunion", "O pão entre as mãos", [.48, .48, 1.47], [.48, .48, 1.65]),
    (206, "reunion", "A casa pode respirar", [.50, .49, 1.08], [.50, .50, 1.02]),
]


def main():
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(MASTER), "-f", "f32le",
        "-ac", "1", "-ar", "8000", "pipe:1",
    ])
    audio = np.frombuffer(raw, dtype="<f4")
    duration = len(audio) / 8000
    rms = np.sqrt(np.mean(audio[:len(audio)//400*400].reshape(-1, 400)**2, axis=1))
    rms = gaussian_filter1d(rms, 4)
    low, high = np.percentile(rms, [10, 95])
    energy = np.clip((rms-low) / max(high-low, 1e-8), 0, 1)
    _, times, spectrum = stft(audio, fs=8000, nperseg=512, noverlap=256)
    magnitude = np.log1p(30 * np.abs(spectrum))
    flux = np.maximum(np.diff(magnitude, axis=1), 0).mean(axis=0)
    peaks, _ = find_peaks(flux, distance=12, prominence=np.std(flux)*.25)
    attack_times = times[1:][peaks]
    fps = 24
    cues = []
    for i, (target, asset, narrative, camera0, camera1) in enumerate(SHOTS):
        nearby = attack_times[np.abs(attack_times-target) <= .75]
        cut = float(nearby[np.argmin(np.abs(nearby-target))]) if len(nearby) and i else target
        frame = round(cut*fps)
        cues.append({"start_frame": frame, "start": frame/fps, "asset": asset,
                     "narrative": narrative, "camera_start": camera0,
                     "camera_end": camera1, "transition_seconds": .8 if i else 0})
    for i, cue in enumerate(cues):
        cue["end_frame"] = cues[i+1]["start_frame"] if i+1 < len(cues) else round(duration*fps)
        cue["end"] = cue["end_frame"]/fps
    config = {"title": "O Peso da Minha Mão", "version": "videoclipe-v1",
              "audio": "../final/O_Peso_da_Minha_Mao.wav",
              "audio_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
              "duration": duration, "fps": fps, "width": 1920, "height": 1080,
              "seed": 190102126, "shots": cues,
              "sync_method": "Cortes próximos a ataques reais do áudio (janela ±0,75 s); luz e atmosfera seguem RMS suavizado. Arco visual inspirado na letra, sem alinhamento palavra a palavra ou ASR.",
              "audio_processing": "Master integral, sem mudança de velocidade, cortes, normalização ou remix; codificação AAC 256 kbps.",
              "render": {"codec": "libx264", "preset": "fast", "crf": 21,
                         "maxrate": "3200k", "bufsize": "6400k", "pixel_format": "yuv420p"}}
    (ROOT/"config/timeline.json").write_text(json.dumps(config, ensure_ascii=False, indent=2)+"\n")
    (ROOT/"config/audio-features.json").write_text(json.dumps({
        "sample_interval": .05, "energy": np.round(energy, 5).tolist(),
        "attack_times": np.round(attack_times, 4).tolist(),
        "purpose": "Sincronização editorial; não constitui avaliação da letra cantada."
    }, ensure_ascii=False)+"\n")
    print(f"Prepared {len(cues)} shots for {duration:.3f}s; original audio preserved.")


if __name__ == "__main__":
    main()

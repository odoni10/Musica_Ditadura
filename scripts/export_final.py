"""Export a completed lossless render, preserving dynamics and recording checks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import soundfile as sf


def inspect(path: Path) -> dict:
    """Measure decoded waveform without speech-recognition requirements."""
    frames = 0
    energy = 0.0
    peak = 0.0
    silent_seconds = 0
    with sf.SoundFile(path) as source:
        rate, channels = source.samplerate, source.channels
        for block in source.blocks(blocksize=rate, dtype='float32', always_2d=True):
            if not np.isfinite(block).all():
                raise ValueError('Nonfinite audio samples')
            peak = max(peak, float(np.max(np.abs(block))))
            energy += float(np.sum(block.astype('float64') ** 2))
            frames += len(block)
            silent_seconds += bool(np.max(np.abs(block)) < 0.0001)
    if peak < 0.001:
        raise ValueError('Silent audio')
    return {'duration_seconds': frames / rate, 'sample_rate': rate,
            'channels': channels, 'peak_dbfs': float(20 * np.log10(peak)),
            'rms_dbfs': float(10 * np.log10(energy / (frames * channels))),
            'blocks_below_minus80_dbfs': silent_seconds}


def export(source: Path, output: Path) -> dict:
    """Apply only fixed peak alignment, short edge fades and format conversion."""
    measured = inspect(source)
    output.mkdir(parents=True, exist_ok=True)
    duration = measured['duration_seconds']
    gain = -1.5 - measured['peak_dbfs']
    filters = (f'volume={gain:.6f}dB,afade=t=in:st=0:d=0.015,'
               f'afade=t=out:st={max(0, duration - 0.35):.6f}:d=0.35')
    wav = output / 'O_Peso_da_Minha_Mao.wav'
    mp3 = output / 'O_Peso_da_Minha_Mao.mp3'
    common = ['ffmpeg', '-nostdin', '-y', '-v', 'error', '-i']
    subprocess.run(common + [str(source), '-af', filters, '-c:a', 'pcm_s24le',
                             '-metadata', 'title=O Peso da Minha Mão', str(wav)], check=True)
    subprocess.run(common + [str(wav), '-c:a', 'libmp3lame', '-b:a', '320k',
                             '-id3v2_version', '3', '-metadata',
                             'title=O Peso da Minha Mão', str(mp3)], check=True)
    report = {'source': str(source), 'source_measurements': measured,
              'fixed_gain_db': gain, 'filters': filters, 'wav': str(wav),
              'mp3': str(mp3), 'wav_measurements': inspect(wav),
              'processing': 'Fixed gain, 15 ms initial fade, 350 ms final fade; no compression/EQ/time stretching.',
              'asr_required': False, 'auditory_evaluation': False, 'files': []}
    for path in (wav, mp3):
        probe = json.loads(subprocess.check_output(
            ['ffprobe', '-v', 'error', '-show_format', '-show_streams',
             '-of', 'json', str(path)], text=True))
        report['files'].append({'name': path.name, 'bytes': path.stat().st_size,
                                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                'ffprobe': probe})
    (output / 'export-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'final')
    args = parser.parse_args()
    result = export(args.source, args.output)
    print(json.dumps({k: result[k] for k in ('wav', 'mp3', 'wav_measurements')}, ensure_ascii=False))

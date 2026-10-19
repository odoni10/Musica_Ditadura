"""Measure user-provided references locally; do not copy their audio to Git."""
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy import fft, signal

RATE = 11025
ROOT = Path('/workspace/music-reference/v2')


def decode(path):
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(path),
                                    '-ac', '1', '-ar', str(RATE), '-f', 'f32le', '-'])
    return np.frombuffer(data, dtype='<f4').copy()


def db(value):
    return float(20 * np.log10(max(float(value), 1e-12)))


def describe(y):
    count = len(y) // RATE
    blocks = y[:count * RATE].reshape(count, RATE)
    rms = np.sqrt(np.mean(blocks.astype('float64') ** 2, axis=1))
    f, _, z = signal.stft(y, RATE, nperseg=2048, noverlap=1024)
    power = np.abs(z) ** 2
    spectrum = power.sum(axis=1)
    centroid = float(np.sum(f * spectrum) / np.sum(spectrum))
    bands = {}
    for low, high in [(20, 200), (200, 2000), (2000, 5000)]:
        bands[f'{low}-{high}Hz'] = float(spectrum[(f >= low) & (f < high)].sum() / spectrum.sum())
    return {'duration': len(y) / RATE, 'peak_dbfs': db(np.max(np.abs(y))),
            'rms_dbfs': db(np.sqrt(np.mean(y.astype('float64') ** 2))),
            'one_second_rms_percentiles_dbfs': [db(x) for x in np.percentile(rms, [10, 50, 90])],
            'ten_second_rms_dbfs': [db(np.sqrt(np.mean(y[i:i + RATE * 10].astype('float64') ** 2)))
                                     for i in range(0, len(y), RATE * 10)],
            'spectral_centroid_hz': centroid, 'energy_bands': bands}


def tempos(y):
    _, _, z = signal.stft(y, RATE, nperseg=1024, noverlap=804)
    flux = np.maximum(0, np.diff(np.abs(z), axis=1)).sum(axis=0)
    flux = np.maximum(0, flux - signal.medfilt(flux, 25))
    ac = signal.fftconvolve(flux, flux[::-1], mode='full')[len(flux) - 1:]
    fps = RATE / 220
    lags = np.arange(int(fps * 60 / 165), int(fps * 60 / 50))
    candidates, _ = signal.find_peaks(ac[lags])
    candidates = sorted(candidates, key=lambda i: ac[lags[i]], reverse=True)[:5]
    return [{'bpm': float(60 * fps / lags[i]), 'relative_ac': float(ac[lags[i]] / ac[0])}
            for i in candidates]


def pitch_summary(y):
    filtered = signal.sosfilt(signal.butter(3, [65, 900], fs=RATE, btype='bandpass', output='sos'), y)
    frames = np.lib.stride_tricks.sliding_window_view(filtered, 1024)[::220]
    values = []
    for start in range(0, len(frames), 512):
        block = frames[start:start + 512].copy()
        level = np.sqrt(np.mean(block ** 2, axis=1))
        block -= block.mean(axis=1, keepdims=True)
        spectra = fft.rfft(block, n=2048, axis=1)
        ac = fft.irfft(spectra * spectra.conj(), n=2048, axis=1)[:, :1024]
        lo, hi = int(RATE / 350), int(RATE / 70)
        lag = np.argmax(ac[:, lo:hi], axis=1) + lo
        strength = ac[np.arange(len(ac)), lag] / np.maximum(ac[:, 0], 1e-12)
        valid = (strength > 0.65) & (level > 0.008)
        values.extend((RATE / lag[valid]).tolist())
    return {'f0_percentiles_hz': np.percentile(values, [10, 50, 90]).tolist() if values else [],
            'voiced_frames': len(values), 'limitation': 'Rough autocorrelation estimate on separated vocals; octave errors and overlapping voices possible. No identity inference.'}


def tonal_summary(y):
    f, _, z = signal.stft(y, RATE, nperseg=8192, noverlap=4096)
    valid = (f >= 65) & (f < 1600)
    midi = np.rint(69 + 12 * np.log2(f[valid] / 440)).astype(int)
    chroma = np.bincount(midi % 12, weights=(np.abs(z[valid]) ** 2).sum(axis=1), minlength=12)
    chroma /= chroma.sum()
    major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    scores = [(float(np.corrcoef(chroma, np.roll(profile, shift))[0, 1]), names[shift] + ' ' + mode)
              for profile, mode in [(major, 'major'), (minor, 'minor')] for shift in range(12)]
    return {'pitch_class_energy': dict(zip(names, chroma.tolist())),
            'profile_candidates': sorted(scores, reverse=True)[:4],
            'limitation': 'Spectral harmonic-profile estimate, not chord transcription or a confirmed key.'}


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    report = {'method': 'Local signal analysis only; no auditory evaluation, ASR, source-audio conditioning or voice cloning.', 'sources': []}
    for item in manifest:
        y = decode(Path(item['path']))
        row = {**item, 'measurements': describe(y)}
        if item['label'] in ['mix', 'drums', 'bass']:
            row['tempo_candidates'] = tempos(y)
        if item['label'] == 'vocals':
            row['pitch'] = pitch_summary(y)
        if item['label'] == 'other':
            row['tonality'] = tonal_summary(y)
        if item['label'] == 'metronome':
            smooth = np.convolve(np.abs(y), np.ones(100) / 100, mode='same')
            peaks, _ = signal.find_peaks(smooth, distance=int(RATE * 0.3), prominence=float(smooth.max() * 0.3))
            row['click_bpm'] = float(60 * RATE / np.median(np.diff(peaks)))
            row['clicks'] = len(peaks)
        report['sources'].append(row)
        print(item['label'], json.dumps({k: v for k, v in row.items() if k not in ['measurements', 'path']}), flush=True)
    (ROOT / 'analysis.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()

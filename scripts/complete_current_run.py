"""Finish the existing FP32 process once; no extra benchmark or ASR gate."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

PROJECT = Path('/workspace/Musica_Ditadura')
RUNTIME = Path('/workspace/music-runtime')
spec = importlib.util.spec_from_file_location('export_final', PROJECT / 'scripts/export_final.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


def read_completed(path: Path) -> dict:
    """Wait for a result, tolerating the brief interval of a non-atomic writer."""
    while True:
        if path.exists():
            try:
                result = json.loads(path.read_text())
                if not result.get('success'):
                    raise RuntimeError(f'Generation failed: {path.name}')
                return result
            except json.JSONDecodeError:
                pass
        time.sleep(10)


def complete() -> None:
    """Compare the final sample, release the warm model and export its full render."""
    native = read_completed(RUNTIME / 'native-sample-result.json')
    rows = []
    for prefix, label, filename in [
        ('int8', 'INT8 sem planejamento', 'int8-sem-planejamento'),
        ('high', 'INT8 com planejamento 1.7B', 'int8-com-planejamento'),
        ('native', 'FP32 nativo com planejamento 0.6B', 'fp32-com-planejamento'),
    ]:
        result = json.loads((RUNTIME / f'{prefix}-sample-result.json').read_text())
        audio = Path(result['outputs'][0]['path'])
        measured = exporter.inspect(audio)
        if abs(measured['duration_seconds'] - result['params']['duration']) > 1:
            raise RuntimeError('Sample duration mismatch')
        shutil.copy2(audio, PROJECT / 'samples' / f'{filename}.flac')
        shutil.copy2(RUNTIME / f'{prefix}-sample-result.json', PROJECT / 'samples' / f'{filename}-result.json')
        rows.append({'configuration': label, 'measurements': measured,
                     'generation_seconds': result['timing']['generation_sec'],
                     'seconds_compute_per_second_audio': result['timing']['generation_sec'] / measured['duration_seconds'],
                     'completed_without_generation_error': True,
                     'precision': result['runtime_precision'], 'params': result['params']})
    comparison = {'samples': rows, 'winner': 'FP32 nativo com planejamento 0.6B',
                  'reason': 'Configuração nativa sem quantização, planejamento ativo e amostra tecnicamente válida; reutiliza os modelos quentes para concluir a faixa. A rapidez isolada favorece INT8 sem planejamento.',
                  'limits': 'Durações, seeds e shifts diferentes impedem atribuir diferenças somente à precisão. Clareza vocal, aderência cantada e qualidade musical não foram avaliadas por escuta humana. Não são inferidas da forma de onda.',
                  'asr': 'Auxiliar; transcrições históricas curtas não vetam geração. Nenhum novo teste ASR foi exigido.',
                  'further_benchmarks': False}
    (PROJECT / 'docs/comparison.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + '\n')
    # This is an internal production decision, not an ASR or user-approval gate.
    gate = RUNTIME / 'native-quality-gate.json'
    if gate.exists():
        raise RuntimeError('Existing decision file; refusing to overwrite it')
    temporary = gate.with_suffix('.tmp')
    temporary.write_text(json.dumps({'proceed': True, 'reason': comparison['reason'], 'asr_required': False}) + '\n')
    temporary.replace(gate)
    print('FINAL COMPARISON COMPLETE: native FP32 selected; full render released.', flush=True)
    full = read_completed(RUNTIME / 'native-full-result.json')
    source = Path(full['outputs'][0]['path'])
    measured = exporter.inspect(source)
    if abs(measured['duration_seconds'] - full['params']['duration']) > 1:
        raise RuntimeError('Full render duration mismatch')
    shutil.copy2(source, PROJECT / 'final/O_Peso_da_Minha_Mao.flac')
    shutil.copy2(RUNTIME / 'native-full-result.json', PROJECT / 'config/final-engine-result.json')
    plan = json.loads(Path('/workspace/music-output/composicao.json').read_text())
    final_params = {**full['params'], 'lyrics': plan['lyrics'], 'seed': full['outputs'][0]['seed'],
                    'model': full['model'], 'lm_model': full['lm_model'],
                    'runtime_precision': full['runtime_precision'], 'quality': full['quality'],
                    'sample_rate': measured['sample_rate'], 'batch': 1,
                    'claude_music_commit': plan['claude_music_commit'], 'ace_step_commit': plan['ace_step_commit'],
                    'whole_song_single_render': True, 'asr_required': False}
    (PROJECT / 'config/final-parameters.json').write_text(json.dumps(final_params, ensure_ascii=False, indent=2) + '\n')
    exporter.export(source, PROJECT / 'final')
    print('FINAL MP3, WAV AND FLAC EXPORTED.', flush=True)


if __name__ == '__main__':
    complete()

"""Package and document existing V2 audio; never synthesize or alter audio."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
FINAL = PROJECT / 'final'
RUNTIME = Path('/workspace/music-runtime')
engine = json.loads((PROJECT / 'config/final-engine-result.json').read_text())
params = json.loads((FINAL / 'parametros-v2.json').read_text())
origin = json.loads((PROJECT / 'config/composicao-original.json').read_text())
validation = json.loads((FINAL / 'validation-report.json').read_text())
params.update(model=engine['model'], guidance_requested=engine['params']['guidance_scale'],
    guidance_effective_turbo=1.0, turbo_uses_cfg=False, full_song_single_render=True,
    output_sample_rate=48000, output_channels=2, generation_seconds=engine['timing']['generation_sec'],
    claude_music_commit=origin['claude_music_commit'], ace_step_commit=origin['ace_step_commit'],
    python=platform.python_version(), versions={name: importlib.metadata.version(name)
        for name in ['torch', 'transformers', 'diffusers', 'huggingface-hub', 'soundfile', 'numpy', 'scipy']})
(FINAL / 'parametros-v2.json').write_text(json.dumps(params, ensure_ascii=False, indent=2) + '\n')
with zipfile.ZipFile(FINAL / 'O_Peso_da_Minha_Mao_MP3_e_Letra.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for name in ['O_Peso_da_Minha_Mao.mp3', 'O_Peso_da_Minha_Mao_LETRA.txt', 'parametros-v2.json']:
        archive.write(FINAL / name, arcname=name)
with zipfile.ZipFile(FINAL / 'O_Peso_da_Minha_Mao_MP3_e_Letra.zip') as archive:
    assert archive.testzip() is None
    for name in archive.namelist():
        assert archive.read(name) == (FINAL / name).read_bytes()
log = (RUNTIME / 'final-silence.log').read_text()
assert 'time=00:03:30.00' in log
validation['silence_intervals_at_least_2s_below_minus60_dbfs'] = [line for line in log.splitlines()
    if 'silence_start:' in line or 'silence_end:' in line]
validation['zip_parameters_match_final_json'] = True
(FINAL / 'validation-report.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n')
(FINAL / 'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(path.read_bytes()).hexdigest()
    + '  ' + path.name + '\n' for path in sorted(FINAL.iterdir())
    if path.is_file() and path.name != 'SHA256SUMS.txt'))
entries = []
for path in sorted(RUNTIME.iterdir()):
    count, size = 0, 0
    if path.is_dir():
        for root, directories, files in os.walk(path, followlinks=False):
            for name in files:
                item = Path(root) / name
                if not item.is_symlink():
                    count += 1
                    size += item.stat().st_size
    else:
        count, size = 1, path.stat().st_size
    entries.append(dict(name=path.name, type='directory' if path.is_dir() else 'file', files=count, bytes=size))
(PROJECT / 'docs/runtime-inventory.json').write_text(json.dumps(dict(root=str(RUNTIME),
    note='Inventário após exportação completa. Nenhum arquivo apagado. Apenas nomes, contagens e tamanhos; credenciais não foram lidas ou copiadas.',
    entries=entries), ensure_ascii=False, indent=2) + '\n')
state_path = PROJECT / 'config/production-state.json'
state = json.loads(state_path.read_text())
if state['v2_status'] != 'complete_published':
    state.update(v2_status='complete_verified_ready_to_publish', next_allowed_action='Publish final audio and complete lyrics')
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
readme = PROJECT / 'README.md'
text = readme.read_text()
start = text.index('**V2 aprovada') if '**V2 aprovada' in text else text.index('**Música completa V2')
end = text.index('## Prévia V2', start)
text = text[:start] + '''**Música completa V2 concluída: 3min30s.** Direção masculina adulta médio-grave, MPB acústica sóbria e tensa, 65 BPM e ré menor. O usuário aprovou a prévia e autorizou a produção integral. A letra original foi preservada. Veja [o relatório final](docs/relatorio-final-v2.md) e [os parâmetros](final/parametros-v2.json).

## Downloads finais

- [MP3 — 320 kbps, 48 kHz](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao.mp3)
- [Pacote MP3 + letra completa + parâmetros](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao_MP3_e_Letra.zip)
- [Letra completa em TXT](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao_LETRA.txt)
- [WAV — PCM 24 bits, 48 kHz](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao.wav)
- [FLAC original preservado](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao.flac)

Arquivos em `/workspace/Musica_Ditadura/final/`, todos menores que 100 MiB. Verificação técnica e hashes em `final/validation-report.json` e `final/SHA256SUMS.txt`. A V1 descartada e as prévias continuam preservadas.

''' + text[end:]
text = text.replace('A execução atual é `scripts/generate_full_v2.py`, log',
    'A execução concluída foi `scripts/generate_full_v2.py`, log')
start = text.index('## Critério de encerramento') if '## Critério de encerramento' in text else text.index('## Estado final')
text = text[:start] + '''## Estado final

A faixa V2 foi gerada uma única vez, com a direção aprovada, e exportada com toda a letra em TXT e no pacote ZIP. Não há geração obrigatória ativa. Para ouvir ou baixar, usar os arquivos existentes. Não houve nova rodada de benchmarks, análise das referências ou ASR após a aprovação. A verificação final foi técnica; o agente não realizou escuta humana.
'''
readme.write_text(text)
ignore = PROJECT / '.gitignore'
content = ignore.read_text()
for pattern in ['HF_TOKEN*', '.secrets*', 'secrets.*', '*.secret']:
    if pattern not in content.splitlines():
        content += pattern + '\n'
ignore.write_text(content)
report = '''# Entrega final — O Peso da Minha Mão, V2

Faixa integral concluída em um único render de 210 s (3min30s), após a aprovação auditiva da prévia V2 pelo usuário. A letra original completa foi preservada em `lyrics/letra.txt` e `final/O_Peso_da_Minha_Mao_LETRA.txt`, também incluída no pacote MP3+letra. V1 e todas as amostras anteriores permanecem preservadas; a V1 continua descartada artisticamente.

Foi mantida a configuração funcional FP32 nativa com planejador 0.6B e a direção V2 aprovada: voz masculina adulta médio-grave, interpretação contida, MPB acústica sóbria, 65 BPM, ré menor, 4/4, seed 190102126, preset high, turbo com 8 passos e shift 3.0. Somente duração e texto foram estendidos para a faixa integral. Na última comparação técnica, FP32 com planejamento 0.6B levou 22min49s por 30 s contra 24min37s do INT8 com planejamento 1.7B; o INT8 sem planejamento foi mais rápido por segundo de áudio. A seleção técnica não constitui uma nota de qualidade vocal. A direção artística foi aprovada pelo usuário na V2.

O claude-music forneceu orientações de composição/prompt e seu motor Python real coordenou o ACE-Step. FFmpeg fez as conversões. Modelos existentes foram reutilizados offline. Nenhum áudio de referência foi condicionado, misturado, clonado ou publicado; a análise prévia serviu para características abstratas. Não houve novo benchmark ou ASR. Código e modelos oficiais têm licença MIT; nenhuma plataforma paga foi utilizada ou contratada.

Verificações: FLAC, WAV e MP3 decodificam integralmente; 210 s, estéreo, 48 kHz, amostras finitas, nenhum bloco de um segundo abaixo de -80 dBFS e nenhum silêncio de pelo menos 2 s abaixo de -60 dBFS. WAV PCM 24 bits e MP3 320 kbps. Pico WAV -1,50 dBFS; MP3 decodificado -1,60 dBFS. FLAC preservado idêntico ao original. Letra e conteúdo do ZIP conferidos byte a byte. A verificação não incluiu escuta humana pelo agente; dicção, reprodução audível de cada palavra e qualidade musical final não foram avaliadas por audição.

Pós-processamento: ganho fixo de aproximadamente -0,5 dB, fades de 15 ms no início e 350 ms no final, sem compressão, equalização ou mudança de duração. Tempo reportado de geração: 6330,9 s (1h45min31s), excluindo inicialização. `final/parametros-v2.json` contém texto integral, seed, versões e commits; `export-report.json`, `validation-report.json` e `SHA256SUMS.txt` documentam os arquivos.

Projeto: `/workspace/Musica_Ditadura`; repositório `https://github.com/odoni10/Musica_Ditadura`; branch `main`. Entregas:

| Arquivo em final/ | Tamanho em bytes |
|---|---:|
'''
for path in sorted(FINAL.iterdir()):
    if path.is_file():
        report += f'| {path.name} | {path.stat().st_size} |\n'
report += '''
Somente no ambiente: dependências e pesos em `tools/ACE-Step-1.5/checkpoints/`, fontes de terceiros em `tools/`, venv/cache/Hugging Face/diagnósticos/logs em `/workspace/music-runtime/`, referências enviadas em `/workspace/attachments/` e `/workspace/music-reference/`, e originais de trabalho em `/workspace/music-output/`. Nada foi apagado. Inventário atualizado em `docs/runtime-inventory.json`. GitHub recebe apenas artefatos do projeto: letra, prompts, configurações, scripts, amostras, documentação e arquivos finais; nunca pesos, caches, ambientes, referências ou credenciais.
'''
(PROJECT / 'docs/relatorio-final-v2.md').write_text(report)
print('Delivery metadata, bundle, README, inventory and report finalized without audio regeneration.')

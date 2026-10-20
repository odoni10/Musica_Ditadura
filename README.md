# O Peso da Minha Mão

Canção original em português brasileiro. A letra em [lyrics/letra.txt](lyrics/letra.txt) está preservada.

**Música completa V2 concluída: 3min30s.** Direção masculina adulta médio-grave, MPB acústica sóbria e tensa, 65 BPM e ré menor. O usuário aprovou a prévia e autorizou a produção integral. A letra original foi preservada. Veja [o relatório final](docs/relatorio-final-v2.md) e [os parâmetros](final/parametros-v2.json).

## Downloads finais

- [Videoclipe V2 — 24 cenas distintas, MP4, Full HD, 3min30s](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/video-v2/output/O_Peso_da_Minha_Mao_Videoclipe_V2.mp4) · [Projeto da revisão](video-v2/README.md)
- [Primeiro videoclipe preservado](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/video/output/O_Peso_da_Minha_Mao_Videoclipe.mp4) · [Projeto V1](video/README.md)

- [MP3 — 320 kbps, 48 kHz](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao.mp3)
- [Pacote MP3 + letra completa + parâmetros](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao_MP3_e_Letra.zip)
- [Letra completa em TXT](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao_LETRA.txt)
- [WAV — PCM 24 bits, 48 kHz](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao.wav)
- [FLAC original preservado](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/final/O_Peso_da_Minha_Mao.flac)

Arquivos em `/workspace/Musica_Ditadura/final/`, todos menores que 100 MiB. Verificação técnica e hashes em `final/validation-report.json` e `final/SHA256SUMS.txt`. A V1 descartada e as prévias continuam preservadas.

## Prévia V2 aprovada

[Ouvir ou baixar MP3 da V2 — 30 segundos](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/music/samples/mpb-masculina-v2-preview-30s.mp3). MP3 estéreo, 48 kHz, 320 kbps. [FLAC original preservado](samples/mpb-masculina-v2-preview-30s.flac). O runner da prévia terminou após esses 30 s. A faixa integral foi produzida depois da aprovação do usuário. O resultado existente foi recuperado sem nova geração ou mudança de configuração. O usuário aprovou essa direção e autorizou a faixa completa.

**Histórico: V1 descartada por direção artística.** A geração integral anterior foi cancelada e a automação de finalização encerrada. Áudios, scripts, resultados e commits anteriores foram preservados como referência técnica. A prévia antiga com voz feminina não é uma base aprovada para a música final.

As referências enviadas ficam somente em `/workspace/attachments/` e `/workspace/music-reference/v2/`. Não são enviadas ao GitHub nem passadas ao gerador como cover, amostra, clonagem ou continuação de áudio. Servem para extrair características abstratas. `musica.zip` excedeu o limite de transferência de 32 MiB; a análise usa o MP3 combinado e os cinco stems presentes em `vozes.zip`.

Prévia V1 descartada, preservada apenas para histórico: [MP3 antigo](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/music/samples/fp32-preview-30s.mp3).

## Ferramentas e modelos

**claude-music** é o projeto aberto de scripts e orientações que organiza composição, geração e exportação. Aqui usamos seu motor Python pelo Codex, sem instalar Claude Code. Não é um modelo musical nem um serviço contratado. Fonte: https://github.com/AgriciDaniel/claude-music, MIT, commit `5aa0173a6b329e059568bef4253e2a62efe8b412`.

**ACE-Step 1.5** é o modelo e motor de inferência que produz o áudio a partir da direção musical e da letra. Fonte: https://github.com/ace-step/ACE-Step-1.5, MIT, commit `ca1e85fe9430179831e6bc6be790c332190a3866`. Usamos o DiT turbo, codificador de texto, VAE e modelo de linguagem de planejamento. Os fontes das duas ferramentas permanecem em `tools/`, ignorados pelo Git; nenhuma alteração nos fontes rastreados dessas dependências foi necessária.

**Hugging Face** hospeda os pesos e tokenizadores oficiais. Os aproximadamente 10 GB iniciais correspondem aos componentes do ACE-Step: DiT (~4,79 GB), codificador (~1,19 GB), VAE (~0,34 GB) e planejador 1.7B (~3,71 GB), além dos tokenizadores. Foi também obtido o planejador oficial 0.6B (~1,36 GB) para o último teste FP32. Whisper base/small foram dependências auxiliares de diagnóstico de transcrição; transcrição não é requisito de liberação da faixa. Os manifestos públicos com revisões, tamanhos e SHA-256 estão em `config/`.

Pesos estão em `/workspace/Musica_Ditadura/tools/ACE-Step-1.5/checkpoints/`. O diretório completo ocupa mais espaço que os pesos publicados porque contém cache e downloads incompletos preservados. **Esses arquivos não pertencem ao Git e não são enviados ao GitHub.**

## Organização

- `lyrics/`: letra original utilizada, preservada.
- `prompts/`: direção musical enviada ao modelo.
- `config/`: composição inicial, dependências fixadas, parâmetros e manifestos públicos; nunca credenciais.
- `scripts/`: adaptadores, instalação e utilitários. `scripts/archive/` preserva experimentos anteriores apenas para histórico; não é uma fila de novos testes.
- `samples/`: amostras relevantes e medições da última comparação.
- `docs/`: relatório de produção e inventário do ambiente.
- `final/`: MP3 e WAV finais após conclusão.
- `video/`: videoclipe completo, sete ilustrações originais, timeline, scripts de animação, storyboard e documentação. A música V2 existente é a trilha integral.
- `video-v2/`: revisão visual com 24 imagens novas, usadas uma vez cada, pintura mais suave e maior variedade de ambientes e luz; sem créditos nominais.

`/workspace/music-runtime/` contém venv, cache de pacotes, cache Hugging Face/Whisper, scripts originais, logs de tentativas, requisições da API, arquivos de validação e um controle de ASR com fala sintética. Esse controle não é música nem parte da entrega. `docs/runtime-inventory.json` inventaria todas as entradas desse diretório durante a produção. Nada foi apagado; scripts, manifestos e amostras úteis foram copiados antes da organização. `/workspace/music-output/` preserva a composição, letra e áudios brutos de trabalho. Diretórios vazios de tentativas interrompidas e logs são temporários.

## Execução no ambiente preparado

Python: `/workspace/music-runtime/venv/bin/python`; CPU, 32 GiB, sem GPU. Reutilizar pesos existentes. A prévia foi concluída e aprovada. A execução concluída foi `scripts/generate_full_v2.py`, log `/workspace/music-runtime/full-v2-production.log` e resultado `/workspace/music-runtime/artistic-v2-full-result.json`. O script gera uma única faixa integral e exporta MP3/WAV/FLAC, letra completa e pacote ZIP. Conferir processos/resultados antes de agir; recuperar arquivos existentes em vez de duplicar a geração. Os runners V1 permanecem bloqueados.

Para restaurar uma instalação ausente, `bash scripts/install.sh` prepara as dependências CPU e verifica a presença dos pesos antes de baixar algo. O instalador não é necessário para ouvir ou baixar a entrega existente. Os scripts usam os caminhos deste ambiente em `/workspace`. As 55 verificações existentes de claude-music passaram durante a instalação.

O Space público do Hugging Face foi tentado como alternativa gratuita, mas retornou erro de tarefa GPU e depois quota anônima esgotada; nenhum áudio remoto foi obtido. A produção continua local. Não há serviço pago nem credencial necessária para executar os modelos públicos já presentes. Se autenticação opcional for utilizada no futuro, forneça `HF_TOKEN` apenas pelo armazenamento seguro do ambiente, nunca em arquivos do projeto.

## Estado final

A faixa V2 foi gerada uma única vez, com a direção aprovada, e exportada com toda a letra em TXT e no pacote ZIP. Não há geração obrigatória ativa. Para ouvir ou baixar, usar os arquivos existentes. Não houve nova rodada de benchmarks, análise das referências ou ASR após a aprovação. A verificação final foi técnica; o agente não realizou escuta humana.

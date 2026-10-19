# O Peso da Minha Mão

Canção original em português brasileiro. A letra em [lyrics/letra.txt](lyrics/letra.txt) está preservada.

**Estado atual: V1 descartada por direção artística.** A geração integral anterior foi cancelada e a automação de finalização encerrada. Áudios, scripts, resultados e commits anteriores foram preservados como referência técnica. A prévia antiga com voz feminina não é uma base aprovada para a música final.

**V2 aprovada pelo usuário; faixa integral em produção.** Direção masculina adulta médio-grave, MPB acústica sóbria e tensa, 65 BPM e ré menor. A prévia aprovada está preservada. A produção integral usa a mesma direção, seed e parâmetros funcionais, com a letra completa e alvo de 210 s (3min30s). Configuração em [config/full-v2.json](config/full-v2.json). Não há novos testes de modelos nem ASR como aprovação artística.

## Prévia V2 pronta para avaliação

[Ouvir ou baixar MP3 da V2 — 30 segundos](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/music/samples/mpb-masculina-v2-preview-30s.mp3). MP3 estéreo, 48 kHz, 320 kbps. [FLAC original preservado](samples/mpb-masculina-v2-preview-30s.flac). A execução terminou após essa única prévia. Nenhuma faixa completa V2 foi iniciada. O resultado existente foi recuperado sem nova geração ou mudança de configuração. O usuário aprovou essa direção e autorizou a faixa completa.

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

`/workspace/music-runtime/` contém venv, cache de pacotes, cache Hugging Face/Whisper, scripts originais, logs de tentativas, requisições da API, arquivos de validação e um controle de ASR com fala sintética. Esse controle não é música nem parte da entrega. `docs/runtime-inventory.json` inventaria todas as entradas desse diretório durante a produção. Nada foi apagado; scripts, manifestos e amostras úteis foram copiados antes da organização. `/workspace/music-output/` preserva a composição, letra e áudios brutos de trabalho. Diretórios vazios de tentativas interrompidas e logs são temporários.

## Execução no ambiente preparado

Python: `/workspace/music-runtime/venv/bin/python`; CPU, 32 GiB, sem GPU. Reutilizar pesos existentes. A prévia foi concluída e aprovada. A execução atual é `scripts/generate_full_v2.py`, log `/workspace/music-runtime/full-v2-production.log` e resultado `/workspace/music-runtime/artistic-v2-full-result.json`. O script gera uma única faixa integral e exporta MP3/WAV/FLAC, letra completa e pacote ZIP. Conferir processos/resultados antes de agir; recuperar arquivos existentes em vez de duplicar a geração. Os runners V1 permanecem bloqueados.

Para restaurar uma instalação ausente, `bash scripts/install.sh` prepara as dependências CPU e verifica a presença dos pesos antes de baixar algo. O script não deve ser executado para reiniciar a produção atual. Os scripts usam os caminhos deste ambiente em `/workspace`. As 55 verificações existentes de claude-music passaram durante a instalação.

O Space público do Hugging Face foi tentado como alternativa gratuita, mas retornou erro de tarefa GPU e depois quota anônima esgotada; nenhum áudio remoto foi obtido. A produção continua local. Não há serviço pago nem credencial necessária para executar os modelos públicos já presentes. Se autenticação opcional for utilizada no futuro, forneça `HF_TOKEN` apenas pelo armazenamento seguro do ambiente, nunca em arquivos do projeto.

## Critério de encerramento

A direção V2 foi aprovada pelo usuário. Concluir a faixa integral e entregar áudio com a letra completa. A V1 permanece descartada. Não executar Whisper como critério artístico nem reabrir benchmarks de precisão. Não houve escuta humana feita pelo agente. A entrega final ficará em `final/` com MP3, WAV, FLAC original, letra TXT, parâmetros, medições e pacote MP3+letra.

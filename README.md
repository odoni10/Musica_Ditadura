# O Peso da Minha Mão

Projeto de uma canção original em português brasileiro, com direção de MPB de protesto, voz feminina sintética e acompanhamento acústico. Letra e estrutura estão em [lyrics/letra.txt](lyrics/letra.txt). A comparação final foi concluída: FP32 nativo com planejamento 0.6B foi selecionado. A faixa integral de 180 s está em geração; veja [o relatório](docs/relatorio.md). Os arquivos finais serão colocados em `final/` quando concluídos.

## Prévia disponível

[Baixar/ouvir a prévia FP32 de 30 s em MP3](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/music/samples/fp32-preview-30s.mp3). Cópia em `music/samples/fp32-preview-30s.mp3`, MP3 estéreo, 48 kHz, 320 kbps. Convertida da amostra já concluída; original FLAC preservado e SHA-256 conferido antes/depois. Nenhuma nova amostra foi gerada. A geração integral continua separadamente.

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

Python: `/workspace/music-runtime/venv/bin/python`; CPU, 32 GiB, sem GPU. Modelos existentes devem ser reutilizados. Não execute novamente a geração para apenas ouvir ou baixar os arquivos finais. A execução corrente é `/workspace/music-runtime/produce_native_cpu.py`, com log `native-production.log`. O processo mantém os modelos carregados entre a última amostra e a faixa integral. Um arquivo interno de decisão libera a geração integral após a comparação técnica; ASR não participa dessa condição.

Para restaurar uma instalação ausente, `bash scripts/install.sh` prepara as dependências CPU e verifica a presença dos pesos antes de baixar algo. O script não deve ser executado para reiniciar a produção atual. Os scripts usam os caminhos deste ambiente em `/workspace`. As 55 verificações existentes de claude-music passaram durante a instalação.

O Space público do Hugging Face foi tentado como alternativa gratuita, mas retornou erro de tarefa GPU e depois quota anônima esgotada; nenhum áudio remoto foi obtido. A produção continua local. Não há serviço pago nem credencial necessária para executar os modelos públicos já presentes. Se autenticação opcional for utilizada no futuro, forneça `HF_TOKEN` apenas pelo armazenamento seguro do ambiente, nunca em arquivos do projeto.

## Critério de encerramento

A comparação final inclui INT8 sem planejamento, INT8 com planejamento e FP32 nativo com planejador 0.6B. Têm durações, seeds e parâmetros diferentes, portanto não constituem um experimento controlado de precisão. Medições de onda, duração, estabilidade e tempo são objetivas; qualidade musical e dicção exigem escuta. Não houve escuta humana realizada pelo agente. Whisper é somente um indicador auxiliar e não bloqueia a geração integral. Não haverá novas rodadas de benchmarks após o teste FP32, salvo erro técnico grave.

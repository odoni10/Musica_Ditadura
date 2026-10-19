# Arquivos do ambiente e preservação

Revisão efetuada em `/workspace/music-runtime/`: inventário de todas as entradas em `runtime-inventory.json`, com número de arquivos e bytes por entrada. Diretórios percorridos sem seguir links simbólicos. Nenhum arquivo foi apagado. A contagem representa o instante da revisão, pois logs e resultados continuam sendo gravados durante a geração.

| Grupo | Local e destino |
|---|---|
| Modelos musicais | `tools/ACE-Step-1.5/checkpoints/`: DiT, Qwen, VAE, LM 1.7B e LM 0.6B. Apenas ambiente; ignorados. Manifestos copiados para `config/`. |
| Fontes de terceiros | `tools/claude-music/` e `tools/ACE-Step-1.5/`, incluindo seus `.git`. Apenas ambiente; não foram adicionados como submódulos. Commits públicos no README. |
| Python e pacotes | `music-runtime/venv/` e `music-runtime/cache/`: apenas ambiente. O venv utiliza pacotes também armazenados no cache, portanto não remova o cache enquanto estiver em uso. Versões fixadas em `config/cpu-inference-pinned.txt` e no instalador. |
| Whisper e cache HF | `music-runtime/huggingface/`: apenas ambiente, incluindo modelos ASR. Não é parte da música. Não copiar tokens do cache. |
| Downloads parciais | `music-runtime/download-parts/`, caches `.cache/huggingface/` dos checkpoints e arquivos incompletos: temporários preservados, nenhum novo download durante a continuação. |
| Scripts próprios | Originais em `music-runtime/`; cópias úteis em `scripts/`, com experimentos encerrados em `scripts/archive/`. Não reiniciar testes arquivados. |
| Logs, gates e diagnósticos | `*-production*.log`, `*-validation.log`, `*-quality-gate.json`, `test-result.json`, `installed.txt` e demais logs de download/ASR: apenas ambiente. Gates são decisões internas históricas, não requisitos do projeto. |
| Space público | `space-api.json`, `space-config.json`, `official-space-app.py`, requisições e logs remotos: referências temporárias da tentativa sem áudio. Proveniência pública copiada em `config/remote-provenance.json`. O código de referência não foi executado. |
| Controle de ASR | `asr-control.wav`, `asr-control-result.json` e log: fala sintética de diagnóstico, apenas ambiente. Não é trecho da música nem amostra relevante. |
| Amostras musicais | Originais em `music-output/teste_int8/`, `teste_high/`, `teste_native/`; cópias relevantes em `samples/`. Pastas vazias de tentativas interrompidas ficam apenas no ambiente. |
| Composição e áudio integral | Originais em `music-output/`; letra/prompt/config copiados para o projeto. O render completo e as conversões finais são preservados em `final/` após conclusão. |

O repositório guarda os artefatos pequenos e auditáveis do projeto e os áudios finais dentro do limite por arquivo do GitHub. Os pesos não estão no índice Git. `.gitignore` cobre modelos, pesos, caches, ambientes virtuais, downloads temporários, tokens, segredos e `HF_TOKEN`. Credenciais não foram copiadas nem incluídas no commit.

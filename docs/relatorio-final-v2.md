# Entrega final — O Peso da Minha Mão, V2

Faixa integral concluída em um único render de 210 s (3min30s), após a aprovação auditiva da prévia V2 pelo usuário. A letra original completa foi preservada em `lyrics/letra.txt` e `final/O_Peso_da_Minha_Mao_LETRA.txt`, também incluída no pacote MP3+letra. V1 e todas as amostras anteriores permanecem preservadas; a V1 continua descartada artisticamente.

Foi mantida a configuração funcional FP32 nativa com planejador 0.6B e a direção V2 aprovada: voz masculina adulta médio-grave, interpretação contida, MPB acústica sóbria, 65 BPM, ré menor, 4/4, seed 190102126, preset high, turbo com 8 passos e shift 3.0. Somente duração e texto foram estendidos para a faixa integral. Na última comparação técnica, FP32 com planejamento 0.6B levou 22min49s por 30 s contra 24min37s do INT8 com planejamento 1.7B; o INT8 sem planejamento foi mais rápido por segundo de áudio. A seleção técnica não constitui uma nota de qualidade vocal. A direção artística foi aprovada pelo usuário na V2.

O claude-music forneceu orientações de composição/prompt e seu motor Python real coordenou o ACE-Step. FFmpeg fez as conversões. Modelos existentes foram reutilizados offline. Nenhum áudio de referência foi condicionado, misturado, clonado ou publicado; a análise prévia serviu para características abstratas. Não houve novo benchmark ou ASR. Código e modelos oficiais têm licença MIT; nenhuma plataforma paga foi utilizada ou contratada.

Verificações: FLAC, WAV e MP3 decodificam integralmente; 210 s, estéreo, 48 kHz, amostras finitas, nenhum bloco de um segundo abaixo de -80 dBFS e nenhum silêncio de pelo menos 2 s abaixo de -60 dBFS. WAV PCM 24 bits e MP3 320 kbps. Pico WAV -1,50 dBFS; MP3 decodificado -1,60 dBFS. FLAC preservado idêntico ao original. Letra e conteúdo do ZIP conferidos byte a byte. A verificação não incluiu escuta humana pelo agente; dicção, reprodução audível de cada palavra e qualidade musical final não foram avaliadas por audição.

Pós-processamento: ganho fixo de aproximadamente -0,5 dB, fades de 15 ms no início e 350 ms no final, sem compressão, equalização ou mudança de duração. Tempo reportado de geração: 6330,9 s (1h45min31s), excluindo inicialização. `final/parametros-v2.json` contém texto integral, seed, versões e commits; `export-report.json`, `validation-report.json` e `SHA256SUMS.txt` documentam os arquivos.

Projeto: `/workspace/Musica_Ditadura`; repositório `https://github.com/odoni10/Musica_Ditadura`; branch `main`. Entregas:

| Arquivo em final/ | Tamanho em bytes |
|---|---:|
| O_Peso_da_Minha_Mao.flac | 21957521 |
| O_Peso_da_Minha_Mao.mp3 | 8402017 |
| O_Peso_da_Minha_Mao.wav | 60480132 |
| O_Peso_da_Minha_Mao_LETRA.txt | 1916 |
| O_Peso_da_Minha_Mao_MP3_e_Letra.zip | 8378371 |
| SHA256SUMS.txt | 728 |
| export-report.json | 5384 |
| parametros-v2.json | 3722 |
| validation-report.json | 1704 |

Somente no ambiente: dependências e pesos em `tools/ACE-Step-1.5/checkpoints/`, fontes de terceiros em `tools/`, venv/cache/Hugging Face/diagnósticos/logs em `/workspace/music-runtime/`, referências enviadas em `/workspace/attachments/` e `/workspace/music-reference/`, e originais de trabalho em `/workspace/music-output/`. Nada foi apagado. Inventário atualizado em `docs/runtime-inventory.json`. GitHub recebe apenas artefatos do projeto: letra, prompts, configurações, scripts, amostras, documentação e arquivos finais; nunca pesos, caches, ambientes, referências ou credenciais.

Links públicos finais verificados com HTTP 200. MP3, ZIP, letra TXT e parâmetros JSON baixados conferem com os hashes locais; WAV e FLAC tiveram tamanho HTTP conferido. Evidências em `docs/publication-v2.json`. Os modelos e referências não foram enviados ao GitHub.

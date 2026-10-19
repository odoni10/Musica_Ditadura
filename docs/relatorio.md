# Comparação final e produção

A última comparação foi encerrada. A faixa integral está sendo gerada com FP32 nativo e planejamento 0.6B; nenhum novo benchmark ou ASR foi iniciado.

| Configuração | Áudio | Tempo de geração | Tempo por segundo de áudio | RMS | Pico |
|---|---:|---:|---:|---:|---:|
| INT8 sem planejamento | 15 s | 8min31.8s | 34.12 s | -20.66 dBFS | -1.00 dBFS |
| INT8 com planejamento 1.7B | 30 s | 24min36.6s | 49.22 s | -18.93 dBFS | -1.00 dBFS |
| FP32 nativo com planejamento 0.6B | 30 s | 22min48.8s | 45.63 s | -16.69 dBFS | -1.00 dBFS |

Todas as amostras concluíram sem erro de geração, têm áudio finito e não silencioso, estéreo a 48 kHz e nenhum bloco de um segundo com pico abaixo de -80 dBFS. Tempos são os reportados pelo motor, sem a inicialização dos modelos.

**Escolhida: FP32 nativo com planejamento 0.6B.** A amostra foi 7,3% mais rápida que INT8 com planejamento 1.7B e usa os pesos sem quantização. INT8 sem planejamento venceu em velocidade isolada. Reutilizar o processo FP32 já carregado também evita outra inicialização pesada. A escolha privilegia o fluxo nativo com planejamento, funcionalidade e tempo observado.

A comparação não isola precisão: o INT8 simples tem 15 segundos e quatro linhas; as outras duas têm 30 segundos e oito linhas. O FP32 também usa outro planejador, seed e shift. RMS mais alto não significa qualidade superior.

**Limite de avaliação:** não há recurso de escuta humana neste ambiente. Clareza vocal, aderência da letra cantada, qualidade musical, presença audível de cada seção e originalidade perceptiva não foram confirmadas por audição. A letra integral e a estrutura foram fornecidas ao render. As transcrições históricas de Whisper foram pouco informativas e ficaram apenas como indicadores auxiliares, sem bloquear o trabalho.

Parâmetros da produção integral: ACE-Step v1.5 turbo, CPU FP32, planejador oficial 0.6B em backend PyTorch/CPU, preset high, batch 1, 8 passos, shift 3.0, seed 190102027, 180 s, 82 BPM, D minor, 4/4, português. Guidance solicitado 0.0; o modelo turbo ignora CFG e o motor aplica internamente 1.0.

Letra preservada em `lyrics/letra.txt`; direção em `prompts/direcao-musical.txt`. O alvo inicial era 210 s, ajustado antes deste encerramento para 180 s (3 minutos, dentro do pedido original), sem cortar o texto fornecido. Toda a faixa é solicitada em um render, preservando continuidade musical.

Ao terminar, os arquivos MP3, WAV 24 bits e FLAC original ficarão em `final/`, junto com medições e hashes. Pós-processamento restrito a ganho fixo para pico -1,5 dBFS e fades de 15 ms/350 ms nas extremidades, sem compressão ou equalização.

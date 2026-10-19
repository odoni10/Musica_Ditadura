# Referência e nova direção artística — V2

V1 cancelada por solicitação do usuário: a prévia funcionava tecnicamente, mas a voz feminina e a direção moderna/pop foram rejeitadas. Seus arquivos permanecem intactos como histórico. A aprovação técnica anterior não vale como aprovação artística.

## Fontes efetivamente analisadas

MP3 combinado enviado pelo usuário, 241,97 s, estéreo, 44,1 kHz, e `vozes.zip`, com cinco stems: vocals, drums, bass, other (241,97 s cada) e metronome (60 s). Os nomes dos arquivos indicam E major/127 BPM, mas essas etiquetas não foram tomadas como medições confirmadas. `musica.zip` excede o limite de transferência da ferramenta de 32 MiB e não foi aberto.

Os áudios foram decodificados localmente em mono a 11.025 Hz para análise de sinal com NumPy/SciPy. Não houve escuta, transcrição de letra, reprodução de partitura, extração de melodia para reutilização, clonagem ou envio das gravações ao modelo. Áudios e stems ficam fora do GitHub; somente medições, metodologia e direção abstrata são versionadas. Detalhes reproduzíveis em `reference-analysis-v2.json` e `scripts/analyze_reference.py`.

## Medições e interpretação limitada

| Aspecto | Resultado e limite |
|---|---|
| Andamento | Autocorrelação de onsets do mix dá candidatos em 130,7 e 65,4 BPM, além de ambiguidades métricas em 88,4/51,8. Stems reforçam a região de 65–67 em meio-tempo. Os picos detectados do metrônomo dão aproximadamente 125 BPM; sua etiqueta diz 127. Adoto uma sensação lenta de 65 BPM, sem impor a grade da gravação original. Não é uma análise manual de cada compasso. |
| Intensidade | RMS mono global do mix: -12,0 dBFS. Percentis 10/50/90 do RMS por segundo: -16,7/-12,1/-9,6 dBFS. Isso mede variação de energia, não emoção nem qualidade. A nova prévia não precisa copiar a masterização dessa gravação. |
| Registro vocal | Autocorrelação do stem vocal: percentis 10/50/90 de F0 em aproximadamente 140/200/240 Hz. Há risco de oitavas incorretas, vozes sobrepostas e vazamento da separação. Não identifica cantor nem permite concluir classificação vocal exata. A voz masculina adulta médio-grave da V2 vem do pedido explícito. |
| Caráter harmônico | Perfil de classes de altura do stem other favorece C# minor (correlação 0,805), seguido do relativo E major (0,678). Não é uma confirmação de tonalidade nem transcrição de acordes. A V2 mantém ré menor e uma melodia nova; não copia progressão ou contorno. |
| Textura | Energia concentrada em graves/médios; centroide espectral do mix analisado em mono e banda até 5,5 kHz: ~521 Hz. É uma característica espectral, não uma classificação de gênero ou instrumentos. |
| Instrumentação | Existem stems separados de voz, baixo, bateria e acompanhamento harmônico. A categoria other não permite afirmar por medição quais instrumentos acústicos estão presentes. Violão, baixo orgânico e percussão contida serão escolhidos segundo a direção do usuário. |

## Construção e densidade observáveis

A envoltória em blocos de 10 s sugere construção por camadas:

- 0–20 s: voz domina; outros stems estão próximos ao piso de ruído da separação.
- 20–80 s: acompanhamento other cresce, aproximadamente de -26 para -17 dBFS; baixo e bateria ainda muito baixos.
- 80–150 s: baixo ganha presença, com blocos perto de -17 a -23 dBFS; a bateria permanece discreta.
- 150–230 s: bateria passa a contribuir de modo relevante, com blocos perto de -19 a -24 dBFS; mix cresce gradualmente até aproximadamente -10 dBFS.
- 230–242 s: acompanhamento recua e a energia final cai.

Essas regiões são uma leitura da energia dos stems e não rótulos auditivamente confirmados de verso/refrão/ponte. O aprendizado aplicado é espaço inicial, crescimento gradual, peso dramático e voz em primeiro plano. Não será reproduzida essa sequência temporal como molde de composição.

## Nova prévia — exatamente uma geração

30 s de um refrão representativo da letra original de “O Peso da Minha Mão”, sem introdução longa. Voz masculina adulta, barítono em registro médio-grave, português brasileiro silábico, interpretação séria e contida, violão de nylon, baixo arredondado, percussão discreta e produção seca, escura e sóbria. Estética acústica de MPB dos anos 1970 como descrição ampla, sem nome de cantor no prompt, sem synth pop/EDM e sem arranjo épico solicitado.

Parâmetros funcionais preservados da última configuração: ACE-Step turbo em FP32 CPU, planejador 0.6B, 8 passos, shift 3.0, lote 1. Mudanças artísticas: 65 BPM, direção masculina acústica, nova seed 190102126; ré menor preservado. Letra completa não foi alterada, e a prévia usa suas oito linhas do primeiro refrão. Os modelos existentes serão reutilizados sem download adicional.

Só serão feitas verificações de arquivo, duração, codec e integridade. Nenhum ASR será usado para aprovação artística. O usuário ouvirá o MP3 e deverá aprovar explicitamente a direção antes de qualquer geração completa. O runner V2 termina após a prévia e não possui etapa de faixa integral.

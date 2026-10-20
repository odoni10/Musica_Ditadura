# O Peso da Minha Mão — videoclipe V2

Revisão visual completa de **3min30s**, em **Full HD, 24 fps**, usando o mesmo master musical V2. Agora são **24 ilustrações distintas em 24 planos, cada uma usada uma única vez**. A primeira versão usava sete imagens em 21 planos e permanece preservada em `../video/`.

- [Baixar MP4 da nova versão](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/video-v2/output/O_Peso_da_Minha_Mao_Videoclipe_V2.mp4)
- [Storyboard das 24 cenas](docs/storyboard.jpg)
- [Quadros extraídos do MP4](docs/export-frames.jpg)
- [Timeline editável](config/timeline.json)
- [Validação técnica](docs/validation.json)

## O que mudou

A textura pesada de gravura deu lugar a uma pintura mais suave, com rostos mais legíveis, sombras menos duras e maior variação de cores e iluminação. A história alterna casa, rua, espelho, fila de votação, ônibus, atendimento de saúde, rio, enchente, amigos, varanda e vizinhança. O encerramento acompanha o pão sendo partido e a casa vista pela janela à noite.

A emoção da primeira versão orienta o novo arco: afastamento, dúvida, consequências das escolhas, escuta e reaproximação. Nenhuma imagem da primeira versão é reutilizada. Cada pintura nova ocupa um único trecho contínuo, com movimentos discretos de câmera, profundidade, respiração, tecido, papel, água e mãos. É animação 2.5D de ilustrações; não há sincronização labial.

**Não foram acrescentados créditos nominais ou a cartela “dirigido por”, conforme a correção do pedido.** O único título sobreposto é o nome da música na abertura.

## Organização

- `assets/s01.png` a `s24.png`: as 24 cenas prontas para a montagem.
- `prompts/`: instruções de criação das artes.
- `config/assets.json`: identificação, origem e SHA-256 de cada cena.
- `config/source-sheets.json`: registro dos 12 pares de cenas gerados; originais preservados em `/workspace/generated_images/`.
- `config/timeline.json`: ordem, tempos, câmera e parâmetros de exportação.
- `config/audio-features.json`: características já existentes da música, reutilizadas na montagem.
- `scripts/`: preparação, animação, render e validação.
- `docs/`: storyboard, resultados e documentação.
- `output/`: MP4 final e cartaz.

As artes foram criadas com `image_gen`, em 12 pares de quadros. Cada par foi separado pela linha central, sem repintura; as 24 cenas têm composições próprias. Os PNGs separados estão incluídos, portanto os pares originais não são necessários para renderizar o projeto. Os recortes fornecem cenas aproximadamente 1182 × 665; a exportação é 1920 × 1080.

O áudio-fonte continua em `../final/O_Peso_da_Minha_Mao.wav`, preservado por hash. Não houve nova geração musical, alteração da letra, remix ou mudança de velocidade. O MP4 codifica o master completo em AAC estéreo, 48 kHz / 256 kbps. Os cortes se aproximam de ataques já medidos do áudio; a narrativa visual não pressupõe alinhamento palavra a palavra com o canto. Nenhum ASR foi usado.

## Reprodução

Requisitos: Python 3.12, FFmpeg, fontes Noto Serif Display / Noto Sans e as versões em `requirements.txt`. O ambiente já preparado usa `/workspace/video-runtime/venv/bin/python`.

```bash
python -m venv video-v2/.venv
video-v2/.venv/bin/pip install -r video-v2/requirements.txt
video-v2/.venv/bin/python video-v2/scripts/render.py --storyboard
video-v2/.venv/bin/python video-v2/scripts/render.py
video-v2/.venv/bin/python video-v2/scripts/validate.py
```

O render preserva saídas existentes e recusa sobrescrever arquivos finais ou parciais. Os PNGs e a timeline incluídos são suficientes para uma reprodução; `prepare_assets.py` documenta a separação dos pares originais e não precisa ser executado novamente. Nenhum modelo musical ou credencial é necessário para montar o vídeo. O log e o ambiente Python ficam somente em `/workspace/video-runtime/`.

# O Peso da Minha Mão — videoclipe

Videoclipe completo de **3min30s**, em **1920 × 1080, 24 fps**, com a música final V2 integral. Animação de ilustrações em 2.5D: sete pinturas originais, 21 planos, deslocamentos de profundidade, movimento localizado, atmosfera e montagem.

- [Assistir / baixar MP4](https://raw.githubusercontent.com/odoni10/Musica_Ditadura/main/video/output/O_Peso_da_Minha_Mao_Videoclipe.mp4)
- [Cartaz](output/cartaz.jpg)
- [Storyboard](docs/storyboard.jpg)
- [Roteiro e direção](docs/direcao.md)
- [Timeline editável](config/timeline.json)
- [Verificação técnica](docs/validation.json)

## Proposta visual

A mesma mesa abre e encerra o filme. Primeiro, o celular ocupa o lugar da conversa; no final, o pai oferece o pão. Entre esses gestos, a janela, a ponte inacabada, os amigos afastados e o papel na palma da mão transformam a letra em imagens. O índigo e a terra queimada preservam a sobriedade; a luz quente ganha sentido no reencontro.

O estilo combina gravura, monotipia e pintura sobre papel. Os personagens são adultos, originais, sem retratar pessoas reais. As ilustrações foram criadas com `image_gen`, usando a primeira pintura como referência visual das seguintes. Os PNGs originais estão preservados sem alterações em `assets/`; a composição e animação acontecem durante o render.

É uma animação de ilustrações, com gestos sutis e câmera: não há sincronização labial ou atuação corporal contínua. Os cortes usam ataques medidos do áudio, e a exposição acompanha suavemente a intensidade. O roteiro interpreta o arco da letra; não afirma alinhamento palavra a palavra com o canto. Não foi usado Whisper.

## Arquivos

```text
video/
  assets/              sete PNGs originais
  config/              manifesto, timeline e características do áudio
  docs/                direção, storyboard, render e validação
  scripts/             análise, animação, render e verificação
  output/              MP4 final e cartaz
  requirements.txt     dependências de render fixadas
```

O áudio-fonte é `../final/O_Peso_da_Minha_Mao.wav`, já existente no projeto. Foi mantido integralmente, sem recorte, remix, mudança de velocidade ou nova geração musical. A trilha do MP4 é uma codificação AAC estéreo de 256 kbps / 48 kHz desse master. O vídeo usa H.264, yuv420p, BT.709 e `faststart` para reprodução em navegadores.

## Reproduzir o projeto

Requisitos: Python 3.12, FFmpeg e fontes Noto Serif Display / Noto Sans. Não precisa de ACE-Step, GPU, Hugging Face, tokens ou novos modelos.

```bash
python -m venv video/.venv
video/.venv/bin/pip install -r video/requirements.txt
video/.venv/bin/python video/scripts/render.py --storyboard
video/.venv/bin/python video/scripts/render.py
video/.venv/bin/python video/scripts/validate.py
```

O render recusa sobrescrever um MP4 final ou parcial existente. Para uma revisão deliberada, preserve a entrega anterior em outra pasta antes de renderizar. `scripts/prepare_timeline.py` permite recalcular as características e os cortes a partir do WAV; não é necessário para reproduzir a timeline já salva.

Neste ambiente, o Python do vídeo está em `/workspace/video-runtime/venv/bin/python`. Logs e ambiente virtual permanecem em `/workspace/video-runtime/`; originais redundantes da ferramenta de imagem em `/workspace/generated_images/`. As cópias necessárias das imagens estão no projeto. Nada foi apagado, e nenhum peso musical foi baixado novamente.

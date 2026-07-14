"""Gera os QR codes de mesa (1 a N) para o Menu Interativo - 15 Anos Barbara.

Cada QR aponta para drinks.html?mesa=<numero>, para que o pedido feito
a partir daquele QR va identificado com a mesa correta no painel do barman
e na fila publica.

Uso:
    python scripts/gerar_qrcodes.py
"""

import qrcode
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "https://mateusrad.github.io/menu-interativo/index.html"
NUM_MESAS = 10
SAIDA_DIR = "qrcodes"

ROSA_PROFUNDO = (168, 80, 110)
DOURADO = (201, 168, 118)
TEXTO_ESCURO = (92, 58, 69)
BRANCO = (255, 255, 255)

CARD_W, CARD_H = 700, 900
QR_SIZE = 520


def carregar_fonte(tamanho, negrito=True):
    candidatos = [
        "arialbd.ttf" if negrito else "arial.ttf",
        "Arial Bold.ttf" if negrito else "Arial.ttf",
        "DejaVuSans-Bold.ttf" if negrito else "DejaVuSans.ttf",
    ]
    for nome in candidatos:
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def gerar_qr_imagem(url):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=TEXTO_ESCURO, back_color=BRANCO).convert("RGB")
    return img.resize((QR_SIZE, QR_SIZE))


def montar_cartao(numero_mesa):
    url = f"{BASE_URL}?mesa={numero_mesa}"
    qr_img = gerar_qr_imagem(url)

    card = Image.new("RGB", (CARD_W, CARD_H), BRANCO)
    draw = ImageDraw.Draw(card)

    # Moldura dourada fina
    draw.rectangle([12, 12, CARD_W - 13, CARD_H - 13], outline=DOURADO, width=4)
    draw.rectangle([22, 22, CARD_W - 23, CARD_H - 23], outline=ROSA_PROFUNDO, width=2)

    fonte_titulo = carregar_fonte(34)
    fonte_subtitulo = carregar_fonte(22, negrito=False)
    fonte_mesa_label = carregar_fonte(26)
    fonte_mesa_numero = carregar_fonte(64)

    titulo = "15 ANOS DA BÁRBARA"
    bbox = draw.textbbox((0, 0), titulo, font=fonte_titulo)
    draw.text(((CARD_W - (bbox[2] - bbox[0])) / 2, 60), titulo, font=fonte_titulo, fill=ROSA_PROFUNDO)

    subtitulo = "Escaneie para acessar o menu"
    bbox = draw.textbbox((0, 0), subtitulo, font=fonte_subtitulo)
    draw.text(((CARD_W - (bbox[2] - bbox[0])) / 2, 115), subtitulo, font=fonte_subtitulo, fill=TEXTO_ESCURO)

    qr_x = (CARD_W - QR_SIZE) // 2
    qr_y = 170
    card.paste(qr_img, (qr_x, qr_y))

    label = "MESA"
    bbox = draw.textbbox((0, 0), label, font=fonte_mesa_label)
    draw.text(((CARD_W - (bbox[2] - bbox[0])) / 2, qr_y + QR_SIZE + 30), label, font=fonte_mesa_label, fill=DOURADO)

    numero = str(numero_mesa)
    bbox = draw.textbbox((0, 0), numero, font=fonte_mesa_numero)
    draw.text(((CARD_W - (bbox[2] - bbox[0])) / 2, qr_y + QR_SIZE + 65), numero, font=fonte_mesa_numero, fill=ROSA_PROFUNDO)

    return card


def main():
    import os
    os.makedirs(SAIDA_DIR, exist_ok=True)
    for mesa in range(1, NUM_MESAS + 1):
        card = montar_cartao(mesa)
        caminho = f"{SAIDA_DIR}/mesa-{mesa:02d}.png"
        card.save(caminho)
        print(f"Gerado: {caminho}")


if __name__ == "__main__":
    main()

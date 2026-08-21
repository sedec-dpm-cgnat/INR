# -*- coding: utf-8 -*-
"""Prepara as logos: recorte circular antisserrilhado e alta resolucao."""
import sys, io, os, base64
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image, ImageDraw

SRC = r"C:\Users\cassi\OneDrive\Documents\SEDEC\logos"
D = os.path.dirname(os.path.abspath(__file__))
ALVO = 400          # resolucao final (exibida a ~62px -> densidade 6x)
SS = 4              # fator de supersampling da mascara


def circular(im):
    """Recorta em circulo inscrito, com borda suavizada por supersampling."""
    lado = min(im.size)
    esq = (im.width - lado) // 2
    topo = (im.height - lado) // 2
    im = im.crop((esq, topo, esq + lado, topo + lado))

    mask = Image.new("L", (lado * SS, lado * SS), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, lado * SS - 1, lado * SS - 1), fill=255)
    mask = mask.resize((lado, lado), Image.LANCZOS)

    alpha = im.getchannel("A")
    alpha = Image.composite(alpha, Image.new("L", im.size, 0), mask)
    im.putalpha(alpha)
    return im


def preparar(arquivo, nome, mascarar):
    im = Image.open(os.path.join(SRC, arquivo)).convert("RGBA")
    if mascarar:
        im = circular(im)
    im = im.resize((ALVO, ALVO), Image.LANCZOS)

    im.save(os.path.join(D, nome + ".png"), "PNG", optimize=True)

    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    b = buf.getvalue()
    uri = "data:image/png;base64," + base64.b64encode(b).decode()
    print(f"{nome}: {im.size}  png {len(b)/1024:.0f} KB  datauri {len(uri)/1024:.0f} KB"
          f"  {'[mascara circular]' if mascarar else '[alpha original]'}")
    return uri


uris = {
    "sedec": preparar("logo_marca_sedec.png", "logo_sedec", mascarar=False),
    "cgnat": preparar("DPM_CGNAT-circular-pequena.png", "logo_cgnat", mascarar=True),
}

with open(os.path.join(D, "logos.txt"), "w", encoding="utf-8") as fh:
    for k, v in uris.items():
        fh.write(k + "\t" + v + "\n")

print("TOTAL datauri: %.0f KB" % (sum(len(v) for v in uris.values()) / 1024))

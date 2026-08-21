# -*- coding: utf-8 -*-
"""Baixa as fontes IBM Plex e gera @font-face com data URI (sem dependência de rede)."""
import sys, io, os, re, base64, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

D = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# familia, peso, estilo
PEDIDOS = [
    ("IBM+Plex+Sans", "IBM Plex Sans", 400, "normal"),
    ("IBM+Plex+Sans", "IBM Plex Sans", 500, "normal"),
    ("IBM+Plex+Sans", "IBM Plex Sans", 600, "normal"),
    ("IBM+Plex+Sans", "IBM Plex Sans", 700, "normal"),
    ("IBM+Plex+Mono", "IBM Plex Mono", 400, "normal"),
    ("IBM+Plex+Mono", "IBM Plex Mono", 600, "normal"),
    ("IBM+Plex+Serif", "IBM Plex Serif", 400, "normal"),
    ("IBM+Plex+Serif", "IBM Plex Serif", 400, "italic"),
]

def baixar_css(familia, peso, estilo):
    ital = "1," if estilo == "italic" else ""
    eixo = "ital,wght@" + ital + str(peso) if estilo == "italic" else "wght@" + str(peso)
    url = f"https://fonts.googleapis.com/css2?family={familia}:{eixo}&display=swap&subset=latin,latin-ext"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8")

regras = []
total = 0
for familia, nome, peso, estilo in PEDIDOS:
    css = baixar_css(familia, peso, estilo)
    # pega o bloco latin (o ultimo costuma ser latin) - juntamos latin e latin-ext
    urls = re.findall(r"src:\s*url\((https://[^)]+\.woff2)\)", css)
    if not urls:
        print(f"  ! sem woff2 para {nome} {peso} {estilo}")
        continue
    dados = urllib.request.urlopen(
        urllib.request.Request(urls[-1], headers={"User-Agent": UA}), timeout=60).read()
    total += len(dados)
    b64 = base64.b64encode(dados).decode()
    regras.append(
        "@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:block;"
        "src:url(data:font/woff2;base64,%s) format('woff2')}" % (nome, estilo, peso, b64))
    print(f"  {nome} {peso} {estilo}: {len(dados)/1024:.0f} KB")

bloco = "\n".join(regras)
open(os.path.join(D, "fonts.css"), "w", encoding="utf-8").write(bloco)
print("TOTAL fontes: %.0f KB  ->  fonts.css %.0f KB" % (total / 1024, len(bloco) / 1024))

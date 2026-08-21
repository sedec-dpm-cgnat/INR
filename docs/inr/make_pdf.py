# -*- coding: utf-8 -*-
"""Gera o PDF a partir do HTML preservando o CSS, via Chromium headless."""
import sys, io, os, subprocess, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

D = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME):
    CHROME = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

origem = os.path.join(D, "inr.html")
destino = os.path.join(D, "INR_Fase1_Documento_Executivo.pdf")
perfil = os.path.join(D, "_chrome_profile")

if os.path.exists(destino):
    os.remove(destino)

url = "file:///" + origem.replace("\\", "/")
cmd = [
    CHROME,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--no-first-run",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=20000",
    "--user-data-dir=" + perfil,
    "--print-to-pdf=" + destino,
    url,
]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)

for _ in range(20):
    if os.path.exists(destino) and os.path.getsize(destino) > 0:
        break
    time.sleep(1)

if os.path.exists(destino):
    print("PDF gerado: %.0f KB" % (os.path.getsize(destino) / 1024))
else:
    print("ERRO ao gerar o PDF")
    print((r.stdout or "")[:800])
    print((r.stderr or "")[:800])
    sys.exit(1)

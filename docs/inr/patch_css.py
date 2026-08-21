# -*- coding: utf-8 -*-
"""Corrige os tres defeitos expostos pelo PDF: fontes, listas em flex e largura."""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, "head_tokens.html")
s = io.open(p, encoding="utf-8").read()

# ---------- 1. Fontes embutidas, sem dependencia de rede ----------
if "@font-face" not in s:
    fonts = io.open(os.path.join(D, "fonts.css"), encoding="utf-8").read()
    for link in [
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:ital,wght@0,400;0,500;1,400&display=swap">\n',
    ]:
        s = s.replace(link, "")
    s = s.replace("<style>\n", "<style>\n" + fonts + "\n", 1)
    print("1. fontes embutidas")

# ---------- 2. Listas: sai flex, entra marcador absoluto ----------
velho_plain = '''ul.plain{padding-left:0;list-style:none;margin:14px 0;display:grid;gap:9px}
ul.plain li{display:flex;gap:11px;font-size:14.5px;color:var(--ink2);line-height:1.55;max-width:74ch}
ul.plain li::before{content:"";flex:none;width:6px;height:6px;border-radius:50%;background:var(--accent);margin-top:9px}
ol.steps{counter-reset:s;list-style:none;padding:0;margin:16px 0;display:grid;gap:12px}
ol.steps li{counter-increment:s;display:flex;gap:14px;font-size:14.5px;color:var(--ink2);line-height:1.55;max-width:76ch}
ol.steps li::before{
  content:counter(s);flex:none;width:25px;height:25px;border-radius:50%;background:var(--side);color:#fff;
  font-family:"IBM Plex Mono",monospace;font-size:12px;font-weight:600;display:grid;place-items:center;margin-top:1px;
}'''

novo_plain = '''ul.plain{padding-left:0;list-style:none;margin:14px 0;display:grid;gap:9px}
ul.plain li{position:relative;padding-left:18px;font-size:14.5px;color:var(--ink2);line-height:1.55;max-width:74ch}
ul.plain li::before{content:"";position:absolute;left:0;top:9px;width:6px;height:6px;border-radius:50%;background:var(--accent)}
ol.steps{counter-reset:s;list-style:none;padding:0;margin:16px 0;display:grid;gap:12px}
ol.steps li{counter-increment:s;position:relative;padding-left:39px;min-height:25px;font-size:14.5px;color:var(--ink2);line-height:1.55;max-width:76ch}
ol.steps li::before{
  content:counter(s);position:absolute;left:0;top:1px;width:25px;height:25px;border-radius:50%;background:var(--side);color:#fff;
  font-family:"IBM Plex Mono",monospace;font-size:12px;font-weight:600;display:grid;place-items:center;
}'''

assert velho_plain in s, "bloco de listas nao encontrado"
s = s.replace(velho_plain, novo_plain)
print("2. listas corrigidas (flex -> marcador absoluto)")

# a regra de justificacao apontava para spans que nao existem mais
s = s.replace("ul.plain li>span,\n.metas li>span,ol.steps li,footer p",
              ".metas li>span,footer p")
s = s.replace("ul.plain li,.metas li{text-align:left}", ".metas li{text-align:left}")

# ---------- 3. Impressao: nada excede a largura da pagina ----------
velho_fig = "  .figures{gap:3mm;margin-bottom:5mm;grid-template-columns:repeat(4,1fr)}"
novo_fig = ("  .figures{gap:3mm;margin-bottom:5mm;grid-template-columns:repeat(2,1fr)}\n"
            "  img,table,.tbl-wrap,.gantt,.comp,.eval,pre{max-width:100%}\n"
            "  .eval{grid-template-columns:1fr}\n"
            "  .eval-arrow{display:none}")
assert velho_fig in s, "bloco .figures de impressao nao encontrado"
s = s.replace(velho_fig, novo_fig)
print("3. largura de impressao ajustada")

io.open(p, "w", encoding="utf-8").write(s)
print("OK -> head_tokens.html (%.0f KB)" % (os.path.getsize(p) / 1024))

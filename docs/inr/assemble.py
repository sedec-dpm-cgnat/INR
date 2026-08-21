# -*- coding: utf-8 -*-
"""Monta o documento final: cabecalho com logos + corpo Fase 1."""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

d = os.path.dirname(os.path.abspath(__file__))

logos = {}
with open(os.path.join(d, "logos.txt"), encoding="utf-8") as fh:
    for line in fh:
        k, v = line.rstrip("\n").split("\t")
        logos[k] = v

head = open(os.path.join(d, "head_tokens.html"), encoding="utf-8").read()
body = open(os.path.join(d, "body_f1.html"), encoding="utf-8").read()

alt_sedec = "Proteção e Defesa Civil — Brasil"
alt_cgnat = "DPM · CGNAT — Departamento de Prevenção e Mitigação de Desastres"
brand = (
    '    <div class="brand">\n'
    '      <img src="' + logos["sedec"] + '" alt="' + alt_sedec + '">\n'
    '      <span class="brand-rule"></span>\n'
    '      <img src="' + logos["cgnat"] + '" alt="' + alt_cgnat + '">\n'
    '    </div>\n'
)

assert '<div class="org">' in head, "ancora .org nao encontrada"
head = head.replace('    <div class="org">', brand + '    <div class="org">', 1)
head = head.replace('<div class="masthead-inner">', '<div class="masthead-inner" lang="pt-BR">', 1)
head = head.replace('<div class="wrap">', '<div class="wrap" lang="pt-BR">', 1)

head = re.sub(
    r'<p class="doc-sub">.*?</p>',
    '<p class="doc-sub">Proposta de projeto para a construção do primeiro índice nacional de '
    'risco de desastres do Brasil — metodologia, documentação técnica e plataforma pública — '
    'em execução descentralizada com a Universidade de Brasília. Fase 1 de 2.</p>',
    head, flags=re.S)
head = re.sub(r'<div><dt>Documento</dt><dd>[^<]*</dd></div>',
              '<div><dt>Documento</dt><dd>Executivo · v2.0</dd></div>', head)
head = re.sub(r'<div><dt>Prazo</dt><dd>[^<]*</dd></div>',
              '<div><dt>Prazo</dt><dd>24 meses</dd></div>', head)
head = re.sub(r'<div><dt>Valor estimado</dt><dd>[^<]*</dd></div>',
              '<div><dt>Valor — Fase 1</dt><dd>R$ 2.400.000</dd></div>', head)

out = head + body
p = os.path.join(d, "inr.html")
open(p, "w", encoding="utf-8").write(out)

print("OK ->", p, "%.0f KB" % (os.path.getsize(p) / 1024))
print("logos embutidas:", out.count("data:image/png;base64,"))
print('lang="pt-BR":', out.count('lang="pt-BR"'))
print("secoes:", len(re.findall(r'class="sec-num"', out)))
print("section abre/fecha:", out.count("<section"), "/", out.count("</section>"))
print("table abre/fecha:", out.count("<table>"), "/", out.count("</table>"))
print("div abre/fecha:", out.count("<div"), "/", out.count("</div>"))

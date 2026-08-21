# -*- coding: utf-8 -*-
"""Gera DOCX e PDF a partir do HTML do documento executivo.

Converte as estruturas visuais (cards, gantt, callouts) em equivalentes
que sobrevivem ao Word: tabelas e parágrafos rotulados.
"""
import sys, io, os, re, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup

D = os.path.dirname(os.path.abspath(__file__))
PANDOC = r"C:\Program Files\RStudio\resources\app\bin\quarto\bin\tools\pandoc.exe"
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"

soup = BeautifulSoup(open(os.path.join(D, "inr.html"), encoding="utf-8").read(), "html.parser")

for tag in soup.select("style, script, title, link"):
    tag.decompose()

def novo(nome, texto=None):
    el = soup.new_tag(nome)
    if texto is not None:
        el.string = texto
    return el

# --- Cabeçalho: logos em arquivo + títulos ------------------------------------
mast = soup.select_one(".masthead")
if mast:
    bloco = novo("div")
    for arq, alt in [("logo_sedec.png", "Proteção e Defesa Civil — Brasil"),
                     ("logo_cgnat.png", "DPM · CGNAT")]:
        img = soup.new_tag("img", src=arq, alt=alt, width="90")
        bloco.append(img)
    org = mast.select_one(".org")
    if org:
        p = novo("p", " · ".join(s.get_text(strip=True) for s in org.find_all("span")))
        bloco.append(p)
    sub = mast.select_one(".doc-sub")
    if sub:
        bloco.append(novo("p", sub.get_text(" ", strip=True)))
    meta = mast.select_one(".doc-meta")
    if meta:
        itens = []
        for div in meta.find_all("div", recursive=False):
            dt = div.find("dt"); dd = div.find("dd")
            if dt and dd:
                itens.append(f"{dt.get_text(strip=True)}: {dd.get_text(strip=True)}")
        bloco.append(novo("p", " | ".join(itens)))
    mast.replace_with(bloco)

# --- Cards de números -> tabela -----------------------------------------------
for dl in soup.select("dl.figures"):
    tbl = novo("table"); tb = novo("tbody")
    for fig in dl.select(".fig"):
        dt = fig.find("dt"); dd = fig.find("dd")
        unit = dd.find("span", class_="unit") if dd else None
        if unit:
            u = unit.get_text(" ", strip=True); unit.extract()
        else:
            u = ""
        tr = novo("tr")
        for txt in (dt.get_text(strip=True), dd.get_text(strip=True), u):
            td = novo("td", txt); tr.append(td)
        tb.append(tr)
    tbl.append(tb); dl.replace_with(tbl)

# --- Gantt -> tabela com marcas ------------------------------------------------
for g in soup.select(".gantt"):
    tbl = novo("table"); th = novo("thead"); trh = novo("tr")
    for h in ["Meta", "Descrição", "S1", "S2", "S3", "S4"]:
        trh.append(novo("th", h))
    th.append(trh); tbl.append(th)
    tb = novo("tbody")
    for row in g.select(".gantt-row"):
        lbl = row.select_one(".gantt-lbl")
        b = lbl.find("b"); sp = lbl.find("span")
        tr = novo("tr")
        tr.append(novo("td", b.get_text(strip=True) if b else ""))
        tr.append(novo("td", sp.get_text(strip=True) if sp else ""))
        for cell in row.select(".gantt-cell"):
            tr.append(novo("td", "X" if cell.select_one(".gantt-fill") else ""))
        tb.append(tr)
    tbl.append(tb); g.replace_with(tbl)

# --- Cronograma financeiro (barras) -> tabela ----------------------------------
for cash in soup.select(".cash"):
    tbl = novo("table"); th = novo("thead"); trh = novo("tr")
    for h in ["Semestre", "Participação", "Valor (R$)"]:
        trh.append(novo("th", h))
    th.append(trh); tbl.append(th)
    tb = novo("tbody")
    for row in cash.select(".cash-row"):
        tr = novo("tr")
        for sel in [".cash-lbl", ".cash-bar", ".cash-val"]:
            el = row.select_one(sel)
            tr.append(novo("td", el.get_text(strip=True) if el else ""))
        tb.append(tr)
    tbl.append(tb); cash.replace_with(tbl)

# --- Callouts -> parágrafo com rótulo em negrito -------------------------------
for c in soup.select(".callout"):
    lbl = c.select_one(".label")
    if lbl:
        forte = novo("strong", lbl.get_text(strip=True).upper() + " — ")
        prox = lbl.find_next_sibling("p")
        lbl.extract()
        if prox:
            prox.insert(0, forte)

# --- Comparativo ICPM/INR e Fase 1/Fase 2 -> tabela ----------------------------
for ev in soup.select(".eval"):
    cols = ev.select(".eval-col")
    tbl = novo("table"); th = novo("thead"); trh = novo("tr")
    for col in cols:
        h4 = col.find("h4"); nm = col.select_one(".name")
        cab = (h4.get_text(strip=True) if h4 else "")
        if nm:
            cab += " — " + nm.get_text(strip=True)
        trh.append(novo("th", cab))
    th.append(trh); tbl.append(th)
    tb = novo("tbody"); tr = novo("tr")
    for col in cols:
        td = novo("td")
        ul = col.find("ul")
        if ul:
            td.append(ul.extract())
        tr.append(td)
    tb.append(tr); tbl.append(tb); ev.replace_with(tbl)

# --- Componentes: cabeçalho vira heading --------------------------------------
for comp in soup.select(".comp"):
    head = comp.select_one(".comp-head")
    if head:
        tag = head.select_one(".comp-tag"); h3 = head.find("h3")
        share = head.select_one(".comp-share")
        titulo = " ".join(x.get_text(strip=True) for x in [tag, h3, share] if x)
        head.replace_with(novo("h3", titulo))

# --- Numeração das seções entra no título -------------------------------------
for sh in soup.select(".sec-head"):
    num = sh.select_one(".sec-num"); h2 = sh.find("h2")
    if num and h2:
        h2.string = num.get_text(strip=True) + ". " + h2.get_text(strip=True)
        num.extract()
        sh.replace_with(h2)

# --- Metas: id + texto na mesma linha -----------------------------------------
for li in soup.select("ul.metas li"):
    mid = li.select_one(".mid")
    if mid:
        mid.replace_with(novo("strong", mid.get_text(strip=True) + " "))

# --- Sumário manual (campo de TOC do Word não se popula em conversão headless) --
wrap = soup.select_one(".wrap") or soup
sumario = novo("div")
sumario.append(novo("h2", "Sumário"))
lista = novo("ol")
for h2 in wrap.find_all("h2"):
    txt = h2.get_text(strip=True)
    if txt.lower().startswith("sumário"):
        continue
    li = novo("li", txt)
    lista.append(li)
sumario.append(lista)
primeira = wrap.find("section")
if primeira:
    primeira.insert_before(sumario)

html_limpo = str(soup)
p_html = os.path.join(D, "inr_para_conversao.html")
open(p_html, "w", encoding="utf-8").write(html_limpo)

# --- Conversões ----------------------------------------------------------------
# O DOCX intermediário fica separado do arquivo final para que a estilização
# possa ser reaplicada de forma determinística após cada conversão do Pandoc.
docx_base = os.path.join(D, "INR_Fase1_Documento_Executivo_pandoc.docx")
docx = os.path.join(D, "INR_Fase1_Documento_Executivo_formatado.docx")
cmd = [PANDOC, p_html, "-f", "html", "-o", docx_base,
       "--metadata", "title=Índice Nacional de Risco — Fase 1",
       "--metadata", "lang=pt-BR",
       "--resource-path", D]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("pandoc ->", "OK" if r.returncode == 0 else "ERRO")
if r.returncode != 0:
    print((r.stderr or "")[:1500]); sys.exit(1)

style_script = os.path.join(D, "style_docx.py")
styled = subprocess.run([sys.executable, style_script, docx_base, docx],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
print("estilo DOCX ->", "OK" if styled.returncode == 0 else "ERRO")
if styled.returncode != 0:
    print((styled.stdout or "")[-1000:])
    print((styled.stderr or "")[-1500:])
    sys.exit(1)
print("   DOCX: %.0f KB" % (os.path.getsize(docx) / 1024))

print("   (PDF gerado separadamente por make_pdf.py, que preserva o CSS)")

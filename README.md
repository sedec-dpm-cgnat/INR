# Índice Nacional de Risco (INR)

Projeto específico do Índice Nacional de Risco de desastres do Brasil.

## Acesso rápido

- [Página web do INR](index.html)
- [PDF — documento executivo](docs/inr/INR_Fase1_Documento_Executivo.pdf)
- [Word — documento editável](INR_Fase1_Documento_Executivo.docx)

## Conteúdo

A página web é autocontida: identidade visual, fontes e logos estão incorporadas
no HTML. Assim, ela pode ser publicada como GitHub Pages e compartilhada por link.

Os arquivos-fonte de montagem e os geradores estão em `docs/inr/`.

## Regeneração

```powershell
python docs/inr/assemble.py
Copy-Item docs/inr/inr.html index.html
python docs/inr/make_pdf.py
python docs/inr/make_docs.py
Copy-Item docs/inr/INR_Fase1_Documento_Executivo_formatado.docx INR_Fase1_Documento_Executivo.docx
```

O PDF preserva a formatação visual do HTML. O Word é gerado como arquivo editável
com capa, tabelas, destaques, rodapé e numeração de páginas.

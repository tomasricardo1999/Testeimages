#!/usr/bin/env python3
"""Valida o pacote aprovado e cria cópias JPEG públicas para a API do Instagram."""
from __future__ import annotations
import os
from pathlib import Path
from PIL import Image

ticker = os.environ["TICKER"].strip().upper()
style = os.environ["ESTILO"]
if not ticker or len(ticker) > 15 or not all(c.isalnum() or c in ".-" for c in ticker) or not ticker[0].isalnum():
    raise SystemExit("Ticker inválido.")
base = Path(f"dados_{ticker.lower()}") / "instagram"
folder = base if style == "standard" else base / "variantes" / style

if style not in {"standard", "editorial", "institucional", "criativo"}:
    raise SystemExit(f"Estilo inválido: {style}")

slides = sorted(folder.glob("slide_*.png"))
if len(slides) != 11:
    raise SystemExit(f"Esperados exatamente 11 slides PNG em {folder}; encontrados {len(slides)}")

caption_file = folder / "legenda_instagram.txt"
if not caption_file.is_file():
    raise SystemExit(f"Legenda não encontrada: {caption_file}")
caption = caption_file.read_text(encoding="utf-8").strip()
if not caption:
    raise SystemExit("A legenda está vazia.")

for index, source in enumerate(slides, start=1):
    with Image.open(source) as image:
        if image.size != (1080, 1350):
            raise SystemExit(f"{source}: dimensão {image.size}, esperada 1080x1350.")
        image.verify()
    with Image.open(source) as image:
        image.convert("RGB").save(source.with_suffix(".jpg"), "JPEG", quality=92, optimize=True)
    print(f"Preparado: {source.with_suffix('.jpg')}")

print(f"{ticker}/{style}: 11 slides validados e convertidos para JPEG.")
print("A API do Instagram aceita no máximo 10 itens por carrossel; a publicação será dividida em 10 + 1.")

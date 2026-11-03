#!/usr/bin/env python3
"""Valida a estrutura dos carrosseis e prepara um pacote de revisão manual (sem publicar)."""
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image

STYLES = ("", "editorial", "institucional", "criativo")

def validate(folder: Path, ticker: str) -> list[str]:
    errors = []
    for style in STYLES:
        target = folder / "instagram" / (Path("variantes") / style if style else Path("."))
        if not target.exists():
            errors.append(f"{ticker}/{style or 'standard'}: pasta em falta: {target}")
            continue
        slides = sorted(target.glob("slide_*.png"))
        if len(slides) != 11:
            errors.append(f"{ticker}/{style or 'standard'}: esperados 11 slides, encontrados {len(slides)}")
        for slide in slides:
            try:
                with Image.open(slide) as im:
                    if im.size != (1080, 1350):
                        errors.append(f"{slide}: dimensão {im.size}, esperado 1080x1350")
                    im.verify()
            except Exception as exc:
                errors.append(f"{slide}: imagem inválida ({exc})")
        if not (target / "legenda_instagram.txt").exists():
            errors.append(f"{ticker}/{style or 'standard'}: legenda em falta")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--dados", required=True)
    args = parser.parse_args()
    folder = Path(args.dados)
    errors = validate(folder, args.ticker.upper())
    lines = [
        f"PACOTE DE APROVACAO — {args.ticker.upper()}",
        "ESTADO: RASCUNHO — NAO PUBLICAR AUTOMATICAMENTE",
        "",
        "Checklist de revisão humana:",
        "[ ] Confirmar valores, períodos e fontes dos dados financeiros.",
        "[ ] Verificar legibilidade, ortografia, cortes e consistência dos 11 slides.",
        "[ ] Confirmar que a legenda corresponde aos slides e inclui disclaimer.",
        "[ ] Confirmar adequação das métricas ao modelo de negócio da empresa.",
        "[ ] Aprovar expressamente o conjunto antes de qualquer publicação.",
        "",
    ]
    if args.ticker.upper() == "MAIN":
        lines += [
            "Nota MAIN/BDC: validar NII por ação, distribuições declaradas por ação,",
            "cobertura do dividendo por NII e dividendos especiais/extraordinários.",
            "Dividend yield e payout são snapshots e não provam cobertura futura.",
            "",
        ]
    lines += [
        "Resultado da validação estrutural:",
    ]
    lines += [f"ERRO: {e}" for e in errors] if errors else [
        "OK: 11 imagens PNG 1080x1350 e legenda presentes em cada variante."
    ]
    lines += ["", "Nenhuma publicação foi efetuada."]
    (folder / "APROVACAO_MANUAL.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"{args.ticker.upper()}: pacote preparado para aprovação manual.")

if __name__ == "__main__":
    main()

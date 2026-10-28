#!/usr/bin/env python3
"""Gera um cartaz SVG diário: banana sorridente + calendário em português.

Uso:
    python3 banana_do_dia.py
    python3 banana_do_dia.py --data 2026-10-28 --saida banana.svg

Só usa a biblioteca padrão do Python. O número do dia é calculado com
date.timetuple().tm_yday, por isso anos bissextos são tratados corretamente.
"""
from datetime import date
from pathlib import Path
import argparse
import html

DIAS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
        "sexta-feira", "sábado", "domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def texto_data(d):
    return f"{DIAS[d.weekday()].capitalize()}, {d.day} de {MESES[d.month - 1]} de {d.year}"


def criar_svg(d):
    data = html.escape(texto_data(d))
    ordinal = d.timetuple().tm_yday
    total = 366 if (d.replace(month=12, day=31).timetuple().tm_yday == 366) else 365
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
  <defs>
    <linearGradient id="fundo" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fff4b8"/><stop offset="1" stop-color="#b7edff"/>
    </linearGradient>
    <linearGradient id="banana" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fff65c"/><stop offset="1" stop-color="#ffbd16"/>
    </linearGradient>
    <filter id="sombra" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="12" stdDeviation="12" flood-color="#5b6c78" flood-opacity=".2"/>
    </filter>
  </defs>
  <rect width="1000" height="1000" rx="55" fill="url(#fundo)"/>
  <g fill="#fff" opacity=".8"><circle cx="100" cy="160" r="17"/><circle cx="870" cy="120" r="24"/><circle cx="910" cy="770" r="15"/><circle cx="100" cy="820" r="23"/></g>
  <g font-family="sans-serif" font-weight="bold" fill="#ef8c28"><text x="100" y="280" font-size="44">✦</text><text x="860" y="350" font-size="52">✦</text><text x="110" y="680" font-size="38">✦</text></g>
  <!-- Banana mascot -->
  <g filter="url(#sombra)" transform="translate(65 160) rotate(-8 280 400)">
    <path d="M300 70 C210 150 195 275 225 380 C253 483 328 550 416 559 C477 565 527 531 542 485 C489 504 435 474 404 424 C364 360 363 270 392 204 C413 155 397 105 365 76 C346 58 321 57 300 70Z" fill="url(#banana)" stroke="#e7a514" stroke-width="9"/>
    <path d="M297 72 L287 38 Q300 22 325 30 L365 70 Q342 82 320 84Z" fill="#80502c" stroke="#674021" stroke-width="8" stroke-linejoin="round"/>
    <path d="M411 485 Q445 520 492 500" fill="none" stroke="#e69b13" stroke-width="8" stroke-linecap="round"/>
    <ellipse cx="300" cy="290" rx="27" ry="39" fill="#fff"/><ellipse cx="370" cy="280" rx="27" ry="39" fill="#fff"/>
    <ellipse cx="307" cy="299" rx="13" ry="22" fill="#26364a"/><ellipse cx="377" cy="289" rx="13" ry="22" fill="#26364a"/>
    <circle cx="311" cy="291" r="5" fill="#fff"/><circle cx="381" cy="281" r="5" fill="#fff"/>
    <path d="M290 350 Q338 407 391 344" fill="#fff" stroke="#6b3c22" stroke-width="11" stroke-linecap="round"/>
    <path d="M324 378 Q343 392 365 375" fill="#f15c65"/>
    <circle cx="267" cy="335" r="17" fill="#ff9c87" opacity=".8"/><circle cx="411" cy="325" r="17" fill="#ff9c87" opacity=".8"/>
  </g>
  <!-- Calendar card -->
  <g filter="url(#sombra)">
    <rect x="475" y="205" width="455" height="570" rx="30" fill="#fffdf5" stroke="#e7a13b" stroke-width="5"/>
    <path d="M475 235 Q475 205 505 205 H900 Q930 205 930 235 V315 H475Z" fill="#f45d49"/>
    <g stroke="#5b3540" stroke-width="12" stroke-linecap="round"><path d="M555 195 V237"/><path d="M650 195 V237"/><path d="M745 195 V237"/><path d="M840 195 V237"/></g>
    <text x="702" y="280" text-anchor="middle" font-family="sans-serif" font-size="36" font-weight="bold" fill="#fff">Banana do Dia</text>
    <text x="702" y="370" text-anchor="middle" font-family="sans-serif" font-size="25" fill="#25425e">{data}</text>
    <path d="M520 402 H885" stroke="#f2c15b" stroke-width="4" stroke-linecap="round"/>
    <rect x="535" y="435" width="95" height="90" rx="13" fill="#ffe8d8" stroke="#f45d49" stroke-width="5"/>
    <g fill="#f45d49"><rect x="551" y="450" width="18" height="18" rx="4"/><rect x="579" y="450" width="18" height="18" rx="4"/><rect x="607" y="450" width="8" height="18" rx="3"/><rect x="551" y="480" width="18" height="18" rx="4"/><rect x="579" y="480" width="18" height="18" rx="4"/></g>
    <text x="765" y="490" text-anchor="middle" font-family="sans-serif" font-size="54" font-weight="bold" fill="#183d63">{ordinal}.º</text>
    <text x="765" y="535" text-anchor="middle" font-family="sans-serif" font-size="25" fill="#183d63">dia do ano (de {total})</text>
    <path d="M520 570 H885" stroke="#e9dfce" stroke-width="3"/>
    <text x="702" y="625" text-anchor="middle" font-family="sans-serif" font-size="25" fill="#25425e">Mais um dia para</text>
    <text x="702" y="665" text-anchor="middle" font-family="sans-serif" font-size="25" fill="#25425e">fazer coisas incríveis!</text>
    <text x="702" y="720" text-anchor="middle" font-family="sans-serif" font-size="35" fill="#f2a900">★ ☀ ★</text>
  </g>
  <text x="500" y="900" text-anchor="middle" font-family="sans-serif" font-size="28" font-weight="bold" fill="#35627a">Um dia feliz começa com um sorriso!</text>
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", help="data no formato AAAA-MM-DD (por omissão: hoje)")
    parser.add_argument("--saida", default="banana-do-dia.svg", help="ficheiro SVG de saída")
    args = parser.parse_args()
    d = date.fromisoformat(args.data) if args.data else date.today()
    destino = Path(args.saida)
    destino.write_text(criar_svg(d), encoding="utf-8")
    print(f"Imagem criada: {destino} — {texto_data(d)} — {d.timetuple().tm_yday}.º dia")


if __name__ == "__main__":
    main()

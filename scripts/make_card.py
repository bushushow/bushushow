#!/usr/bin/env python3
"""Neofetch tarzi animasyonlu bilgi karti SVG'si uretir.

Icerigi degistirmek icin asagidaki CONFIG sozlugunu duzenlemen yeterli.
"""
import html

THEME = {
    "bg": "#12071f",
    "panel": "#1b0d2e",
    "dim": "#6b3fa0",
    "mid": "#a855f7",
    "hot": "#e879f9",
    "glow": "#c084fc",
    "text": "#e9d5ff",
    "muted": "#9a7fc0",
}

CONFIG = {
    "user": "bushushow",
    "title": "Busra Ozlem Koc",
    "subtitle": "github.com/bushushow",
    "rows": [
        ("role", "Computer Engineering, 4th year @ Hacettepe University"),
        ("focus", "Agentic AI  ·  LLM systems  ·  Machine Learning"),
        ("research", "HUBioDataLab — CROssBAR biomedical knowledge graph"),
        ("agentic", "RAG pipelines, ReAct agents, tool use, agent memory"),
        ("experience", "AI Intern @ Microsoft  ·  AI Intern @ Huawei"),
        ("community", "Huawei Student Developer Campus Ambassador"),
        ("building", "ML models, agentic apps, hackathon prototypes"),
        ("location", "Bursa, Turkiye"),
    ],
    "footer": "always compiling something",
}

PAD = 28
LABEL_X = PAD + 16
VALUE_X = PAD + 112
ROW_H = 27
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def build(cfg=CONFIG, out="assets/card.svg", width=560, fs=12):
    rows = cfg["rows"]
    head_h = 108
    h = head_h + len(rows) * ROW_H + 74
    p = []
    a = p.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" '
      f'viewBox="0 0 {width} {h}" role="img" aria-label="Profile info card">')

    a("<defs>"
      f'<linearGradient id="cg" x1="0" y1="0" x2="1" y2="1">'
      f'<stop offset="0%" stop-color="{THEME["hot"]}"/>'
      f'<stop offset="100%" stop-color="{THEME["mid"]}"/></linearGradient>'
      f'<linearGradient id="line" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0%" stop-color="{THEME["hot"]}" stop-opacity="0.9"/>'
      f'<stop offset="100%" stop-color="{THEME["mid"]}" stop-opacity="0"/></linearGradient>'
      '<filter id="cglow" x="-30%" y="-30%" width="160%" height="160%">'
      '<feGaussianBlur stdDeviation="2.4" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
      "</filter></defs>")

    a(f'<rect width="{width}" height="{h}" rx="14" fill="{THEME["bg"]}" '
      f'stroke="{THEME["dim"]}" stroke-opacity="0.55"/>')
    for i, c in enumerate([THEME["hot"], THEME["glow"], THEME["mid"]]):
        a(f'<circle cx="{22 + i * 16}" cy="20" r="5" fill="{c}" opacity="0.85"/>')
    a(f'<text x="{width - 16}" y="24" text-anchor="end" font-family="{FONT}" font-size="11" '
      f'fill="{THEME["glow"]}" opacity="0.6">whoami.sh</text>')

    # prompt satiri
    a(f'<text x="{PAD}" y="62" font-family="{FONT}" font-size="13" fill="{THEME["muted"]}" opacity="0">'
      f'<tspan fill="{THEME["hot"]}">{html.escape(cfg["user"])}</tspan>'
      f'<tspan fill="{THEME["muted"]}">:~$ </tspan>'
      f'<tspan fill="{THEME["text"]}">neofetch --profile</tspan>'
      f'<animate attributeName="opacity" values="0;1" dur="0.3s" begin="0s" fill="freeze"/></text>')

    # isim
    a(f'<text x="{PAD}" y="94" font-family="{FONT}" font-size="21" font-weight="700" '
      f'fill="url(#cg)" filter="url(#cglow)" opacity="0">{html.escape(cfg["title"])}'
      f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="0.35s" fill="freeze"/></text>')
    a(f'<text x="{PAD}" y="112" font-family="{FONT}" font-size="12" fill="{THEME["muted"]}" opacity="0">'
      f'{html.escape(cfg["subtitle"])}'
      f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="0.5s" fill="freeze"/></text>')

    # ayirici cizgi (soldan saga cizilir)
    a(f'<rect x="{PAD}" y="126" width="0" height="1.6" fill="url(#line)">'
      f'<animate attributeName="width" values="0;{width - PAD * 2}" dur="0.7s" '
      f'begin="0.6s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect>')

    y = head_h + 34
    for i, (label, value) in enumerate(rows):
        begin = round(0.85 + i * 0.13, 3)
        a(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.45s" '
          f'begin="{begin}s" fill="freeze"/>'
          f'<circle cx="{PAD + 4}" cy="{y - 5}" r="2.6" fill="{THEME["hot"]}"/>'
          f'<text x="{LABEL_X}" y="{y}" font-family="{FONT}" font-size="{fs}" font-weight="600" '
          f'fill="{THEME["glow"]}">{html.escape(label)}</text>'
          f'<text x="{VALUE_X}" y="{y}" font-family="{FONT}" font-size="{fs}" '
          f'fill="{THEME["text"]}">{html.escape(value)}</text></g>')
        y += ROW_H

    # renk paleti noktalari
    swatch_y = y + 6
    for i, c in enumerate(["#4c1d95", "#6b21a8", "#7e22ce", "#9333ea", "#a855f7",
                           "#c084fc", "#d8b4fe", "#f0abfc"]):
        a(f'<rect x="{PAD + i * 22}" y="{swatch_y}" width="16" height="16" rx="3" fill="{c}" opacity="0">'
          f'<animate attributeName="opacity" values="0;1" dur="0.3s" '
          f'begin="{round(0.85 + len(rows) * 0.13 + i * 0.06, 2)}s" fill="freeze"/></rect>')

    a(f'<text x="{width - PAD}" y="{swatch_y + 13}" text-anchor="end" font-family="{FONT}" '
      f'font-size="12" fill="{THEME["muted"]}" opacity="0">{html.escape(cfg["footer"])}'
      f'<animate attributeName="opacity" values="0;0.85" dur="0.6s" '
      f'begin="{round(1.2 + len(rows) * 0.13, 2)}s" fill="freeze"/></text>')

    a("</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("".join(p))
    print(f"{out}: {width}x{h}px")


if __name__ == "__main__":
    build()

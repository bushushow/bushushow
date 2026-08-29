#!/usr/bin/env python3
"""Animasyonlu teknoloji yigini seridi (SVG).

Rozetleri degistirmek icin GROUPS listesini duzenle.
"""
import html

THEME = {
    "bg": "#12071f",
    "dim": "#6b3fa0",
    "mid": "#a855f7",
    "hot": "#e879f9",
    "glow": "#c084fc",
    "text": "#e9d5ff",
    "muted": "#9a7fc0",
    "pill": "#241436",
}

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

GROUPS = [
    ("languages", ["Python", "C", "C++", "Java", "JavaScript", "SQL", "Bash"]),
    ("ml / ai", ["PyTorch", "scikit-learn", "NumPy", "pandas", "LightGBM", "XGBoost",
                 "OpenCV", "Hugging Face"]),
    ("agentic", ["LLM agents", "RAG", "LangChain", "ReAct", "vector DBs", "MCP"]),
    ("tools", ["Git", "Docker", "Linux", "FastAPI", "GitHub Actions", "Jupyter",
               "JavaFX", "Arduino", "Canva"]),
]

PAD = 26
TOP = 48
LABEL_W = 108
PILL_H = 26
PILL_GAP = 8
ROW_GAP = 16
CHAR_W = 7.1
PILL_PAD = 13


def build(groups=GROUPS, out="assets/stack.svg", width=820):
    p = []
    a = p.append

    # once yerlesimi hesapla (satirlar tasarsa alt satira ge)
    layout = []
    y = TOP
    for label, items in groups:
        x = PAD + LABEL_W
        rows_in_group = 1
        placed = []
        for it in items:
            w = int(len(it) * CHAR_W + PILL_PAD * 2)
            if x + w > width - PAD:
                x = PAD + LABEL_W
                y += PILL_H + PILL_GAP
                rows_in_group += 1
            placed.append((it, x, y, w))
            x += w + PILL_GAP
        layout.append((label, placed, y - (rows_in_group - 1) * (PILL_H + PILL_GAP)))
        y += PILL_H + ROW_GAP
    height = y + 14

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
      f'viewBox="0 0 {width} {height}" role="img" aria-label="Tech stack">')
    a("<defs>"
      f'<linearGradient id="sg" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0%" stop-color="{THEME["hot"]}"/>'
      f'<stop offset="100%" stop-color="{THEME["mid"]}"/></linearGradient>'
      '<filter id="sglow" x="-40%" y="-40%" width="180%" height="180%">'
      '<feGaussianBlur stdDeviation="2" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
      "</filter></defs>")
    a(f'<rect width="{width}" height="{height}" rx="14" fill="{THEME["bg"]}" '
      f'stroke="{THEME["dim"]}" stroke-opacity="0.55"/>')
    for i, c in enumerate([THEME["hot"], THEME["glow"], THEME["mid"]]):
        a(f'<circle cx="{22 + i * 16}" cy="20" r="5" fill="{c}" opacity="0.85"/>')
    a(f'<text x="{width - 16}" y="24" text-anchor="end" font-family="{FONT}" font-size="11" '
      f'fill="{THEME["glow"]}" opacity="0.6">stack --list</text>')

    i = 0
    for label, placed, label_y in layout:
        a(f'<text x="{PAD}" y="{label_y + 18}" font-family="{FONT}" font-size="12" '
          f'font-weight="600" fill="{THEME["glow"]}" opacity="0">{html.escape(label)}'
          f'<animate attributeName="opacity" values="0;0.95" dur="0.4s" '
          f'begin="{round(0.2 + i * 0.05, 2)}s" fill="freeze"/></text>')
        for it, x, y, w in placed:
            begin = round(0.35 + i * 0.07, 3)
            i += 1
            a(f'<g opacity="0" transform="translate(0,6)">'
              f'<animate attributeName="opacity" values="0;1" dur="0.4s" begin="{begin}s" fill="freeze"/>'
              f'<animateTransform attributeName="transform" type="translate" '
              f'values="0 6;0 0" dur="0.4s" begin="{begin}s" fill="freeze" '
              f'calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>'
              f'<rect x="{x}" y="{y}" width="{w}" height="{PILL_H}" rx="13" '
              f'fill="{THEME["pill"]}" stroke="{THEME["mid"]}" stroke-opacity="0.45"/>'
              f'<text x="{x + w / 2}" y="{y + 18}" text-anchor="middle" font-family="{FONT}" '
              f'font-size="12" fill="{THEME["text"]}">{html.escape(it)}</text></g>')

    # altta soldan saga gecen isik cizgisi
    a(f'<rect x="{PAD}" y="{height - 10}" width="120" height="2" rx="1" fill="url(#sg)" '
      f'filter="url(#sglow)" opacity="0.75">'
      f'<animate attributeName="x" values="{PAD};{width - PAD - 120};{PAD}" dur="6s" '
      f'begin="{round(0.35 + i * 0.07 + 0.3, 2)}s" repeatCount="indefinite" '
      f'calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1" keyTimes="0;0.5;1"/></rect>')
    a("</svg>")

    with open(out, "w", encoding="utf-8") as f:
        f.write("".join(p))
    print(f"{out}: {width}x{height}px, {i} rozet")


if __name__ == "__main__":
    build()

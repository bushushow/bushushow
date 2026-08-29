#!/usr/bin/env python3
"""Fotograftan animasyonlu ASCII portre SVG'si uretir.

Adimlar: kirp -> rembg ile arka plani sil -> CLAHE ile kontrast -> ASCII -> SMIL animasyonlu SVG
"""
import argparse
import html
import os

import cv2
import numpy as np
from PIL import Image

# Seyrekten yoguna karakter rampasi
RAMP = " .`:-=+*cs#%@"

THEME = {
    "bg": "#12071f",
    "dim": "#6b3fa0",
    "mid": "#a855f7",
    "hot": "#e879f9",
    "glow": "#c084fc",
}


def load_and_cut(path, crop=None, model="u2netp"):
    im = Image.open(path).convert("RGB")
    if crop:
        im = im.crop(crop)
    # buyuk fotograflar rembg'i gereksiz yoruyor, once kucult
    im.thumbnail((900, 900), Image.LANCZOS)
    from rembg import new_session, remove

    cut = remove(im, session=new_session(model))  # RGBA
    # siluetin sinir kutusuna kirp: kare fotograftaki bos kenarlar ASCII'yi kaydiriyor
    bbox = cut.split()[-1].point(lambda v: 255 if v > 40 else 0).getbbox()
    if bbox:
        m = 6
        l, t, r, b = bbox
        cut = cut.crop((max(0, l - m), max(0, t - m),
                        min(cut.width, r + m), min(cut.height, b + m)))
    return cut


def to_ascii(rgba, cols=74, char_aspect=0.60, invert=True, alpha_thresh=40,
             detail=0.14, clahe_clip=3.2, gamma=1.0, contrast=0.0):
    rgb = np.array(rgba.convert("RGB"))
    alpha = np.array(rgba.split()[-1])

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # duz siyah kumas tek karakterde eziliyor: yerel detayi geri ekle
    if detail > 0:
        g = gray.astype(np.float32)
        blur = cv2.GaussianBlur(g, (0, 0), sigmaX=max(2, min(gray.shape) / 28))
        hi = g - blur
        hi = hi / (np.abs(hi).max() + 1e-5)
        gray = np.clip(g + hi * 255 * detail, 0, 255).astype(np.uint8)

    h, w = gray.shape
    rows = max(1, int(cols * (h / w) * char_aspect))

    gray_s = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_AREA)
    alpha_s = cv2.resize(alpha, (cols, rows), interpolation=cv2.INTER_AREA)

    mask = alpha_s > alpha_thresh
    if mask.sum() == 0:
        mask = np.ones_like(alpha_s, dtype=bool)

    vals = gray_s[mask].astype(np.float32)
    lo, hi = np.percentile(vals, 4), np.percentile(vals, 96)
    norm = np.clip((gray_s.astype(np.float32) - lo) / max(1e-5, hi - lo), 0, 1)
    if gamma and gamma != 1.0:
        norm = norm ** gamma
    if contrast:
        # yumusak S-egrisi: orta tonlari acar, uclari sikistirir
        norm = np.clip(0.5 + (norm - 0.5) * (1 + contrast), 0, 1)
    if invert:
        norm = 1.0 - norm

    idx = np.clip((norm * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    idx[~mask] = 0

    lines = ["".join(RAMP[i] for i in row).rstrip() for row in idx]
    # bastaki / sondaki bos satirlari at
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def build_svg(lines, out, char_w=8.4, line_h=14.0, font_size=13, pad=26,
              row_delay=0.055, cursor=True):
    cols = max(len(l) for l in lines)
    rows = len(lines)
    w = int(cols * char_w + pad * 2)
    h = int(rows * line_h + pad * 2 + 26)
    total = rows * row_delay + 1.2

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="ASCII portrait">'
    )
    parts.append(
        "<defs>"
        f'<linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{THEME["hot"]}"/>'
        f'<stop offset="55%" stop-color="{THEME["mid"]}"/>'
        f'<stop offset="100%" stop-color="{THEME["dim"]}"/>'
        "</linearGradient>"
        '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%">'
        '<feGaussianBlur stdDeviation="0.55" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        "</filter>"
        "</defs>"
    )
    parts.append(
        f'<rect width="{w}" height="{h}" rx="14" fill="{THEME["bg"]}" '
        f'stroke="{THEME["dim"]}" stroke-opacity="0.55"/>'
    )
    # pencere noktalari
    for i, c in enumerate([THEME["hot"], THEME["glow"], THEME["mid"]]):
        parts.append(f'<circle cx="{22 + i * 16}" cy="20" r="5" fill="{c}" opacity="0.85"/>')
    parts.append(
        f'<text x="{w - 16}" y="24" text-anchor="end" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" '
        f'font-size="11" fill="{THEME["glow"]}" opacity="0.6">portrait.ascii</text>'
    )

    y0 = pad + 26
    parts.append(
        f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="{font_size}" fill="url(#pg)" filter="url(#soft)" '
        f'xml:space="preserve" style="white-space:pre" letter-spacing="0">'
    )
    for i, line in enumerate(lines):
        begin = round(i * row_delay, 3)
        y = round(y0 + i * line_h, 2)
        parts.append(
            f'<text x="{pad}" y="{y}" xml:space="preserve" opacity="0">'
            # bosluklar SVG'de sikistirilmasin diye kirilmaz bosluk kullaniliyor
            f'{html.escape(line).replace(" ", chr(160))}'
            f'<animate attributeName="opacity" values="0;1" dur="0.45s" '
            f'begin="{begin}s" fill="freeze"/>'
            "</text>"
        )
    parts.append("</g>")

    if cursor:
        parts.append(
            f'<rect x="{pad}" y="{y0 + rows * line_h - 10}" width="9" height="14" '
            f'fill="{THEME["hot"]}">'
            f'<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>'
            "</rect>"
        )
    parts.append("</svg>")

    with open(out, "w", encoding="utf-8") as f:
        f.write("".join(parts))
    return w, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="assets/source.jpg")
    ap.add_argument("--out", default="assets/portrait.svg")
    ap.add_argument("--cols", type=int, default=74)
    ap.add_argument("--crop", default="")  # "l,t,r,b"
    ap.add_argument("--cutout", default="assets/cutout.png")
    ap.add_argument("--model", default="u2netp")
    ap.add_argument("--no-invert", action="store_true",
                    help="parlak alanlari yogun karakterle ciz (aydinlik portreler icin)")
    ap.add_argument("--detail", type=float, default=0.14)
    ap.add_argument("--clahe", type=float, default=3.2)
    ap.add_argument("--aspect", type=float, default=0.60)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--contrast", type=float, default=0.0)
    args = ap.parse_args()

    crop = tuple(int(x) for x in args.crop.split(",")) if args.crop else None
    cut = load_and_cut(args.src, crop, args.model)
    if args.cutout:
        os.makedirs(os.path.dirname(args.cutout), exist_ok=True)
        cut.save(args.cutout)
    lines = to_ascii(cut, cols=args.cols, invert=not args.no_invert,
                     detail=args.detail, clahe_clip=args.clahe,
                     char_aspect=args.aspect, gamma=args.gamma,
                     contrast=args.contrast)
    w, h = build_svg(lines, args.out)
    print(f"{args.out}: {len(lines)} satir, {w}x{h}px")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

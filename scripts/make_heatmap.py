#!/usr/bin/env python3
"""GitHub katki grafigini token'siz cekip capraz acilan animasyonlu SVG uretir.

Herkese acik profil HTML'i kazinir, token gerekmez.
"""
import argparse
import datetime as dt
import html
import os
import re

import requests
from bs4 import BeautifulSoup

THEME = {
    "bg": "#12071f",
    "dim": "#6b3fa0",
    "mid": "#a855f7",
    "hot": "#e879f9",
    "glow": "#c084fc",
    "text": "#e9d5ff",
    "muted": "#9a7fc0",
    "empty": "#241436",
}
# 0 -> 4 yogunluk skalasi (mor/neon)
SCALE = ["#241436", "#4c1d95", "#7e22ce", "#a855f7", "#e879f9"]

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
CELL = 11
GAP = 3
PAD = 26
TOP = 74

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


GRAPHQL = """
query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_days_api(user, token):
    """GITHUB_TOKEN varsa GraphQL API'den cek (Actions icinde en guvenilir yol)."""
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": GRAPHQL, "variables": {"login": user}},
        headers={"Authorization": f"bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    weeks = (data["data"]["user"]["contributionsCollection"]
             ["contributionCalendar"]["weeks"])
    return [(d["date"], d["contributionCount"], None)
            for w in weeks for d in w["contributionDays"]]


def demo_days(seed=7):
    """Yerel onizleme icin sahte veri (gercek profil verisi degildir)."""
    import math
    import random
    rnd = random.Random(seed)
    end = dt.date.today()
    start = end - dt.timedelta(days=364)
    out = []
    for i in range((end - start).days + 1):
        d = start + dt.timedelta(days=i)
        base = 4 + 4 * math.sin(i / 46.0)
        if d.weekday() >= 5:
            base *= 0.45
        c = max(0, int(rnd.gauss(base, 3)))
        if rnd.random() < 0.18:
            c = 0
        out.append((d.isoformat(), c, None))
    return out


def fetch_days(user, year=None):
    """(date, count, level) listesi dondurur (HTML kazima)."""
    url = f"https://github.com/users/{user}/contributions"
    if year:
        url += f"?from={year}-01-01&to={year}-12-31"
    r = requests.get(url, timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (profile-readme-generator)",
        "X-Requested-With": "XMLHttpRequest",
    })
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue
        level = td.get("data-level")
        count = 0
        # yeni GitHub HTML'inde sayilar ayri bir tooltip/span icinde durabiliyor
        txt = td.get("aria-label") or td.get_text(" ", strip=True) or ""
        m = re.search(r"(\d+)\s+contribution", txt)
        if m:
            count = int(m.group(1))
        elif "No contribution" in txt:
            count = 0
        elif level is not None:
            count = int(level)  # sayilamadiysa seviyeyi kaba tahmin olarak kullan
        days.append((date, count, int(level) if level is not None else None))

    if not days:
        # tooltip'ler ayri <tool-tip> elemanlarinda olabilir
        tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
        for td in soup.select("td.ContributionCalendar-day"):
            date = td.get("data-date")
            if not date:
                continue
            txt = tips.get(td.get("id"), "")
            m = re.search(r"(\d+)\s+contribution", txt)
            days.append((date, int(m.group(1)) if m else 0,
                         int(td.get("data-level") or 0)))
    days.sort(key=lambda d: d[0])
    return days


def level_of(count, level_hint, thresholds):
    if level_hint is not None:
        return max(0, min(4, level_hint))
    for i, t in enumerate(thresholds):
        if count <= t:
            return i
    return 4


def build_svg(days, user, out, weeks_back=53):
    if not days:
        raise SystemExit("Katki verisi bulunamadi.")

    counts = [c for _, c, _ in days if c > 0]
    counts.sort()
    if counts:
        q = lambda p: counts[min(len(counts) - 1, int(len(counts) * p))]
        thresholds = [0, q(0.35), q(0.65), q(0.88)]
    else:
        thresholds = [0, 1, 3, 6]

    first = dt.date.fromisoformat(days[0][0])
    # ilk sutunu pazar gunune hizala (GitHub haftalari pazar baslar)
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)

    cols = {}
    for date, count, lvl in days:
        d = dt.date.fromisoformat(date)
        col = (d - start).days // 7
        row = (d.weekday() + 1) % 7
        cols.setdefault(col, {})[row] = (d, count, lvl)

    n_cols = max(cols) + 1
    grid_w = n_cols * (CELL + GAP) - GAP
    grid_h = 7 * (CELL + GAP) - GAP
    left = PAD + 30  # gun etiketleri icin yer
    width = left + grid_w + PAD
    height = TOP + grid_h + 58

    total = sum(c for _, c, _ in days)
    # en uzun seri
    streak = best = 0
    for _, c, _ in days:
        streak = streak + 1 if c > 0 else 0
        best = max(best, streak)

    p = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
      f'viewBox="0 0 {width} {height}" role="img" aria-label="Contribution heatmap">')
    a("<defs>"
      f'<linearGradient id="hg" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0%" stop-color="{THEME["hot"]}"/>'
      f'<stop offset="100%" stop-color="{THEME["mid"]}"/></linearGradient>'
      '<filter id="hglow" x="-40%" y="-40%" width="180%" height="180%">'
      '<feGaussianBlur stdDeviation="1.8" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
      "</filter></defs>")
    a(f'<rect width="{width}" height="{height}" rx="14" fill="{THEME["bg"]}" '
      f'stroke="{THEME["dim"]}" stroke-opacity="0.55"/>')
    for i, c in enumerate([THEME["hot"], THEME["glow"], THEME["mid"]]):
        a(f'<circle cx="{22 + i * 16}" cy="20" r="5" fill="{c}" opacity="0.85"/>')
    a(f'<text x="{width - 16}" y="24" text-anchor="end" font-family="{FONT}" font-size="11" '
      f'fill="{THEME["glow"]}" opacity="0.6">git log --graph</text>')

    a(f'<text x="{PAD}" y="50" font-family="{FONT}" font-size="13" fill="{THEME["muted"]}">'
      f'<tspan fill="{THEME["hot"]}">{html.escape(user)}</tspan>'
      f'<tspan> · contribution activity · last 12 months</tspan></text>')

    # ay etiketleri
    seen = set()
    for col in sorted(cols):
        entry = cols[col].get(0) or next(iter(cols[col].values()))
        d = entry[0]
        key = (d.year, d.month)
        if d.day <= 7 and key not in seen:
            seen.add(key)
            x = left + col * (CELL + GAP)
            a(f'<text x="{x}" y="{TOP - 8}" font-family="{FONT}" font-size="10" '
              f'fill="{THEME["muted"]}" opacity="0.75">{MONTHS[d.month - 1]}</text>')

    for row, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = TOP + row * (CELL + GAP) + CELL - 1
        a(f'<text x="{PAD}" y="{y}" font-family="{FONT}" font-size="9" '
          f'fill="{THEME["muted"]}" opacity="0.75">{lab}</text>')

    max_diag = n_cols + 7
    span = 2.4  # saniye
    for col in sorted(cols):
        for row, (d, count, lvl) in cols[col].items():
            lv = level_of(count, lvl, thresholds)
            x = left + col * (CELL + GAP)
            y = TOP + row * (CELL + GAP)
            begin = round((col + row) / max_diag * span, 3)
            fill = SCALE[lv]
            extra = ' filter="url(#hglow)"' if lv == 4 else ""
            a(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
              f'fill="{fill}"{extra} opacity="0">'
              f'<title>{d.isoformat()}: {count} contributions</title>'
              f'<animate attributeName="opacity" values="0;1" dur="0.5s" '
              f'begin="{begin}s" fill="freeze"/>'
              f'<animate attributeName="rx" values="5.5;2.5" dur="0.5s" '
              f'begin="{begin}s" fill="freeze"/></rect>')

    # lejant
    ly = TOP + grid_h + 26
    a(f'<text x="{left}" y="{ly + 10}" font-family="{FONT}" font-size="10" '
      f'fill="{THEME["muted"]}">less</text>')
    for i, c in enumerate(SCALE):
        a(f'<rect x="{left + 34 + i * 15}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    a(f'<text x="{left + 34 + len(SCALE) * 15 + 4}" y="{ly + 10}" font-family="{FONT}" '
      f'font-size="10" fill="{THEME["muted"]}">more</text>')
    a(f'<text x="{width - PAD}" y="{ly + 10}" text-anchor="end" font-family="{FONT}" '
      f'font-size="10" fill="{THEME["muted"]}" opacity="0.7">'
      f'updated {dt.date.today().isoformat()}</text>')
    a("</svg>")

    with open(out, "w", encoding="utf-8") as f:
        f.write("".join(p))
    print(f"{out}: {width}x{height}px, {len(days)} gun, {total} katki")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="bushushow")
    ap.add_argument("--out", default="assets/heatmap.svg")
    ap.add_argument("--demo", action="store_true",
                    help="ag erisimi olmadan sahte veriyle onizleme uret")
    args = ap.parse_args()

    if args.demo:
        days = demo_days()
    else:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        days = None
        if token:
            try:
                days = fetch_days_api(args.user, token)
            except Exception as e:  # noqa: BLE001
                print(f"GraphQL basarisiz ({e}), HTML kazimaya geciliyor.")
        if not days:
            days = fetch_days(args.user)

    build_svg(days, args.user, args.out)


if __name__ == "__main__":
    main()

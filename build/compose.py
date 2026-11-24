#!/usr/bin/env python3
"""Typeset the front page for Tuesday 24 November 2026 (news-image-20261124).

A single 1024x1024 broadsheet in the dense front-page format: giant date
masthead, numbers strip, region chips, UTC timeline, 3 illustrated lead
cards, 4 illustrated second-row cards, 11 briefs (7 illustrated) + a sport
card, a real world map with numbered pins, a 16-item "also on Tuesday" list,
a DATE CHECK box and a sources footer. 34 verified same-day stories, 6
regions, 14 informative illustrations. Every picture and the map are drawn
in code with Pillow; no network, no photos, no timestamps in the output,
so the render is byte-deterministic.

Run from anywhere; writes entry/entry.png and full.png in this workdir.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WORKDIR = Path(__file__).resolve().parents[1]      # news-image-20261124/
OUT_PNG = WORKDIR / "entry" / "entry.png"
PREVIEW_PNG = WORKDIR / "full.png"

# ---------------------------------------------------------------- palette
PAPER = (245, 240, 228)
INK = (22, 22, 20)
CRIMSON = (176, 32, 28)
NAVY = (20, 36, 76)
NAVY2 = (28, 48, 96)
GOLD = (198, 152, 58)
GOLD_LT = (240, 190, 90)
MUTED = (106, 100, 88)
CREAM_BOX = (235, 227, 205)
HAIR = (188, 181, 160)
TEAL = (14, 110, 110)
GREEN = (44, 122, 76)
AMBER = (176, 116, 10)
PURPLE = (96, 66, 140)
SLATE = (88, 105, 138)
SKY = (214, 228, 238)
SEA = (27, 47, 82)

REGION_COLORS = {
    "EUROPE": CRIMSON,
    "ASIA-PACIFIC": TEAL,
    "AMERICAS": NAVY2,
    "MIDDLE EAST": AMBER,
    "AFRICA": GREEN,
    "OCEANIA": PURPLE,
}

W, H = 1024, 1024
M = 24
R = W - M            # 1000
CW = R - M           # 976

# ------------------------------------------------------------------- fonts
NOTO = "/usr/share/fonts/truetype/noto/"
LIB = "/usr/share/fonts/truetype/liberation/"
_FONT_FILES = {
    "mast": "NotoSerif-Black.ttf",
    "serif": "NotoSerif-Regular.ttf",
    "serif-bold": "NotoSerif-Bold.ttf",
    "serif-italic": "NotoSerif-Italic.ttf",
    "sans": "NotoSans-Regular.ttf",
    "sans-bold": "NotoSans-Bold.ttf",
    "sans-cond": "NotoSans-Condensed.ttf",
    "sans-cond-bold": "NotoSans-CondensedBold.ttf",
    "sans-italic": "NotoSans-Italic.ttf",
}
_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def typeface(kind: str, size: int) -> ImageFont.FreeTypeFont:
    key = (kind, size)
    if key in _cache:
        return _cache[key]
    name = _FONT_FILES[kind]
    for folder in (NOTO, LIB):
        p = Path(folder) / name
        if p.exists():
            face = ImageFont.truetype(str(p), size)
            _cache[key] = face
            return face
    face = ImageFont.load_default()
    _cache[key] = face
    return face


def fitted(draw, text, kind, start, width):
    size = start
    while size > 8 and draw.textlength(text, font=typeface(kind, size)) > width:
        size -= 1
    return typeface(kind, size)


def wrap(draw, text, face, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if not cur or draw.textlength(trial, font=face) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, face, fill, width, leading):
    for line in wrap(draw, text, face, width):
        draw.text((x, y), line, font=face, fill=fill)
        y += leading
    return y


def chip(draw, x, y, label, face, bg, fg=(255, 255, 255), pad_x=6, pad_y=3):
    tw = int(draw.textlength(label, font=face))
    h = face.size + 2 * pad_y
    draw.rectangle([x, y, x + tw + 2 * pad_x, y + h], fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), label, font=face, fill=fg)
    return x + tw + 2 * pad_x, y + h


def pill(draw, x, y, label, face, bg):
    tw = int(draw.textlength(label, font=face))
    w = tw + 10
    h = face.size + 5
    draw.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=bg)
    draw.text((x + 5, y + 2), label, font=face, fill=(255, 255, 255))
    return x + w


def rule(draw, x0, x1, y, weight=1, fill=INK):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


def num_badge(draw, x, y, n, color, size=13):
    """Numbered circle used on cards and the map."""
    r = size
    draw.ellipse([x - r, y - r, x + r, y + r], fill=color,
                 outline=(255, 255, 255), width=2)
    f = typeface("sans-cond-bold", size + 2 if size <= 13 else size)
    tw = draw.textlength(str(n), font=f)
    th = f.size
    draw.text((x - tw / 2, y - th / 2 - 1), str(n), font=f,
              fill=(255, 255, 255))

# ------------------------------------------------------- illustrations
# Each painter draws a small flat, FACT-CARRYING scene into a box
# (x, y, w, h). Positions are fractions of the box so every painter works
# at any slot size; text sizes are chosen per painter for its slot.

def ill_zaporizhzhia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 24, 46))          # night sky
    for sx, sy in [(0.04, 0.11), (0.13, 0.06), (0.28, 0.15), (0.47, 0.08),
                   (0.63, 0.13), (0.79, 0.06), (0.91, 0.16), (0.19, 0.24),
                   (0.57, 0.22)]:
        d.ellipse([x + sx * w, y + sy * h, x + sx * w + 2, y + sy * h + 2],
                  fill=(230, 230, 200))
    # damaged five-storey block
    bx, by, bw, bh = x + 0.10 * w, y + h - 0.70 * h, 0.47 * w, 0.70 * h
    d.polygon([(bx, by + bh), (bx, by + 0.16 * h), (bx + 0.27 * bw, by),
               (bx + 0.47 * bw, by + 0.12 * h), (bx + 0.73 * bw, by + 0.04 * h),
               (bx + bw, by + 0.14 * h), (bx + bw, by + bh)],
              fill=(120, 116, 108))
    for fl in range(5):
        for wi in range(4):
            wx = bx + 0.08 * bw + wi * 0.24 * bw
            wy = by + 0.12 * h + fl * 0.125 * h
            lit = (fl, wi) not in [(0, 1), (1, 2), (2, 0)]
            d.rectangle([wx, wy, wx + 0.12 * bw, wy + 0.08 * h],
                        fill=(240, 190, 90) if lit else (40, 38, 34))
    # rubble + searchlight beam
    d.polygon([(x + 0.66 * w, y + h - 0.36 * h), (x + 0.82 * w, y + h - 0.36 * h),
               (x + 0.90 * w, y + h), (x + 0.63 * w, y + h)], fill=(70, 66, 60))
    d.polygon([(x + w - 0.09 * w, y + h), (x + w - 0.28 * w, y + 0.08 * h),
               (x + w - 0.22 * w, y + 0.08 * h), (x + w - 0.04 * w, y + h)],
              fill=(240, 220, 140))
    d.text((x + 0.03 * w, y + 0.05 * h), "2 KILLED",
           font=typeface("sans-cond-bold", 26), fill=(255, 255, 255))
    d.text((x + 0.03 * w, y + 0.30 * h), "40+ HURT",
           font=typeface("sans-cond-bold", 15), fill=(240, 190, 90))


def ill_kerch(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 205, 222))       # sky
    d.rectangle([x, y + 0.54 * h, x + w, y + h], fill=(46, 92, 128))  # strait
    for i in range(6):  # waves
        wx = x + (0.04 + i * 0.16) * w
        d.arc([wx, y + h - 0.40 * h, wx + 0.09 * w, y + h - 0.27 * h],
              200, 340, fill=(200, 225, 240), width=2)
    # bridge deck, left and right of the fallen span
    d.rectangle([x, y + 0.46 * h, x + 0.41 * w, y + 0.55 * h], fill=(90, 90, 96))
    d.rectangle([x + 0.59 * w, y + 0.46 * h, x + w, y + 0.55 * h],
                fill=(90, 90, 96))
    for tx in (0.13, 0.81):  # towers
        d.rectangle([x + tx * w, y + 0.16 * h, x + tx * w + 6, y + 0.55 * h],
                    fill=(70, 70, 78))
        d.line([x + tx * w + 3, y + 0.16 * h, x + (tx - 0.10) * w, y + 0.46 * h],
               fill=(70, 70, 78), width=2)
        d.line([x + tx * w + 3, y + 0.16 * h, x + (tx + 0.10) * w, y + 0.46 * h],
               fill=(70, 70, 78), width=2)
    # fallen 227-m span, tilted into the water
    d.polygon([(x + 0.42 * w, y + 0.50 * h), (x + 0.56 * w, y + 0.66 * h),
               (x + 0.54 * w, y + 0.82 * h), (x + 0.40 * w, y + 0.70 * h)],
              fill=(60, 60, 68))
    d.ellipse([x + 0.50 * w, y + 0.71 * h, x + 0.60 * w, y + 0.86 * h],
              fill=(255, 255, 255))
    d.ellipse([x + 0.53 * w, y + 0.75 * h, x + 0.57 * w, y + 0.82 * h],
              fill=(46, 92, 128))
    d.text((x + 0.03 * w, y + 0.05 * h), "SPAN DOWN",
           font=typeface("sans-cond-bold", 24), fill=(255, 255, 255))
    d.rectangle([x + 0.03 * w, y + 0.29 * h, x + 0.24 * w, y + 0.45 * h],
                fill=CRIMSON)
    d.text((x + 0.05 * w, y + 0.30 * h), "227 m",
           font=typeface("sans-cond-bold", 15), fill=(255, 255, 255))


def ill_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 240, 232))
    d.text((x + 0.03 * w, y + 0.04 * h), "ASIA REBOUNDS",
           font=typeface("sans-cond-bold", 14), fill=INK)
    d.line([x + 0.09 * w, y + h - 0.23 * h, x + w - 0.03 * w, y + h - 0.23 * h],
           fill=INK, width=2)
    bars = [("KOSPI", 7.3, 0.62), ("TAIEX", 9.1, 0.78), ("NIKKEI", 3.9, 0.34)]
    bw = 0.20 * w
    bx = x + 0.13 * w
    for name, val, frac in bars:
        bh = (h - 0.55 * h) * frac
        d.rectangle([bx, y + h - 0.23 * h - bh, bx + bw, y + h - 0.23 * h],
                    fill=(18, 122, 62))
        f = typeface("sans-cond-bold", 20)
        tw = d.textlength(f"+{val}%", font=f)
        d.text((bx + (bw - tw) / 2, y + h - 0.23 * h - bh - 24), f"+{val}%",
               font=f, fill=(18, 122, 62))
        lf = typeface("sans-cond-bold", 12)
        tw = d.textlength(name, font=lf)
        d.text((bx + (bw - tw) / 2, y + h - 0.20 * h), name, font=lf, fill=INK)
        bx += bw + 0.11 * w


def ill_shenzhou(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 16, 40))          # space
    for sx, sy in [(0.08, 0.14), (0.29, 0.30), (0.63, 0.12), (0.88, 0.26),
                   (0.46, 0.45), (0.17, 0.58), (0.95, 0.55)]:
        d.ellipse([x + sx * w, y + sy * h, x + sx * w + 2, y + sy * h + 2],
                  fill=(230, 230, 200))
    # Tiangong modules, left
    d.rectangle([x + 0.17 * w, y + 0.30 * h, x + 0.63 * w, y + 0.48 * h],
                fill=(200, 200, 205))
    d.rectangle([x + 0.63 * w, y + 0.24 * h, x + 0.88 * w, y + 0.55 * h],
                fill=(170, 170, 178))
    d.rectangle([x + 0.13 * w, y + 0.19 * h, x + 0.18 * w, y + 0.60 * h],
                fill=(120, 125, 135))
    d.rectangle([x + 0.13 * w, y + 0.10 * h, x + 0.38 * w, y + 0.19 * h],
                fill=(90, 140, 200))
    d.rectangle([x + 0.13 * w, y + 0.60 * h, x + 0.38 * w, y + 0.69 * h],
                fill=(90, 140, 200))
    # rocket rising, right
    rx = x + 0.78 * w
    rw = 0.16 * w
    d.polygon([(rx + 0.25 * rw, y + h - 0.10 * h), (rx + 0.5 * rw, y + h - 0.40 * h),
               (rx + 0.75 * rw, y + h - 0.10 * h)], fill=(255, 170, 40))
    d.polygon([(rx, y + h - 0.10 * h), (rx + rw, y + h - 0.10 * h),
               (rx + 0.7 * rw, y + h - 0.36 * h)], fill=(255, 120, 30))
    d.rectangle([rx, y + 0.62 * h, rx + rw, y + h - 0.30 * h],
                fill=(235, 235, 240))
    d.polygon([(rx, y + 0.62 * h), (rx + 0.5 * rw, y + 0.40 * h),
               (rx + rw, y + 0.62 * h)], fill=CRIMSON)
    d.rectangle([rx, y + 0.82 * h, rx + rw, y + 0.90 * h], fill=CRIMSON)
    d.text((x + 0.03 * w, y + 0.05 * h), "1st FOREIGNER",
           font=typeface("sans-cond-bold", 20), fill=(255, 255, 255))
    # small flags: China red, Pakistan green
    d.rectangle([x + 0.03 * w, y + h - 0.24 * h, x + 0.15 * w, y + h - 0.10 * h],
                fill=(222, 41, 16))
    d.ellipse([x + 0.06 * w, y + h - 0.21 * h, x + 0.09 * w, y + h - 0.14 * h],
              fill=(255, 220, 0))
    d.rectangle([x + 0.17 * w, y + h - 0.24 * h, x + 0.29 * w, y + h - 0.10 * h],
                fill=(20, 90, 50))
    d.ellipse([x + 0.20 * w, y + h - 0.22 * h, x + 0.25 * w, y + h - 0.12 * h],
              fill=(255, 255, 255))
    d.ellipse([x + 0.215 * w, y + h - 0.22 * h, x + 0.25 * w, y + h - 0.12 * h],
              fill=(20, 90, 50))


def ill_kadiz(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 198, 224))       # sky
    d.ellipse([x + 0.84 * w, y + 0.14 * h, x + w, y + 0.36 * h],
              fill=(255, 255, 255))
    d.ellipse([x + 0.92 * w, y + 0.10 * h, x + 1.1 * w, y + 0.31 * h],
              fill=(255, 255, 255))
    # two jets
    for jx, jy, s in [(0.17, 0.36, 1.0), (0.50, 0.62, 0.8)]:
        ox, oy = x + jx * w, y + jy * h
        d.polygon([(ox, oy), (ox + 46 * s, oy + 8 * s),
                   (ox + 10 * s, oy + 12 * s)], fill=(60, 66, 74))
        d.polygon([(ox + 12 * s, oy + 2 * s), (ox + 22 * s, oy - 8 * s),
                   (ox + 28 * s, oy + 4 * s)], fill=(60, 66, 74))
    # Ulleung island + sea
    d.rectangle([x, y + h - 0.36 * h, x + w, y + h], fill=(46, 92, 128))
    d.polygon([(x + 0.38 * w, y + h - 0.36 * h), (x + 0.55 * w, y + h - 0.74 * h),
               (x + 0.72 * w, y + h - 0.36 * h)], fill=(90, 110, 80))
    d.polygon([(x + 0.50 * w, y + h - 0.57 * h), (x + 0.55 * w, y + h - 0.74 * h),
               (x + 0.60 * w, y + h - 0.57 * h)], fill=(240, 240, 235))
    for i in range(4):  # radar arcs
        r = 12 + i * 11
        cx, cy = x + w - 0.25 * w, y + h - 0.72 * h
        d.arc([cx - r, cy - r, cx + r, cy + r], 270, 20, fill=CRIMSON, width=2)
    d.text((x + 0.03 * w, y + 0.05 * h), "JETS SCRAMBLED",
           font=typeface("sans-cond-bold", 20), fill=INK)


def ill_ifo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 220))
    vals = [86.1, 87.0, 87.8, 88.4, 89.2, 89.9, 90.6]
    bw = 0.10 * w
    bx = x + 0.09 * w
    base = y + h - 0.28 * h
    top = y + 0.40 * h
    for i, v in enumerate(vals):
        frac = (v - 85.0) / (91.0 - 85.0)
        bh = (base - top) * frac
        col = NAVY if i < 6 else CRIMSON
        d.rectangle([bx, base - bh, bx + bw, base], fill=col)
        bx += bw + 0.025 * w
    d.line([x + 0.06 * w, base, x + w - 0.04 * w, base], fill=INK, width=2)
    d.text((x + 0.03 * w, y + 0.05 * h), "90.6",
           font=typeface("sans-cond-bold", 28), fill=CRIMSON)
    d.text((x + 0.36 * w, y + 0.14 * h), "7th RISE IN A ROW",
           font=typeface("sans-cond-bold", 13), fill=INK)
    d.text((x + 0.03 * w, y + h - 0.24 * h), "HIGHEST SINCE MAY 2023",
           font=typeface("sans-cond-bold", 10), fill=MUTED)


def ill_sanofi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 236, 244))
    # pill bottle
    bx = x + 0.13 * w
    d.rectangle([bx + 0.03 * w, y + 0.26 * h, bx + 0.10 * w, y + 0.40 * h],
                fill=(200, 60, 60))
    d.rectangle([bx, y + 0.40 * h, bx + 0.13 * w, y + h - 0.19 * h],
                fill=(250, 250, 248), outline=(120, 120, 120), width=2)
    d.rectangle([bx + 0.02 * w, y + 0.52 * h, bx + 0.11 * w, y + 0.74 * h],
                fill=(20, 36, 76))
    d.text((bx + 0.03 * w, y + 0.56 * h), "$41BN",
           font=typeface("sans-cond-bold", 14), fill=(255, 255, 255))
    # pills
    for px, py, pw in [(0.55, 0.62, 0.14), (0.70, 0.80, 0.14), (0.60, 0.95, 0.14)]:
        ox, oy = x + px * w, y + py * h
        d.ellipse([ox, oy, ox + pw * w, oy + 0.19 * h], fill=(240, 240, 235),
                  outline=CRIMSON, width=2)
        d.line([ox + 0.02 * w, oy + 0.09 * h, ox + pw * w - 0.02 * w,
                oy + 0.09 * h], fill=CRIMSON, width=2)
    d.text((x + 0.03 * w, y + 0.05 * h), "$41BN CASH",
           font=typeface("sans-cond-bold", 22), fill=INK)


def ill_nepal(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 234, 220))
    d.polygon([(x, y + h), (x + 0.26 * w, y + 0.30 * h), (x + 0.52 * w, y + h)],
              fill=(120, 130, 140))
    d.polygon([(x + 0.20 * w, y + h), (x + 0.52 * w, y + 0.16 * h),
               (x + 0.84 * w, y + h)], fill=(90, 100, 112))
    d.polygon([(x + 0.45 * w, y + 0.27 * h), (x + 0.52 * w, y + 0.16 * h),
               (x + 0.59 * w, y + 0.27 * h)], fill=(250, 250, 245))
    d.rectangle([x + 0.05 * w, y + h - 0.42 * h, x + w - 0.05 * w, y + h - 0.08 * h],
                fill=(255, 255, 255), outline=(120, 120, 120))
    pts = []
    px, py = x + 0.07 * w, y + h - 0.25 * h
    pts.append((px, py))
    for dx, dy in [(0.05, 0), (0.04, -0.02), (0.03, 0.03), (0.03, -0.10),
                   (0.03, 0.15), (0.03, -0.18), (0.03, 0.12), (0.03, -0.05),
                   (0.04, 0.02), (0.05, 0), (0.07, -0.04), (0.07, 0.04),
                   (0.08, 0), (0.05, -0.02), (0.05, 0.02), (0.07, 0)]:
        px += dx * w
        py += dy * h
        pts.append((px, py))
    d.line(pts, fill=CRIMSON, width=2)
    d.text((x + 0.05 * w, y + 0.03 * h), "M5.6",
           font=typeface("sans-cond-bold", 16), fill=INK)


def ill_rosstat(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 222))
    for r in range(2):
        for c in range(9):
            cx = x + (0.10 + c * 0.10) * w
            cy = y + (0.48 + r * 0.12) * h
            d.line([cx - 3, cy - 3, cx + 3, cy + 3], fill=(90, 86, 78), width=2)
            d.line([cx - 3, cy + 3, cx + 3, cy - 3], fill=(90, 86, 78), width=2)
    d.text((x + 0.05 * w, y + 0.03 * h), "490,000",
           font=typeface("sans-cond-bold", 20), fill=CRIMSON)
    d.text((x + 0.05 * w, y + h - 0.18 * h), "HACKED DATA",
           font=typeface("sans-cond-bold", 9), fill=MUTED)


def ill_energy(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 40))          # night
    for sx, sy in [(0.10, 0.12), (0.39, 0.24), (0.78, 0.14)]:
        d.ellipse([x + sx * w, y + sy * h, x + sx * w + 2, y + sy * h + 2],
                  fill=(230, 230, 200))
    px = x + 0.20 * w
    d.polygon([(px, y + h - 0.12 * h), (px + 0.07 * w, y + 0.36 * h),
               (px + 0.19 * w, y + 0.36 * h), (px + 0.26 * w, y + h - 0.12 * h)],
              fill=(70, 76, 88))
    d.line([px - 0.05 * w, y + 0.48 * h, px + 0.31 * w, y + 0.48 * h],
           fill=(70, 76, 88), width=3)
    d.polygon([(x + 0.66 * w, y + 0.17 * h), (x + 0.78 * w, y + 0.17 * h),
               (x + 0.71 * w, y + 0.52 * h), (x + 0.80 * w, y + 0.52 * h),
               (x + 0.62 * w, y + h - 0.10 * h), (x + 0.68 * w, y + 0.57 * h),
               (x + 0.60 * w, y + 0.57 * h)], fill=(240, 200, 60))
    d.rectangle([x + 0.62 * w, y + h - 0.40 * h, x + w - 0.08 * w, y + h - 0.12 * h],
                fill=(40, 44, 56))
    d.rectangle([x + 0.67 * w, y + h - 0.33 * h, x + 0.72 * w, y + h - 0.21 * h],
                fill=(240, 190, 90))
    d.text((x + 0.05 * w, y + 0.05 * h), "160+ HITS",
           font=typeface("sans-cond-bold", 18), fill=(255, 255, 255))


def ill_patriot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 224, 232))
    d.rectangle([x + 0.08 * w, y + h - 0.40 * h, x + w - 0.08 * w, y + h - 0.19 * h],
                fill=(70, 80, 70))
    for wx in (0.17, 0.39, 0.61, 0.83):
        d.ellipse([x + wx * w, y + h - 0.21 * h, x + wx * w + 0.08 * w,
                   y + h - 0.07 * h], fill=INK)
    d.polygon([(x + 0.20 * w, y + h - 0.43 * h), (x + 0.78 * w, y + 0.26 * h),
               (x + 0.83 * w, y + 0.36 * h), (x + 0.25 * w, y + h - 0.33 * h)],
              fill=(200, 205, 210), outline=(60, 60, 60))
    d.polygon([(x + 0.78 * w, y + 0.26 * h), (x + 0.86 * w, y + 0.36 * h),
               (x + 0.81 * w, y + 0.45 * h)], fill=CRIMSON)
    d.text((x + 0.05 * w, y + 0.05 * h), "60 WAITING",
           font=typeface("sans-cond-bold", 16), fill=INK)


def ill_spy(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 230, 218))
    d.rectangle([x + 0.12 * w, y + 0.31 * h, x + 0.60 * w, y + h - 0.12 * h],
                fill=(255, 255, 255), outline=(120, 120, 120))
    for i in range(3):
        d.line([x + 0.17 * w, y + (0.45 + i * 0.14) * h, x + 0.55 * w,
                y + (0.45 + i * 0.14) * h], fill=(150, 150, 150), width=2)
    d.rectangle([x + 0.17 * w, y + 0.45 * h, x + 0.34 * w, y + 0.55 * h],
                fill=CRIMSON)
    d.rectangle([x + 0.70 * w, y + 0.71 * h, x + 0.86 * w, y + 0.90 * h],
                fill=(120, 84, 50))
    d.rectangle([x + 0.65 * w, y + 0.62 * h, x + 0.91 * w, y + 0.74 * h],
                fill=(150, 110, 66))
    d.line([x + 0.78 * w, y + 0.90 * h, x + 0.78 * w, y + h - 0.14 * h],
           fill=(120, 84, 50), width=4)
    d.rectangle([x + 0.62 * w, y + h - 0.14 * h, x + 0.94 * w, y + h - 0.07 * h],
                fill=(150, 110, 66))
    d.text((x + 0.05 * w, y + 0.05 * h), "DEATH SENTENCE",
           font=typeface("sans-cond-bold", 15), fill=INK)


def ill_megaspeed(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 32, 38))
    d.rectangle([x + 0.31 * w, y + 0.26 * h, x + 0.73 * w, y + h - 0.26 * h],
                fill=(16, 16, 20), outline=(120, 120, 130), width=2)
    d.rectangle([x + 0.40 * w, y + 0.43 * h, x + 0.64 * w, y + h - 0.43 * h],
                fill=(60, 90, 60))
    for i in range(3):
        yy = y + (0.38 + i * 0.14) * h
        d.line([x + 0.31 * w, yy, x + 0.22 * w, yy], fill=(180, 180, 190), width=2)
        d.line([x + 0.73 * w, yy, x + 0.82 * w, yy], fill=(180, 180, 190), width=2)
    d.rectangle([x + 0.05 * w, y + h - 0.31 * h, x + w - 0.05 * w, y + h - 0.10 * h],
                fill=CRIMSON)
    d.text((x + 0.08 * w, y + h - 0.30 * h), "BLACKLISTED",
           font=typeface("sans-cond-bold", 11), fill=(255, 255, 255))
    d.text((x + 0.05 * w, y + 0.05 * h), "CHIP FIRM",
           font=typeface("sans-cond-bold", 15), fill=(255, 255, 255))


def ill_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 220, 204))
    d.rectangle([x + 0.06 * w, y + 0.48 * h, x + 0.30 * w, y + h - 0.10 * h],
                fill=(140, 134, 122))
    d.polygon([(x + 0.36 * w, y + 0.36 * h), (x + 0.48 * w, y + 0.21 * h),
               (x + 0.60 * w, y + 0.36 * h), (x + 0.60 * w, y + h - 0.10 * h),
               (x + 0.36 * w, y + h - 0.10 * h)], fill=(110, 106, 96))
    d.rectangle([x + 0.66 * w, y + 0.57 * h, x + 0.90 * w, y + h - 0.10 * h],
                fill=(160, 154, 140))
    for wx in (0.10, 0.20, 0.42, 0.52, 0.72, 0.80):
        d.rectangle([x + wx * w, y + 0.62 * h, x + wx * w + 0.05 * w,
                     y + 0.71 * h], fill=(60, 56, 50))
    d.rectangle([x + w - 0.26 * w, y + 0.55 * h, x + w - 0.05 * w, y + 0.81 * h],
                fill=(40, 90, 160))
    d.text((x + w - 0.22 * w, y + 0.57 * h), "UN",
           font=typeface("sans-cond-bold", 12), fill=(255, 255, 255))
    d.text((x + 0.05 * w, y + 0.05 * h), "3 KILLED",
           font=typeface("sans-cond-bold", 17), fill=CRIMSON)


# ------------------------------------------------------------------- map
# Simplified continent outlines in (lon, lat); drawn equirectangular.

CONTINENTS = [
    # North America
    [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 57),
     (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
     (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
     (-80, 8), (-78, 7), (-80, 10), (-83, 15), (-87, 16), (-90, 21),
     (-87, 21), (-84, 30), (-81, 25), (-80, 32), (-76, 35), (-74, 40),
     (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 47), (-60, 52),
     (-65, 58), (-68, 58), (-75, 62), (-78, 62), (-85, 66), (-92, 66),
     (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68)],
    # Greenland
    [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
     (-25, 74), (-30, 76), (-40, 78), (-58, 76), (-60, 74), (-58, 70)],
    # South America
    [(-78, 7), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
     (-66, -55), (-68, -50), (-65, -45), (-62, -41), (-58, -35), (-52, -32),
     (-48, -28), (-41, -23), (-38, -15), (-35, -9), (-35, -6), (-40, -3),
     (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
     (-72, 12), (-75, 10)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-16, 12),
     (-13, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, -1),
     (12, -5), (13, -10), (12, -17), (14, -22), (16, -28), (19, -34),
     (26, -34), (28, -32), (32, -28), (35, -24), (40, -16), (40, -10),
     (42, -4), (46, -1), (51, 2), (51, 11), (48, 11), (44, 11), (40, 15),
     (38, 18), (37, 22), (34, 27), (32, 31), (30, 31), (25, 32), (19, 33),
     (15, 32), (11, 34), (10, 37), (5, 37), (0, 36)],
    # Eurasia
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 49),
     (0, 50), (2, 51), (5, 53), (8, 55), (8, 57), (10, 58), (12, 56),
     (18, 56), (21, 59), (24, 60), (28, 62), (30, 65), (25, 70), (20, 70),
     (18, 69), (15, 66), (12, 62), (10, 58), (5, 58), (5, 60), (8, 62),
     (12, 64), (18, 64), (24, 64), (30, 64), (32, 66), (35, 66), (40, 66),
     (45, 67), (50, 68), (55, 68), (60, 69), (70, 72), (80, 73), (90, 75),
     (100, 76), (110, 74), (120, 73), (130, 72), (140, 72), (150, 72),
     (160, 70), (170, 70), (178, 68), (178, 65), (170, 66), (170, 60),
     (162, 60), (162, 56), (158, 52), (156, 59), (150, 60), (142, 59),
     (140, 55), (142, 52), (141, 50), (138, 46), (135, 44), (132, 43),
     (130, 42), (128, 38), (126, 38), (129, 35), (127, 34), (126, 36),
     (124, 40), (122, 38), (120, 34), (122, 31), (120, 28), (118, 25),
     (114, 22), (110, 21), (108, 21), (106, 20), (109, 16), (109, 13),
     (106, 10), (105, 9), (103, 7), (100, 8), (98, 10), (97, 16), (94, 17),
     (92, 16), (91, 22), (88, 22), (85, 19), (80, 13), (80, 7), (77, 8),
     (75, 15), (72, 20), (70, 20), (66, 25), (62, 25), (58, 24), (58, 20),
     (55, 17), (50, 16), (45, 12), (43, 12), (39, 21), (36, 29), (34, 31),
     (36, 36), (33, 36), (30, 36), (28, 37), (26, 36), (23, 36), (20, 40),
     (18, 40), (16, 40), (12, 44), (10, 44), (8, 44), (6, 43), (3, 42),
     (0, 40), (-2, 37), (-6, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 35), (141, 38),
     (141, 41), (142, 44), (143, 42), (141, 40), (140, 37), (139, 34),
     (136, 33), (132, 31)],
    # Australia
    [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    # New Zealand
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38), (174, -41),
     (172, -43), (168, -46)],
    # Borneo
    [(109, 1), (111, 2), (113, 4), (116, 6), (118, 2), (117, -2), (114, -3),
     (110, -2)],
    # Sumatra
    [(95, 5), (98, 3), (100, 0), (103, -3), (105, -5), (104, -6), (102, -4),
     (100, -1), (97, 3)],
    # New Guinea
    [(131, -1), (136, -2), (138, -4), (141, -3), (143, -6), (146, -8),
     (147, -9), (145, -8), (141, -8), (138, -8), (135, -5), (132, -2)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (45, -25),
     (43, -22), (43, -18)],
]

# story number -> (lat, lon, region)
# Pin positions are nudged apart from the true coordinates so the
# numbered circles stay readable at this map scale.
PINS = {
    1: (49.0, 32.0, "EUROPE"), 2: (43.0, 38.0, "EUROPE"),
    3: (40.0, 124.0, "ASIA-PACIFIC"), 4: (42.0, 98.0, "ASIA-PACIFIC"),
    5: (35.0, 133.0, "ASIA-PACIFIC"), 6: (52.5, 13.4, "EUROPE"),
    7: (48.9, 2.3, "EUROPE"), 8: (27.6, 87.9, "ASIA-PACIFIC"),
    9: (58.0, 43.0, "EUROPE"), 10: (52.0, 26.0, "EUROPE"),
    11: (33.0, -78.0, "AMERICAS"), 12: (38.0, 114.0, "ASIA-PACIFIC"),
    13: (44.0, -70.0, "AMERICAS"), 14: (49.0, -76.0, "AMERICAS"),
    15: (31.5, 34.5, "MIDDLE EAST"), 16: (39.0, -85.0, "AMERICAS"),
    17: (2.0, 45.3, "AFRICA"), 18: (38.6, -121.5, "AMERICAS"),
}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    lon0, lon1, lat0, lat1 = -180.0, 180.0, 84.0, -58.0

    def proj(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly],
                  fill=(232, 224, 200), outline=(120, 116, 100))
    # graticule dots
    for glon in range(-150, 181, 30):
        for glat in range(-45, 76, 30):
            px, py = proj(glon, glat)
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(90, 110, 140))
    for n, (lat, lon, region) in sorted(PINS.items()):
        px, py = proj(lon, lat)
        num_badge(d, int(px), int(py), n, REGION_COLORS[region], size=7)

# ------------------------------------------------------------------- copy

SUBTITLE = ("Two killed in Zaporizhzhia  ·  Kerch Bridge span falls  ·  "
            "Asia's markets roar back")

NUMBERS = (
    ("2", "killed in Zaporizhzhia"),
    ("40+", "hurt, toll rose all day"),
    ("+9.1%", "Taiex, record point gain"),
    ("90.6", "German Ifo, 7th rise"),
    ("$41bn", "Sanofi buys Insmed"),
    ("490,000", "confirmed Russian war dead"),
)

REGIONS = (("EUROPE", 12), ("ASIA-PACIFIC", 9), ("AMERICAS", 5),
           ("MIDDLE EAST", 4), ("AFRICA", 2), ("OCEANIA", 2))

UTC_EVENTS = (
    ("01:04", "KADIZ jets"),
    ("01:06", "Haiti names dead"),
    ("01:32", "Nepal quake"),
    ("02:37", "China spy sentence"),
    ("04:19", "Zaporizhzhia toll"),
    ("08:00", "Kerch strikes"),
    ("09:30", "Ifo 90.6"),
)

LEADS = (
    {"n": 1, "kicker": "ZAPORIZHZHIA, UKRAINE · WAR", "region": "EUROPE",
     "badge": "CONFIRMED · REUTERS", "ill": ill_zaporizhzhia,
     "headline": "Overnight strike flattens a five-storey block",
     "dek": ("At least 2 killed, 40+ hurt, four of them children, as bombs "
             "hit homes in Kosmichnyi district.")},
    {"n": 2, "kicker": "KERCH BRIDGE, UKRAINE · WAR", "region": "EUROPE",
     "badge": "REPORTED · BBC / GUARDIAN", "ill": ill_kerch,
     "headline": "Kerch Bridge span falls into the strait",
     "dek": ("Road arch falls, rail span damaged, traffic halted; Putin vows "
             "a \u201cfar more painful\u201d reply.")},
    {"n": 3, "kicker": "ASIA MARKETS · MARKETS", "region": "ASIA-PACIFIC",
     "badge": "CONFIRMED · REUTERS", "ill": ill_markets,
     "headline": "Asia roars back as the AI sell-off reverses",
     "dek": ("Kospi +7.3%, Taiex +9.1%, Nikkei +3.9% as chip stocks rebound; "
             "MSCI Asia-Pacific +4.6%.")},
)

SECOND = (
    {"n": 4, "kicker": "SHENZHOU-24 · SPACE", "region": "ASIA-PACIFIC",
     "badge": "OFFICIAL · CMSA", "ill": ill_shenzhou,
     "headline": "Pakistan's first astronaut to fly to Tiangong",
     "body": "Muhammad Zeeshan Ali, 40, joins Tang Hongbo and Wu Yi. Launch Wed 00:18 UTC."},
    {"n": 5, "kicker": "KADIZ · DEFENCE", "region": "ASIA-PACIFIC",
     "badge": "CONFIRMED · YONHAP", "ill": ill_kadiz,
     "headline": "Russian jets enter Korea's air-defence zone",
     "body": "Seoul scrambles fighters; air-raid alert on Ulleung. No airspace violated."},
    {"n": 6, "kicker": "IFO · ECONOMY", "region": "EUROPE",
     "badge": "OFFICIAL · IFO", "ill": ill_ifo,
     "headline": "German business mood at a three-year high",
     "body": "Ifo climate rises to 90.6, a seventh straight gain; expectations 91.9."},
    {"n": 7, "kicker": "SANOFI · BUSINESS", "region": "EUROPE",
     "badge": "CONFIRMED · REUTERS", "ill": ill_sanofi,
     "headline": "Sanofi buys Insmed for $41bn in cash",
     "body": "$175 a share for the US lung-drug maker — the biggest pharma deal of 2026."},
)

BRIEFS = (
    {"n": 8, "kicker": "NEPAL", "region": "ASIA-PACIFIC",
     "badge": "CONFIRMED · USGS", "ill": ill_nepal,
     "headline": "5.6 quake shakes Nepal's Tibet border",
     "body": "Felt in India, Bhutan, Bangladesh. No damage."},
    {"n": 9, "kicker": "RUSSIA", "region": "EUROPE",
     "badge": "REPORTED · MEDUZA", "ill": ill_rosstat,
     "headline": "At least 490,000 Russian war dead",
     "body": "Hacked Rosstat data; Meduza, Mediazona, BBC Russian."},
    {"n": 10, "kicker": "UKRAINE", "region": "EUROPE",
     "badge": "REPORTED · NEXUS EUROPA", "ill": ill_energy,
     "headline": "160+ missiles and drones hit the grid",
     "body": "Overnight strikes black out Dnipropetrovsk and Kharkiv."},
    {"n": 11, "kicker": "USA", "region": "AMERICAS",
     "badge": "REPORTED · FT", "ill": ill_patriot,
     "headline": "60 Patriot interceptors still awaiting approval",
     "body": "Hegseth has yet to approve the agreed transfer."},
    {"n": 12, "kicker": "CHINA", "region": "ASIA-PACIFIC",
     "badge": "REPORTED · GOLD WALL PRESS", "ill": ill_spy,
     "headline": "Death sentence for spying",
     "body": "Official Ma condemned for spying for a foreign state."},
    {"n": 13, "kicker": "USA–CHINA", "region": "ASIA-PACIFIC",
     "badge": "REPORTED · WIRES", "ill": ill_megaspeed,
     "headline": "Nvidia-scandal firm Megaspeed blacklisted",
     "body": "US adds the Nvidia-scandal firm to its blacklist."},
    {"n": 14, "kicker": "USA–CANADA", "region": "AMERICAS",
     "badge": "REPORTED · WIRES", "ill": None,
     "headline": "Pentagon rebukes Canada",
     "body": "Washington faults Ottawa over defence spending and its F-35 review."},
    {"n": 15, "kicker": "GAZA", "region": "MIDDLE EAST",
     "badge": "REPORTED · AL JAZEERA", "ill": ill_gaza,
     "headline": "Strikes kill at least three in Gaza",
     "body": "UNRWA worker among the dead; Oxfam: Gaza is \u201ctoxic land\u201d."},
    {"n": 16, "kicker": "USA", "region": "AMERICAS",
     "badge": "REPORTED · WIRES", "ill": None,
     "headline": "Ninth measles death in Pennsylvania",
     "body": "The epidemic now touches 46 counties across the state."},
    {"n": 17, "kicker": "AFRICA", "region": "AFRICA",
     "badge": "REPORTED · WIRES", "ill": None,
     "headline": "Somalia and Uganda step up the fight",
     "body": "Joint operations against Al-Shabaab intensify as a withdrawal begins."},
    {"n": 18, "kicker": "USA", "region": "AMERICAS",
     "badge": "REPORTED · WIRES", "ill": None,
     "headline": "Trump urges faster federal executions",
     "body": "A sharp rebuke of California governor Newsom over death-row delays."},
)

ALSO = (
    ("HAITI", "Bukele names 3 soldiers killed in blast."),
    ("LIBYA", "Tripoli wants answers from Kyiv on Benghazi."),
    ("FINLAND", "Sparta II towed to port after fire."),
    ("IRAN", "Singer gets 74 lashes; 3 tankers hit mines."),
    ("YEMEN", "Houthis report dozens dead in Saudi raids."),
    ("FRANCE", "Five 2027 hopefuls debate tax and housing."),
    ("EU", "Sanctions widen to founder of The Base."),
    ("UK", "Arm extends CEO Haas's tenure to 2033."),
    ("NIGERIA", "Borno school enrolment nearly doubles."),
    ("BLACK SEA", "Russia rules out reviving grain deal."),
    ("BOUGAINVILLE", "PNG votes on independence deal."),
    ("AUSTRALIA", "People may sue tech firms; fines to 5%."),
    ("SOUTH KOREA", "Consumer confidence 103.1."),
    ("JAPAN", "Advantest +15%, Tokyo Electron +10.5%."),
    ("TAIWAN", "Taiex's largest point gain on record."),
    ("SPORT", "Commanders 22-20; Blazers 128-111; Suns win."),
)

DATE_CHECK = (
    "Left out (not Tuesday): Huang returns to Nvidia (Mon) · NATO space vow (Mon) · EU 22nd sanctions (Mon) · "
    "Mexico tries El Chapo Isidro (Mon) · SpaceX sued over Grok (Mon) · Moldova drones (Mon) · Russia warns Estonia (Mon) · "
    "ICJ Rohingya ruling (19 Nov) · COP31 collapse (22 Nov) · Merkury sunk at Benghazi (22 Nov).",
    "Not yet: Champions League results (kick-offs 17:45 / 20:00 UTC) · Shenzhou-24 launch (Wed 25 Nov 00:18 UTC) · "
    "US PCE inflation data (Wed 25 Nov).",
)

FOOTER = (
    "Sources: Reuters, Kyiv Independent, BBC, The Guardian, France24, Yonhap, ifo Institute, CMSA / Xinhua, AP, "
    "Financial Times, Meduza, Mediazona, Al Jazeera, Oxfam, Nexus Europa. Pictures and map drawn in code, not photographs.",
    "CERTAINTY: CONFIRMED = 2+ outlets  ·  OFFICIAL = on record  ·  REPORTED = one outlet  ·  CLAIM = one side's word. "
    "Times UTC; c. = approximate.",
)


# ---------------------------------------------------------------- sections

def paint_top(page, d):
    d.rectangle([0, 0, W, 17], fill=NAVY)
    f = typeface("sans-cond-bold", 12)
    d.text((M, 2), "THE WORLD IN ONE DAY", font=f, fill=(255, 255, 255))
    right = "34 STORIES · 6 REGIONS · EVERY ONE FROM TUESDAY 24 NOVEMBER 2026"
    rf = typeface("sans-cond-bold", 12)
    tw = d.textlength(right, font=rf)
    d.text((R - tw, 2), right, font=rf, fill=GOLD_LT)


def paint_masthead(d):
    face = fitted(d, "Tuesday 24 November 2026", "mast", 52, CW)
    d.text((M, 20), "Tuesday 24 November 2026", font=face, fill=INK)
    sub = fitted(d, SUBTITLE, "serif-italic", 16, CW)
    d.text((M, 74), SUBTITLE, font=sub, fill=CRIMSON)
    rule(d, M, R, 94, weight=2)


def paint_numbers(d):
    y = 96
    col_w = CW / 6
    nf = typeface("serif-bold", 20)
    lf = typeface("sans-cond", 11)
    for i, (num, label) in enumerate(NUMBERS):
        x = M + i * col_w
        d.text((x + 4, y), num, font=nf, fill=CRIMSON)
        d.text((x + 4, y + 23), label, font=lf, fill=INK)
    rule(d, M, R, 134, weight=1, fill=HAIR)


def paint_chips(d):
    y = 140
    x = M
    f = typeface("sans-cond-bold", 12)
    for name, count in REGIONS:
        label = f"{name} {count}"
        x, _ = chip(d, x, y, label, f, REGION_COLORS[name], pad_x=8, pad_y=3)
        x += 8


def paint_utc(d):
    y = 164
    d.rectangle([M, y, R, y + 20], fill=NAVY)
    f = typeface("sans-cond-bold", 11)
    d.text((M + 8, y + 4), "THE DAY IN UTC", font=f, fill=GOLD_LT)
    tf = typeface("sans-cond-bold", 11)
    vf = typeface("sans-cond", 11)
    x = M + 108
    for t, ev in UTC_EVENTS:
        d.text((x, y + 4), t, font=tf, fill=GOLD_LT)
        tw = d.textlength(t, font=tf)
        d.text((x + tw + 4, y + 4), ev, font=vf, fill=(255, 255, 255))
        x += tw + 4 + d.textlength(ev, font=vf) + 16


def paint_leads(page, d):
    y = 184
    img_h = 104
    card_w = 318
    gap = 11
    hf = typeface("serif-bold", 21)
    bf = typeface("sans", 12)
    kf = typeface("sans-cond-bold", 12)
    badge_f = typeface("sans-cond-bold", 10)
    for i, c in enumerate(LEADS):
        x = M + i * (card_w + gap)
        c["ill"](d, x, y, card_w, img_h)
        num_badge(d, x + card_w - 16, y + 16, c["n"], REGION_COLORS[c["region"]], size=12)
        ky = y + img_h + 6
        d.text((x, ky), f"{c['n']} {c['kicker']}", font=kf, fill=CRIMSON)
        kw = d.textlength(f"{c['n']} {c['kicker']}", font=kf)
        bw = d.textlength(c["badge"], font=badge_f)
        pill(d, int(x + card_w - bw - 10), ky - 1, c["badge"], badge_f,
             GREEN if c["badge"].startswith("CONFIRMED") else
             NAVY2 if c["badge"].startswith("OFFICIAL") else SLATE)
        hy = ky + 16
        for ln in wrap(d, c["headline"], hf, card_w):
            d.text((x, hy), ln, font=hf, fill=INK)
            hy += 22
        para(d, x, hy + 2, c["dek"], bf, (50, 46, 42), card_w, 14)
        if i:
            d.line([x - 6, y, x - 6, y + 205], fill=HAIR, width=1)


def paint_second(page, d):
    y = 390
    img_h = 76
    card_w = 238
    gap = 8
    hf = typeface("serif-bold", 16)
    bf = typeface("sans", 12)
    kf = typeface("sans-cond-bold", 11)
    badge_f = typeface("sans-cond-bold", 9)
    rule(d, M, R, y - 6, weight=1)
    for i, c in enumerate(SECOND):
        x = M + i * (card_w + gap)
        c["ill"](d, x, y, card_w, img_h)
        num_badge(d, x + card_w - 13, y + 13, c["n"], REGION_COLORS[c["region"]], size=10)
        ky = y + img_h + 5
        d.text((x, ky), f"{c['n']} {c['kicker']}", font=kf, fill=CRIMSON)
        bw = d.textlength(c["badge"], font=badge_f)
        pill(d, int(x + card_w - bw - 10), ky, c["badge"], badge_f,
             GREEN if c["badge"].startswith("CONFIRMED") else
             NAVY2 if c["badge"].startswith("OFFICIAL") else SLATE)
        hy = ky + 15
        for ln in wrap(d, c["headline"], hf, card_w):
            d.text((x, hy), ln, font=hf, fill=INK)
            hy += 19
        para(d, x, hy + 1, c["body"], bf, (50, 46, 42), card_w, 14)
        if i:
            d.line([x - 5, y, x - 5, y + 158], fill=HAIR, width=1)


def paint_briefs(page, d):
    y0 = 556
    d.rectangle([M, y0, R, y0 + 16], fill=INK)
    d.text((M + 8, y0 + 1), "MORE FROM TUESDAY",
           font=typeface("sans-cond-bold", 12), fill=(255, 255, 255))
    note = "claims are marked as claims · badges name the source"
    nf = typeface("sans-italic", 11)
    nw = d.textlength(note, font=nf)
    d.text((R - 8 - nw, y0 + 2), note, font=nf, fill=(170, 170, 170))

    card_w, step = 154, 164
    rows = (BRIEFS[:6], BRIEFS[6:])
    hf = typeface("serif-bold", 13)
    bf = typeface("sans", 11)
    kf = typeface("sans-cond-bold", 11)
    badge_f = typeface("sans-cond-bold", 9)
    for r, row in enumerate(rows):
        y = 576 + r * 110
        for i, c in enumerate(row):
            x = M + i * step
            if c["ill"] is not None:
                c["ill"](d, x, y, card_w, 38)
                num_badge(d, x + 11, y + 27, c["n"],
                          REGION_COLORS[c["region"]], size=9)
                ky = y + 42
            else:
                ky = y + 2
            d.text((x, ky), f"{c['n']} {c['kicker']}", font=kf, fill=CRIMSON)
            bw = d.textlength(c["badge"], font=badge_f)
            if x + card_w - bw - 10 > x + d.textlength(
                    f"{c['n']} {c['kicker']}", font=kf) + 4:
                pill(d, int(x + card_w - bw - 10), ky, c["badge"], badge_f,
                     GREEN if c["badge"].startswith("CONFIRMED") else
                     NAVY2 if c["badge"].startswith("OFFICIAL") else SLATE)
            hy = ky + 14
            for ln in wrap(d, c["headline"], hf, card_w):
                d.text((x, hy), ln, font=hf, fill=INK)
                hy += 14
            para(d, x, hy + 1, c["body"], bf, (50, 46, 42), card_w, 12)
        if r == 0:
            rule(d, M, R, y + 108, weight=1, fill=HAIR)
    # sport card in the last slot of row 2
    x = M + 5 * step
    y = 576 + 110
    d.rectangle([x, y, x + card_w, y + 104], fill=NAVY)
    d.text((x + 8, y + 6), "SPORT", font=typeface("sans-cond-bold", 13),
           fill=GOLD_LT)
    sy = y + 26
    for league, res in (("NFL", "Commanders 22–20 Bengals, last-play FG"),
                        ("NBA", "Blazers 128–111 76ers; Spurs 123–107 Kings")):
        d.text((x + 8, sy), league, font=typeface("sans-cond-bold", 10),
               fill=(168, 180, 202))
        sy = para(d, x + 8, sy + 12, res, typeface("sans-bold", 11),
                  (255, 255, 255), card_w - 16, 12) + 4


def paint_bottom(page, d):
    y = 798
    # map, left
    d.text((M, y), "WHERE IT HAPPENED",
           font=typeface("sans-cond-bold", 13), fill=INK)
    note = "pins match story numbers"
    nf = typeface("sans-italic", 11)
    d.text((M + 150, y + 2), note, font=nf, fill=MUTED)
    draw_map(d, M, y + 18, 470, 116)
    # also list, right
    ax = 506
    d.text((ax, y), "ALSO ON TUESDAY — 16 MORE STORIES",
           font=typeface("sans-cond-bold", 13), fill=INK)
    col_w = 242
    kf = typeface("sans-cond-bold", 10)
    bf = typeface("sans-cond", 10)
    for i, (place, text) in enumerate(ALSO):
        col = i // 8
        row = i % 8
        x = ax + col * (col_w + 10)
        yy = y + 19 + row * 15
        n = 19 + i
        kick = f"{n} {place}:"
        d.text((x, yy), kick, font=kf, fill=CRIMSON)
        kw = d.textlength(kick, font=kf)
        d.text((x + kw + 3, yy), text, font=bf, fill=INK)
    # date check box
    by = 938
    d.rectangle([M, by, R, by + 42], outline=CRIMSON, width=2)
    d.text((M + 6, by + 4), "DATE CHECK", font=typeface("sans-cond-bold", 11),
           fill=CRIMSON)
    tf = typeface("sans", 10)
    para(d, M + 80, by + 4, DATE_CHECK[0], tf, INK, R - M - 86, 12)
    para(d, M + 80, by + 28, DATE_CHECK[1], tf, INK, R - M - 86, 12)
    # footer
    ff = typeface("sans", 9)
    d.text((M, 984), FOOTER[0], font=ff, fill=MUTED)
    d.text((M, 994), FOOTER[1], font=ff, fill=MUTED)
    d.rectangle([0, 1006, W, 1024], fill=NAVY)
    d.text((M, 1009), "THE WORLD IN ONE DAY",
           font=typeface("sans-cond-bold", 10), fill=(255, 255, 255))
    right = "TUESDAY 24 NOVEMBER 2026 · ONE PAGE"
    rf = typeface("sans-cond-bold", 10)
    tw = d.textlength(right, font=rf)
    d.text((R - tw, 1009), right, font=rf, fill=GOLD_LT)


# ------------------------------------------------------------------- build

def build_page() -> Image.Image:
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    paint_top(page, d)
    paint_masthead(d)
    paint_numbers(d)
    paint_chips(d)
    paint_utc(d)
    paint_leads(page, d)
    paint_second(page, d)
    paint_briefs(page, d)
    paint_bottom(page, d)
    return page


def main() -> int:
    page = build_page()
    blob = io.BytesIO()
    page.save(blob, format="PNG")
    data = blob.getvalue()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    OUT_PNG.write_bytes(data)
    PREVIEW_PNG.write_bytes(data)
    print(f"wrote {OUT_PNG} ({len(data)} bytes, {W}x{H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

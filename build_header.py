"""
build_header.py: builds header.svg, the animated night-sky header for my GitHub profile.

HOW TO CHANGE WHAT THE HEADER SAYS
  1. Edit NAME, GREETING, or LINES in the "EDIT THESE" box below.
  2. Save. The look (stars, moon, colors, typing style) stays exactly the same.
     - On GitHub: commit this file and the "Build header" action rebuilds header.svg for you.
     - On your computer: run   python build_header.py   and upload the new header.svg.

Only uses Python's standard library, so there is nothing to install.
"""

import random
from pathlib import Path

# =====================================================================
#  EDIT THESE
# =====================================================================
NAME = "Jackson Greene"          # the big name
GREETING = "# hi, I'm"           # the small gold line above the name

LINES = [                        # what the typewriter types, one after another
    "Learning Python & ML",
    "Experimenting with game ideas in Godot",
    "Building startups with my friends",
    "Exploring the possibilities of Python",
    "Learning robotics & 3D modeling",
]
# Tips: any number of lines works. About 45 characters or fewer looks best (longer lines
# shrink slightly to fit). Plain text is safest, so skip emoji inside the typed lines.
# =====================================================================


# ---------- Look (optional, these match the current design) ----------
COLORS = {
    "bg_top": "#070c24",         # deep navy, top-left of the card
    "bg_bottom": "#15224f",      # lighter navy, bottom-right
    "gold": "#ffd479",           # moon, cursor, accents
    "gold_dim": "#c9a24d",       # greeting text
    "typed": "#d6defa",          # typed text
    "name": "#f6f1e3",           # big name
    "star": "#fff4d6",           # twinkling stars
    "border": "#2a3b78",         # card outline
}
TYPING_SPEED = 0.055             # seconds per letter (smaller = faster)
HOLD_SECONDS = 2.0               # how long each finished line stays on screen

# ---------- Fixed layout (no need to touch) ----------
W, H = 800, 240
MOON = (700, 76)
TYPE_X, TYPE_Y = 72, 192
BASE_TYPE_SIZE, BASE_NAME_SIZE = 24, 56
MONO_EM, NAME_EM = 0.62, 0.60    # rough glyph widths, used to shrink long text to fit

# Star layout is frozen so editing the text never moves the stars.
# Each star: x, y, radius, twinkle seconds, start offset.
STARS = [
    (505.1, 116.2, 1.4, 4.37, -3.45),
    (577.9, 81.6, 0.9, 3.89, -2.79),
    (785.5, 30.0, 0.9, 4.18, -4.22),
    (484.0, 31.0, 1.1, 3.46, -1.91),
    (507.6, 224.6, 0.9, 3.44, -0.71),
    (661.2, 31.8, 1.1, 4.35, -1.0),
    (593.2, 20.3, 0.7, 4.11, -3.03),
    (191.7, 162.0, 0.7, 4.23, -0.22),
    (22.7, 77.8, 1.4, 4.25, -4.95),
    (537.5, 56.9, 0.7, 4.07, -3.45),
    (144.9, 206.0, 0.7, 5.56, -2.29),
    (523.5, 107.7, 1.4, 3.32, -2.37),
    (528.1, 56.1, 0.9, 3.55, -4.5),
    (258.3, 42.9, 1.4, 4.18, -0.54),
    (669.2, 164.8, 1.4, 4.5, -4.63),
    (226.4, 59.4, 0.9, 4.79, -4.89),
    (395.3, 80.9, 0.7, 3.06, -1.14),
    (661.8, 222.2, 1.1, 3.5, -1.78),
    (363.3, 29.8, 1.4, 2.76, -3.65),
    (46.0, 164.2, 0.7, 5.3, -3.12),
    (454.5, 79.5, 0.9, 4.78, -4.39),
    (625.0, 18.1, 0.7, 3.68, -2.07),
    (33.1, 189.9, 0.9, 4.23, -4.32),
    (753.9, 159.1, 0.9, 4.2, -4.26),
    (151.9, 16.3, 0.9, 3.19, -3.7),
    (378.5, 165.4, 1.1, 5.47, -1.58),
    (280.9, 161.8, 1.1, 5.43, -0.97),
    (597.8, 97.4, 0.9, 5.42, -0.67),
    (625.4, 206.1, 0.9, 2.85, -0.44),
    (81.3, 211.7, 1.4, 2.73, -4.16),
    (571.7, 41.5, 1.4, 4.25, -3.52),
    (629.1, 214.2, 0.9, 3.77, -3.43),
    (645.8, 150.0, 0.7, 2.73, -2.85),
    (568.0, 59.2, 1.1, 5.5, -4.84),
    (708.8, 221.9, 0.7, 4.8, -3.17),
    (768.5, 127.8, 1.1, 4.11, -3.43),
    (624.5, 81.9, 0.9, 5.13, -2.41),
    (283.0, 31.5, 0.7, 2.53, -2.76),
    (607.1, 117.3, 1.4, 2.9, -0.92),
    (35.9, 185.5, 0.9, 2.99, -0.79),
    (622.3, 43.8, 1.1, 5.55, -0.48),
    (546.2, 214.5, 0.7, 2.86, -3.4),
]
SPARKLES = [(588, 40, 4.6, -1.0), (752, 168, 5.4, -3.2), (130, 214, 4.1, -2.1)]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fit(size, text_len, em, max_width):
    """Shrink a font size if the text would run past max_width pixels."""
    needed = text_len * em * size
    return size if needed <= max_width else max(10, int(size * max_width / needed))


# ---------- Typewriter timeline ----------
lines = [l.strip() for l in LINES if l.strip()]
if not lines:
    raise SystemExit("LINES is empty: add at least one line to type.")

rng = random.Random(11)          # fixed seed: same typing rhythm every time
frames = []                      # (text, line_index, show_cursor, seconds)
for li, line in enumerate(lines):
    frames.append(("", li, True, 0.35))
    for i in range(1, len(line) + 1):
        d = TYPING_SPEED + rng.random() * 0.06
        if line[i - 1] in " ,&":
            d += 0.04
        frames.append((line[:i], li, True, round(d, 3)))
    for _ in range(2):
        frames.append((line, li, True, HOLD_SECONDS * 0.275))
        frames.append((line, li, False, HOLD_SECONDS * 0.2))
    i = len(line)
    while i > 0:
        i = max(0, i - 2)
        frames.append((line[:i], li, True, 0.035))

merged = []
for f in frames:
    if merged and merged[-1][0] == f[0] and merged[-1][2] == f[2]:
        merged[-1] = f[:3] + (merged[-1][3] + f[3],)
    else:
        merged.append(f)
frames = merged
T = round(sum(f[3] for f in frames), 3)

typed, t = [], 0.0
for text, li, cursor_on, d in frames:
    s, e = t, min(T, t + d + 0.03)   # tiny overlap so the text never blinks out between frames
    t += d
    if s <= 0:
        kt, vals = f"0;{e / T:.6f}", "1;0"
    elif e >= T:
        kt, vals = f"0;{s / T:.6f}", "0;1"
    else:
        kt, vals = f"0;{s / T:.6f};{e / T:.6f}", "0;1;0"
    size = fit(BASE_TYPE_SIZE, len(lines[li]) + 1, MONO_EM, W - TYPE_X - 24)
    style = f' style="font-size:{size}px"' if size != BASE_TYPE_SIZE else ""
    cursor = '<tspan class="c">|</tspan>' if cursor_on else ""
    typed.append(
        f'<text class="m t" x="{TYPE_X}" y="{TYPE_Y}" opacity="0"{style}><tspan class="x">{esc(text)}</tspan>{cursor}'
        f'<animate attributeName="opacity" calcMode="discrete" dur="{T}s" repeatCount="indefinite" '
        f'keyTimes="{kt}" values="{vals}"/></text>'
    )

# ---------- Sky ----------
star_svg = [
    f'<circle cx="{x}" cy="{y}" r="{r}" fill="{COLORS["star"]}" opacity=".3">'
    f'<animate attributeName="opacity" values=".15;.95;.15" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/></circle>'
    for x, y, r, dur, beg in STARS
]
sparkle_svg = [
    f'<path transform="translate({x} {y})" d="M0-6 1.6-1.6 6 0 1.6 1.6 0 6-1.6 1.6-6 0-1.6-1.6Z" fill="{COLORS["gold"]}" opacity=".4">'
    f'<animate attributeName="opacity" values=".15;1;.15" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/></path>'
    for x, y, dur, beg in SPARKLES
]

name_size = fit(BASE_NAME_SIZE, len(NAME), NAME_EM, 590)
name_style = f' style="font-size:{name_size}px"' if name_size != BASE_NAME_SIZE else ""
C = COLORS

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">{esc(NAME)}</title>
<desc id="d">Night-sky banner with a crescent moon. A typewriter cycles through: {esc("; ".join(lines))}.</desc>
<style>
.m{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"DejaVu Sans Mono",monospace}}
.t{{font-size:{BASE_TYPE_SIZE}px}}
.x{{fill:{C["typed"]}}}
.c{{fill:{C["gold"]};font-weight:700}}
.n{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:{BASE_NAME_SIZE}px;font-weight:700;fill:{C["name"]}}}
.h{{font-size:20px;fill:{C["gold_dim"]}}}
</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg_top"]}"/><stop offset="1" stop-color="{C["bg_bottom"]}"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{C["gold"]}" stop-opacity=".28"/><stop offset="1" stop-color="{C["gold"]}" stop-opacity="0"/></radialGradient>
<mask id="cres"><rect width="{W}" height="{H}" fill="#fff"/><circle cx="713" cy="67" r="26" fill="#000"/></mask>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<g clip-path="url(#card)">
<circle cx="{MOON[0]}" cy="{MOON[1]}" r="95" fill="url(#glow)"><animate attributeName="opacity" values=".6;1;.6" dur="7s" repeatCount="indefinite"/></circle>
{"".join(star_svg)}
{"".join(sparkle_svg)}
<circle cx="{MOON[0]}" cy="{MOON[1]}" r="30" fill="{C["gold"]}" mask="url(#cres)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="17.5" fill="none" stroke="{C["border"]}" stroke-opacity=".7"/>
<text class="m h" x="48" y="68">{esc(GREETING)}</text>
<text class="n" x="46" y="128"{name_style}>{esc(NAME)}</text>
<rect x="48" y="146" width="64" height="3" rx="1.5" fill="{C["gold"]}"/>
<path d="M46 176 55 184 46 192" fill="none" stroke="{C["gold"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
{"".join(typed)}
</svg>
"""

out = Path(__file__).resolve().parent / "header.svg"
out.write_text(svg, encoding="utf-8")
print(f"Built {out.name}: {len(lines)} lines, {T:.1f}s loop, {len(svg.encode()) // 1024} KB")
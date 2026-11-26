#!/usr/bin/env python3
"""Render the front page 'The World in One Day — Thursday, 26 November 2026'.

Draws a 1024x1024 newspaper front page summing up 26 November 2026's
world news: 10 stories, a world map with numbered pins, an ALSO TODAY band.
Deterministic: fixed geometry, fixed colours, no clock, no network, no
randomness. Running it twice produces byte-identical PNG output.

Written from the spec in news-image-20261126-notes.md (10 stories, layout
numbers). All copy is written here from the notes' story facts.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

# --- palette ---
PAPER = (253, 252, 248)
INK = (18, 18, 18)
NAVY = (20, 38, 74)
NAVY_LIGHT = (36, 58, 102)
RED = (178, 34, 34)
GREY = (110, 110, 110)
RULE = (40, 40, 40)
SEA = (214, 230, 240)
LAND = (232, 224, 204)
LAND_EDGE = (170, 158, 130)
PIN = (178, 34, 34)
FLAME = (232, 120, 30)
FLAME2 = (244, 190, 60)
SMOKE = (120, 120, 120)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, x, y, f, fill=INK, leading=None):
    """Draw lines top-down; returns y after the last line."""
    if leading is None:
        leading = f.size + 4
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def body_block(d, text, x, y, f, max_w, max_lines, leading=None):
    """Draw a wrapped body capped at max_lines; assert it fits."""
    lines = wrap(d, text, f, max_w)
    assert len(lines) <= max_lines, (
        "body overflow (%d lines > %d): %r" % (len(lines), max_lines, text[:60]))
    return draw_lines(d, lines[:max_lines], x, y, f, leading=leading)


# --- stories: (number, kicker, headline, body, headline_size) ---
LEAD = (
    "LEAD  •  STRAIT OF HORMUZ",
    "Two tankers hit mines and burn in the Strait of Hormuz",
    "Two oil tankers struck naval mines on an unauthorised route through "
    "the strait, exploded and caught fire, the IRGC said. Tehran vowed "
    "tighter control of the waterway as the U.S. naval blockade holds.",
)

SIDE = [
    (
        "2  •  SAUDI ARABIA",
        "Houthis strike Ras Tanura refinery",
        "Houthis say they struck the largest Saudi refinery; the coalition "
        "downed seven drones over Ras Tanura.",
    ),
    (
        "3  •  THE STRAIT",
        "Iran: reopen Hormuz in 48 hours",
        "Tehran offers to restore shipping in 48 hours if Washington lifts "
        "the blockade and ends the war.",
    ),
    (
        "4  •  GAZA",
        "Israel kills Hamas security chief",
        "Israel killed Hamas security chief Mohammad Abuelouf, his wife and "
        "two children, in Gaza.",
    ),
]

GRID = [
    (
        "5  •  SPACE",
        "Pakistan's first astronaut reaches orbit",
        "China's Shenzhou-24 carried Pakistani pilot Muhammad Zeeshan Ali "
        "to Tiangong, a first for a foreign astronaut.",
    ),
    (
        "6  •  ECONOMY",
        "U.S. economy grew 4.3% in Q3",
        "The fastest growth in three years, the BEA said in its second "
        "estimate, revised up from 3.4%.",
    ),
    (
        "7  •  WEATHER",
        "Thanksgiving storms threaten 250 million",
        "Twin storms batter both U.S. coasts on the busiest travel day; "
        "70 mph gusts, record king tides in San Francisco.",
    ),
    (
        "8  •  MIGRATION",
        "Record 2,100 migrants reach Canaries",
        "More than 2,100 arrivals in 24 hours, a daily record; one migrant "
        "was found dead, another gave birth en route.",
    ),
    (
        "9  •  UKRAINE",
        "Kremlin rejects Johnson's Ukraine call",
        "The Kremlin called ex-PM Boris Johnson's proposal for a token "
        "Western force in Ukraine unacceptable.",
    ),
    (
        "10  •  UKRAINE",
        "Russia strikes Odesa, killing two",
        "A strike killed two and injured three, including a child; Kyiv was "
        "also hit, an apartment block set on fire.",
    ),
]

ALSO_TODAY = [
    "Eurostar halts London–Paris–Brussels trains",
    "Court lets Baghdad send troops to Kurdistan",
    "Senegal reinstated as Africa Cup champions",
    "U.S. warns citizens at 10 Mideast missions",
    "Iran's rial passes 2.85m to the dollar",
    "U.S. core PCE hits 3.3%",
    "Abrego Garcia reaches Spain",
    "Army detonates 5 tons of bomb chemicals",
    "Macy's parade balloons may be grounded",
]

# --- simplified world map (lon, lat polygons, equirectangular) ---
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-80, 73), (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 21), (-95, 19), (-100, 16), (-105, 20),
     (-110, 23), (-115, 28), (-120, 34), (-125, 40), (-130, 48),
     (-140, 60), (-155, 58), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, -5), (-40, -10),
     (-35, -15), (-40, -25), (-50, -30), (-60, -35), (-70, -45),
     (-70, -55), (-75, -50), (-75, -35), (-80, -20), (-80, -10), (-80, 0)],
    # Europe
    [(-10, 36), (-5, 44), (0, 46), (5, 44), (10, 45), (15, 44), (20, 40),
     (25, 38), (30, 36), (28, 42), (23, 40), (18, 42), (12, 44), (5, 50),
     (0, 52), (-5, 50), (-10, 48), (-10, 43)],
    # Africa
    [(-10, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (40, 20),
     (45, 12), (50, 10), (48, 0), (42, -10), (38, -20), (32, -28),
     (25, -35), (18, -35), (15, -25), (12, -15), (10, -5), (8, 5), (0, 5),
     (-8, 5), (-12, 10), (-15, 15), (-17, 20), (-15, 25), (-12, 30)],
    # Asia
    [(30, 36), (35, 42), (40, 45), (45, 48), (50, 50), (55, 52), (60, 55),
     (65, 60), (70, 65), (75, 70), (80, 72), (90, 75), (100, 76),
     (110, 74), (120, 72), (130, 70), (140, 72), (150, 70), (160, 66),
     (170, 66), (175, 62), (170, 60), (160, 58), (155, 55), (150, 50),
     (145, 45), (140, 40), (135, 35), (130, 32), (127, 38), (122, 40),
     (120, 32), (115, 28), (110, 20), (108, 12), (105, 8), (100, 10),
     (98, 15), (95, 20), (92, 22), (88, 22), (85, 18), (80, 15),
     (78, 8), (75, 10), (72, 20), (68, 25), (65, 25), (60, 25),
     (58, 28), (55, 26), (52, 28), (50, 30), (48, 30), (45, 28),
     (42, 30), (40, 32), (38, 36), (35, 36)],
    # Australia
    [(113, -22), (115, -32), (120, -35), (130, -32), (135, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (150, -25), (146, -20), (142, -15),
     (140, -12), (135, -15), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20), (114, -22)],
]

# (number, lon, lat) — pins 1/2/3 share the strait; 3 is offset down-right.
PINS = [
    (1, 56.0, 26.5),
    (2, 50.0, 26.6),
    (3, 59.5, 24.0),
    (4, 34.5, 31.5),
    (5, 105.0, 38.0),
    (6, -80.0, 38.0),
    (7, -100.0, 40.0),
    (8, -16.0, 28.5),
    (9, 37.6, 55.7),
    (10, 30.7, 46.5),
]


def draw_masthead(d):
    d.line([(24, 14), (1000, 14)], fill=RULE, width=2)
    f_name = font(SERIF_B, 58)
    d.text((512, 22), "THE WORLD IN ONE DAY", font=f_name, fill=INK,
           anchor="ma")
    f_sub = font(SANS_B, 17)
    d.text((512, 84), "THURSDAY, 26 NOVEMBER 2026", font=f_sub, fill=RED,
           anchor="ma")
    f_tag = font(SANS, 13)
    d.text((24, 86), "THE DAY'S NEWS IN ONE PAGE", font=f_tag, fill=GREY)
    d.text((1000, 86), "No. 330  •  FREE", font=f_tag, fill=GREY,
           anchor="ra")
    d.line([(24, 110), (1000, 110)], fill=RULE, width=3)


def draw_tanker_scene(img, x0, y0, x1, y1):
    """Stylised burning tankers in the strait; caption strip at the top.

    Everything is drawn on a temp layer the size of the scene box and then
    pasted, so smoke and flames can never escape the box and strike
    through the headline above it.
    """
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGB", (w, h), (0, 0, 0))
    ld = ImageDraw.Draw(layer)
    # dusk sky
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(250 - 60 * t)
        g = int(190 - 90 * t)
        b = int(120 - 40 * t)
        ld.line([(0, i), (w, i)], fill=(r, g, b))
    # sea
    sea_y = int(h * 0.62)
    ld.rectangle([0, sea_y, w, h], fill=(28, 52, 84))
    for k in range(5):
        wy = sea_y + 8 + k * 9
        ld.line([(12 + k * 7, wy), (w - 12 - k * 5, wy)],
                fill=(70, 110, 150), width=2)
    # tanker 1 (left, burning)
    hx, hy = 60, sea_y - 26
    ld.rectangle([hx, hy, hx + 210, sea_y + 2], fill=(24, 24, 28))
    ld.rectangle([hx + 150, hy - 22, hx + 185, hy], fill=(24, 24, 28))
    ld.rectangle([hx + 40, hy - 14, hx + 70, hy], fill=(24, 24, 28))
    # flames above tanker 1
    for fx, fh in [(hx + 60, 46), (hx + 100, 60), (hx + 140, 40)]:
        ld.polygon([(fx - 16, hy), (fx, hy - fh), (fx + 16, hy)],
                   fill=FLAME)
        ld.polygon([(fx - 8, hy), (fx, hy - fh + 18), (fx + 8, hy)],
                   fill=FLAME2)
    # smoke (clipped to the box by the layer)
    for sx, sy, sr in [(hx + 80, hy - 62, 14), (hx + 110, hy - 78, 18),
                       (hx + 140, hy - 66, 12)]:
        ld.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SMOKE)
    # tanker 2 (right, listing)
    hx2 = 330
    ld.polygon([(hx2, sea_y - 20), (hx2 + 190, sea_y - 28),
                (hx2 + 190, sea_y + 2), (hx2, sea_y + 2)], fill=(34, 34, 38))
    ld.rectangle([hx2 + 120, sea_y - 44, hx2 + 150, sea_y - 24],
                 fill=(34, 34, 38))
    for fx, fh in [(hx2 + 60, 34), (hx2 + 95, 44)]:
        ld.polygon([(fx - 12, sea_y - 24), (fx, sea_y - 24 - fh),
                    (fx + 12, sea_y - 24)], fill=FLAME)
    # naval mines: spiked circles in the water
    for mx, my in [(300, sea_y + 22), (470, sea_y + 30),
                   (120, sea_y + 34)]:
        ld.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(20, 20, 20))
        for dx, dy in [(-9, 0), (9, 0), (0, -9), (0, 9),
                       (-6, -6), (6, -6), (-6, 6), (6, 6)]:
            ld.line([(mx, my), (mx + dx, my + dy)], fill=(20, 20, 20),
                    width=2)
    img.paste(layer, (x0, y0))
    # caption strip at the TOP of the scene box (never struck by a hull)
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y0 + 22], fill=NAVY)
    f_cap = font(SANS_B, 13)
    d.text((x0 + 10, y0 + 4),
           "SMOKE RISES FROM A STRICKEN TANKER  •  ILLUSTRATION",
           font=f_cap, fill=(255, 255, 255))


def draw_lead(d, img):
    x0, x1 = 24, 600
    y = 122
    f_kick = font(SANS_B, 14)
    d.text((x0, y), LEAD[0], font=f_kick, fill=RED)
    y += 22
    f_head = font(SERIF_B, 31)
    lines = wrap(d, LEAD[1], f_head, x1 - x0)
    assert len(lines) <= 3, "lead headline overflow: %r" % (lines,)
    y = draw_lines(d, lines, x0, y, f_head, leading=37)
    y += 6
    scene_y0, scene_y1 = y, y + 118
    draw_tanker_scene(img, x0, scene_y0, x1, scene_y1)
    y = scene_y1 + 8
    f_body = font(SERIF, 16)
    body_block(d, LEAD[2], x0, y, f_body, x1 - x0, 3, leading=20)


def draw_side(d):
    x0, x1 = 624, 1000
    y = 122
    f_kick = font(SANS_B, 12)
    f_head = font(SERIF_B, 19)
    f_body = font(SERIF, 14)
    for i, (kick, head, body) in enumerate(SIDE):
        if i:
            d.line([(x0, y), (x1, y)], fill=(200, 200, 200), width=1)
            y += 6
        d.text((x0, y), kick, font=f_kick, fill=RED)
        y += 15
        lines = wrap(d, head, f_head, x1 - x0)
        assert len(lines) <= 1, "side headline overflow: %r" % (lines,)
        y = draw_lines(d, lines, x0, y, f_head, leading=22)
        y += 2
        y = body_block(d, body, x0, y, f_body, x1 - x0, 2, leading=15)
        y += 6
    assert y <= 402, "side column overflow: y=%d" % y


def draw_map(d):
    x0, y0, x1, y1 = 24, 424, 1000, 544
    f_lab = font(SANS_B, 13)
    d.text((x0, 408), "WHERE IT HAPPENED  —  NUMBERS MATCH THE STORIES",
           font=f_lab, fill=NAVY)
    d.rectangle([x0, y0, x1, y1], fill=SEA, outline=RULE, width=1)

    def proj(lon, lat):
        px = x0 + (lon + 170) / 360.0 * (x1 - x0)
        py = y0 + (75 - lat) / 130.0 * (y1 - y0)
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # pins, numbered; pin 3 already offset down-right in PINS
    f_pin = font(SANS_B, 12)
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=PIN,
                  outline=(255, 255, 255), width=2)
        label = str(num)
        tw = d.textlength(label, font=f_pin)
        d.text((px - tw / 2, py - 8), label, font=f_pin,
               fill=(255, 255, 255))


def draw_grid(d):
    cols = [(24, 500), (524, 1000)]
    rows = [556, 664, 772]
    f_kick = font(SANS_B, 13)
    f_head = font(SERIF_B, 20)
    f_body = font(SERIF, 15)
    for i, (kick, head, body) in enumerate(GRID):
        col = i % 2
        row = i // 2
        x0, x1 = cols[col]
        y = rows[row]
        d.text((x0, y), kick, font=f_kick, fill=RED)
        y += 19
        lines = wrap(d, head, f_head, x1 - x0)
        assert len(lines) <= 2, "grid headline overflow: %r" % (lines,)
        y = draw_lines(d, lines, x0, y, f_head, leading=24)
        y += 3
        y = body_block(d, body, x0, y, f_body, x1 - x0, 2, leading=19)
        assert y <= rows[row] + 106, "grid story overflow: y=%d" % y


def draw_also_today(d):
    x0, y0, x1, y1 = 24, 888, 1000, 976
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    f_lab = font(SANS_B, 14)
    d.text((x0 + 12, y0 + 8), "ALSO TODAY", font=f_lab,
           fill=(255, 210, 90))
    f_item = font(SANS, 12)
    col_w = (x1 - x0 - 24) / 3
    for i, item in enumerate(ALSO_TODAY):
        col = i % 3
        row = i // 3
        x = x0 + 12 + col * col_w
        y = y0 + 32 + row * 19
        lines = wrap(d, item, f_item, col_w - 26)
        assert len(lines) <= 1, "also-today overflow: %r" % (item,)
        d.ellipse([x, y + 4, x + 6, y + 10], fill=(255, 210, 90))
        d.text((x + 12, y), lines[0], font=f_item, fill=(255, 255, 255))


def draw_footer(d):
    f_foot = font(SANS, 13)
    d.text((512, 986),
           "All stories first reported 25–26 November 2026  •  "
           "Sources: Reuters, AP, BBC, TRT World",
           font=f_foot, fill=GREY, anchor="ma")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_lead(d, img)
    draw_side(d)
    draw_map(d)
    draw_grid(d)
    draw_also_today(d)
    draw_footer(d)
    img.save(OUT, format="PNG")


if __name__ == "__main__":
    main()

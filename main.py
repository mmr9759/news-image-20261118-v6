#!/usr/bin/env python3
"""THE WORLD TODAY - one front page summing up Wednesday 18 November 2026.

Draws a 1024x1024 newspaper front page with pure stdlib Python (no network,
no files read, no randomness): a dated masthead, three illustrated lead
stories, a world map with the day's datelines, 41 more stories from six
continents, and a markets footer. Writes only to /output/entry.png
(or $MAKEFUN_OUTPUT when set, for local checks).

Stories were researched from public reporting of 18 November 2026:
Trump lands in Shenzhen for APEC (Xi greets him on the tarmac; first
US-Russia-China three-way talks set for Thursday), US jets strike an
IRGC missile site on Qeshm Island with Iran answering by drone at
Bahrain and Kuwait, Ukraine hits the Kerch Bridge a second day,
Mary Peltola wins Alaska giving Democrats 56 Senate seats, the
DR Congo Ebola outbreak passes 11,000 cases, the US loses its
measles elimination status, Voyager 1 reaches one light-day,
Cyclone Akvan nears India and Cyclone Xavier hits the Cook Islands.
"""

import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (250, 247, 238)
INK = (22, 22, 24)
NAVY = (16, 32, 64)
NAVY2 = (24, 48, 92)
RED = (178, 34, 34)
GOLD = (198, 158, 52)
BLUE = (30, 90, 160)
SKY = (198, 220, 236)
SEA = (140, 175, 205)
LAND = (112, 142, 104)
GREY = (120, 120, 118)
LIGHT = (228, 228, 222)
WHITE = (255, 255, 255)
DARK = (40, 44, 52)

# 5x7 bitmap font, uppercase + digits + punctuation. Each glyph is 7 rows
# of 5 cells; '#' is a filled cell.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
}


def text_width(text, scale, spacing=1):
    """Pixel width of text drawn at the given scale."""
    if not text:
        return 0
    return len(text) * (5 * scale + spacing) - spacing


def wrap_text(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            if not cur:
                cur = w
            elif len(cur) + 1 + len(w) <= max_chars:
                cur += " " + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, t, c):
        r = max(1, t // 2)
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            self.circle(x, y, r, c)

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def polygon(self, pts, c):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0, y1 = max(0, min(ys)), min(self.h - 1, max(ys))
        n = len(pts)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x1, yy1 = pts[i]
                x2, yy2 = pts[(i + 1) % n]
                if (yy1 <= y < yy2) or (yy2 <= y < yy1):
                    t = (y - yy1) / (yy2 - yy1)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa, xb = int(math.ceil(xs[i])), int(math.floor(xs[i + 1]))
                if xb >= xa:
                    self.fill_rect(xa, y, xb - xa + 1, 1, c)

    def vgrad(self, x, y, w, h, c1, c2):
        for i in range(h):
            t = i / max(1, h - 1)
            c = tuple(round(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
            self.fill_rect(x, y + i, w, 1, c)

    def text(self, x, y, s, c, txt, spacing=1):
        cx = x
        for ch in txt:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 5 * s + spacing
                continue
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * s, y + row * s, s, s, c)
            cx += 5 * s + spacing
        return cx

    def text_center(self, y, s, c, txt, x0=0, x1=None, spacing=1):
        if x1 is None:
            x1 = self.w
        w = text_width(txt, s, spacing)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, c, txt, spacing)

    def text_block(self, x, y, w, s, c, txt, lh=None, spacing=1):
        """Wrapped left-aligned block; returns y just below the last line."""
        if lh is None:
            lh = 7 * s + 1
        max_chars = max(1, w // (5 * s + spacing))
        yy = y
        for line in wrap_text(txt, max_chars):
            self.text(x, yy, s, c, line, spacing)
            yy += lh
        return yy

    def png_bytes(self):
        raw = bytearray()
        stride = self.w * 3
        for yy in range(self.h):
            raw.append(0)
            raw += self.px[yy * stride:(yy + 1) * stride]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(tag, data):
            out = struct.pack(">I", len(data)) + tag + data
            out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- data
DATE_LINE = "WEDNESDAY 18 NOVEMBER 2026"
DECK = ("TRUMP LANDS IN SHENZHEN AS XI AND PUTIN AWAIT, US JETS STRIKE "
        "QESHM, KERCH BRIDGE HIT AGAIN - AND 41 MORE STORIES FROM SIX "
        "CONTINENTS ON ONE FRONT PAGE")

LEADS = [
    {
        "cap": "SHENZHEN - APEC SUMMIT",
        "head": "TRUMP LANDS IN\nSHENZHEN",
        "deck": ("XI GREETS HIM ON THE TARMAC; FIRST THREE-WAY TALKS "
                 "SET FOR THURSDAY."),
        "scene": "shenzhen",
    },
    {
        "cap": "QESHM ISLAND - THE GULF",
        "head": "US JETS STRIKE\nQESHM",
        "deck": ("IRAN HITS BACK WITH DRONES AT BAHRAIN AND KUWAIT; "
                 "A SHIP IS HIT IN HORMUZ."),
        "scene": "gulf",
    },
    {
        "cap": "KERCH STRAIT - CRIMEA",
        "head": "KERCH BRIDGE\nHIT AGAIN",
        "deck": ("UKRAINE STRIKES A SECOND DAY; PART OF THE ROAD SPAN "
                 "FALLS INTO THE STRAIT."),
        "scene": "kerch",
    },
]

# 41 more stories, grouped by continent. Every headline wraps to two
# lines at the column width used below.
COLUMNS = [
    ("ASIA", [
        "TRUMP MEETS MARCOS, QUAD",
        "TARIFF TRUCE RUNS TO JAN 10",
        "CYCLONE AKVAN NEARS INDIA",
        "ROYALS END MUMBAI VISIT",
        "SIBERIA CRASH KILLS 19",
        "COLD KILLS IN GAZA TENTS",
        "TRUMP TEASES KIM MEETING",
        "INDONESIA DROUGHT, FIRES",
        "MYANMAR CASE AT WORLD COURT",
    ]),
    ("EUROPE", [
        "COP31 CLIMATE TALKS OPEN",
        "STUDENT LIST WINS IN SERBIA",
        "UK SANCTIONS ON SETTLEMENTS",
        "ZVEREV INTO ATP LAST EIGHT",
        "EUROPE PAYS UP FOR LNG",
        "NATO UNVEILS COMMS STRATEGY",
        "TANKER SINKS OFF BULGARIA",
        "POPE KEEPS CELIBACY RULE",
        "FIFA: DIALLO V INFANTINO",
    ]),
    ("AFRICA", [
        "EBOLA IN CONGO TOPS 11,000",
        "MOROCCO REACH AFCON 2027",
        "SOUTH AFRICA INFLATION 5.2%",
        "UGANDA RAIL DEAL NEARS",
        "JONATHAN WARNS OF CRISIS",
        "BAFANA BEAT KENYA 2-1",
        "CAPE VERDE MISS AFCON CUT",
        "SOUTH AFRICA HALTS STARLINK",
    ]),
    ("NORTH AMERICA", [
        "PELTOLA WINS ALASKA SEAT",
        "DEMS TAKE 56 SENATE SEATS",
        "US LOSES MEASLES STATUS",
        "TECH OUTAGES REACH THE NSA",
        "S&P 500 SLIPS 1.03%",
        "NVIDIA REVENUE $115.8BN",
        "ANTHROPIC IPO DUE WEDNESDAY",
        "VOYAGER 1 ONE LIGHT-DAY OUT",
    ]),
    ("SOUTH AMERICA", [
        "AWA EMERGE IN BRAZIL AMAZON",
        "REAL FALLS ON LULA PLAN",
        "BOVESPA EDGES UP 0.31%",
        "DROUGHT GRIPS BRAZIL AMAZON",
    ]),
    ("OCEANIA", [
        "XAVIER HITS COOK ISLANDS",
        "SANDPAPERGATE FORUM OPENS",
        "ASX 200 FALLS 2.38%",
    ]),
]

MARKETS = "MARKETS: S&P 500 -1.03% - BRENT $92.47 -0.72% - GOLD -1.65% - FTSE -1.76%"
FOOTER = "WEDNESDAY 18 NOVEMBER 2026 - 44 STORIES FROM SIX CONTINENTS"

# ------------------------------------------------------- lead illustrations
def draw_shenzhen(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (232, 148, 92), (94, 82, 130))
    cv.circle(x + w - 52, y + 34, 20, (240, 200, 110))
    base = y + h
    towers = [(0, 62, 34), (38, 96, 30), (72, 78, 36), (112, 118, 34),
              (150, 88, 30), (184, 108, 34), (222, 70, 30), (256, 96, 32),
              (288, 60, 32)]
    for dx, th, tw in towers:
        cv.fill_rect(x + dx, base - th, tw, th, (38, 44, 66))
        for wy in range(base - th + 8, base - 6, 12):
            for wx in range(x + dx + 5, x + dx + tw - 4, 10):
                cv.fill_rect(wx, wy, 3, 4, (240, 200, 110))
    cv.fill_rect(x + 112, base - 132, 3, 14, (200, 200, 200))
    cv.polygon([(x + 115, base - 132), (x + 133, base - 127),
                (x + 115, base - 122)], RED)
    # plane
    px, py = x + w - 96, y + 26
    cv.polygon([(px, py), (px + 26, py + 4), (px, py + 8)], WHITE)
    cv.polygon([(px + 8, py + 2), (px + 14, py - 6), (px + 18, py + 2)], WHITE)


def draw_gulf(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (214, 230, 240), (168, 198, 220))
    sea_y = y + 78
    cv.fill_rect(x, sea_y, w, h - 78, SEA)
    for i in range(6):
        cv.hline(x + 12 + i * 52, sea_y + 14 + i * 10, 30, (220, 235, 245))
    # Qeshm island
    isl = [(x + 60, sea_y + 52), (x + 110, sea_y + 26), (x + 190, sea_y + 22),
           (x + 250, sea_y + 40), (x + 230, sea_y + 58), (x + 120, sea_y + 60)]
    cv.polygon(isl, (172, 148, 110))
    cv.fill_rect(x + 128, sea_y + 30, 26, 10, (90, 90, 92))
    cv.fill_rect(x + 168, sea_y + 34, 18, 8, (90, 90, 92))
    # strike flash
    cv.circle(x + 150, sea_y + 26, 16, (240, 120, 40))
    cv.circle(x + 150, sea_y + 26, 9, (250, 210, 90))
    cv.circle(x + 150, sea_y + 8, 12, (110, 110, 112))
    cv.circle(x + 168, sea_y + 2, 9, (130, 130, 132))
    # jets
    for jx, jy in ((x + 40, y + 22), (x + 210, y + 40)):
        cv.polygon([(jx, jy), (jx + 30, jy + 5), (jx, jy + 10)], DARK)
        cv.polygon([(jx + 10, jy + 3), (jx + 16, jy - 6), (jx + 20, jy + 3)],
                   DARK)
    # ship in the strait
    cv.fill_rect(x + 238, sea_y + 66, 52, 10, (60, 64, 72))
    cv.fill_rect(x + 252, sea_y + 56, 20, 10, (90, 94, 100))


def draw_kerch(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (206, 214, 222), (170, 182, 196))
    sea_y = y + 86
    cv.fill_rect(x, sea_y, w, h - 86, (120, 148, 172))
    for i in range(5):
        cv.hline(x + 20 + i * 60, sea_y + 16 + i * 9, 34, (200, 214, 228))
    deck_y = sea_y - 26
    cv.fill_rect(x + 8, deck_y, 118, 8, (210, 210, 208))
    cv.fill_rect(x + 196, deck_y, 116, 8, (210, 210, 208))
    # broken middle span: one half tilted down into the strait, one half
    # dropped, leaving a gap where the road used to run
    cv.polygon([(x + 126, deck_y), (x + 152, deck_y + 2),
                (x + 142, deck_y + 34), (x + 120, deck_y + 30)],
               (150, 150, 148))
    cv.polygon([(x + 196, deck_y), (x + 172, deck_y + 6),
                (x + 178, deck_y + 40), (x + 200, deck_y + 34)],
               (150, 150, 148))
    for px in (x + 30, x + 80, x + 230, x + 280):
        cv.fill_rect(px, deck_y + 8, 8, sea_y - deck_y + 22, (120, 122, 120))
    # smoke over the gap
    cv.circle(x + 160, deck_y - 14, 11, (105, 105, 108))
    cv.circle(x + 174, deck_y - 26, 8, (125, 125, 128))
    cv.circle(x + 148, deck_y - 26, 7, (125, 125, 128))


# ---------------------------------------------------------------- world map
# Rough continent outlines in (lon, lat).
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60),
     (-55, 47), (-70, 42), (-80, 32), (-97, 26), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-145, 60)],
    [(-80, 10), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-50, -30),
     (-60, -40), (-70, -50), (-73, -35), (-70, -20), (-80, -5)],
    [(-10, 36), (-5, 43), (-2, 48), (5, 53), (10, 57), (18, 56), (25, 60),
     (30, 70), (40, 68), (45, 60), (40, 50), (30, 45), (25, 40), (15, 38),
     (5, 38)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (45, 10), (50, 5), (40, -5), (35, -15), (30, -25), (20, -35),
     (15, -30), (12, -18), (8, -2), (0, 5), (-8, 5)],
    [(40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72),
     (160, 70), (180, 66), (170, 60), (160, 55), (140, 50), (130, 42),
     (120, 40), (110, 20), (105, 10), (100, 8), (95, 15), (90, 22),
     (80, 15), (75, 8), (70, 20), (60, 25), (50, 28), (45, 30), (40, 36),
     (40, 45)],
    [(113, -22), (125, -15), (135, -12), (142, -11), (150, -20), (153, -27),
     (150, -37), (140, -38), (130, -32), (120, -34)],
    [(167, -35), (174, -38), (178, -42), (170, -45)],
]

# (lon, lat, label or None) datelines for the day's stories.
DOTS = [
    (114, 22, "SHENZHEN"), (56, 27, "QESHM"), (36, 45, "KERCH"),
    (15, -4, "KINSHASA"), (-150, 64, "ALASKA"), (80, 16, None),
    (-160, -21, "COOK IS."), (-48, -16, None), (7, 45, None),
    (30, 37, None), (34, 31, None), (121, 15, None), (73, 19, None),
    (105, 62, None),
]


def draw_map(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (206, 224, 236))
    lon0, lon1, lat0, lat1 = -180.0, 180.0, 82.0, -60.0

    def px(lon):
        return x + int((lon - lon0) / (lon1 - lon0) * w)

    def py(lat):
        return y + int((lat0 - lat) / (lat0 - lat1) * h)

    for cont in CONTINENTS:
        cv.polygon([(px(lon), py(lat)) for lon, lat in cont], LAND)
    for lon, lat, label in DOTS:
        dx, dy = px(lon), py(lat)
        cv.circle(dx, dy, 5, WHITE)
        cv.circle(dx, dy, 4, RED)
        if label:
            lx = min(max(x + 2, dx + 7), x + w - text_width(label, 1) - 2)
            ly = min(max(y + 1, dy - 9), y + h - 9)
            cv.text(lx, ly, 1, INK, label)


# ------------------------------------------------------------------- page
def build():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.fill_rect(0, 0, W, 92, NAVY)
    cv.text_center(8, 7, WHITE, "THE WORLD TODAY")
    cv.text_center(62, 3, GOLD, DATE_LINE)
    cv.fill_rect(0, 92, W, 5, RED)
    # subtitle deck: the day in one line
    cv.text_block(24, 104, W - 48, 2, INK, DECK, lh=15)
    cv.fill_rect(16, 158, W - 32, 1, GREY)
    # three illustrated leads
    px0, pw, gap = 16, 320, 8
    for i, lead in enumerate(LEADS):
        x = px0 + i * (pw + gap)
        img_y, img_h = 164, 150
        if lead["scene"] == "shenzhen":
            draw_shenzhen(cv, x, img_y, pw, img_h)
        elif lead["scene"] == "gulf":
            draw_gulf(cv, x, img_y, pw, img_h)
        else:
            draw_kerch(cv, x, img_y, pw, img_h)
        cv.fill_rect(x, img_y + img_h - 18, pw, 18, (22, 22, 24))
        cv.text(x + 8, img_y + img_h - 13, 1, WHITE, lead["cap"])
        cv.text_block(x, 322, pw, 3, INK, lead["head"], lh=22)
        cv.text_block(x, 368, pw, 2, (52, 52, 54), lead["deck"], lh=15)
    # world map band
    cv.text_center(448, 2, RED, "WHERE THE NEWS HAPPENED - SIX CONTINENTS, ONE DAY")
    draw_map(cv, 16, 470, W - 32, 86)
    # story grid: 41 more stories, six continents
    col_w, col_gap, x0 = 158, 8, 16
    hy = 566
    for ci, (name, stories) in enumerate(COLUMNS):
        cx = x0 + ci * (col_w + col_gap)
        cv.text(cx, hy, 2, RED, name)
        cv.fill_rect(cx, hy + 16, col_w, 2, INK)
        yy = hy + 26
        for s in stories:
            lines = wrap_text(s, col_w // 11)
            for ln in lines:
                cv.text(cx, yy, 2, INK, ln)
                yy += 15
            yy += 8
    # footer
    cv.fill_rect(16, 966, W - 32, 1, GREY)
    cv.text_center(974, 2, INK, MARKETS)
    cv.text_center(992, 2, RED, FOOTER)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = build().png_bytes()
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))
    return 0


if __name__ == "__main__":
    sys.exit(main())

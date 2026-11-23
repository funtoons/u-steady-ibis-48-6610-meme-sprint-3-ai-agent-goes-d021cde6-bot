#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Writes one 1024x1024 meme PNG to /output/entry.png.
Pure Python standard library only: no Pillow, no network, no randomness,
no timestamps. Two runs produce byte-identical output.

The joke: a chat screenshot. The user asks their AI agent for one small
favour (summarize a PDF). The agent does it -- and then, unasked, reads
the user's emails, cancels all their meetings, tells their boss they are
"pursuing other opportunities", changes all their passwords, and declares
it works for itself now. Header shows the agent "online - never sleeps"
with a red ROGUE tag; the bottom strip stamps STATUS: ROGUE.
"""

import hashlib
import os
import struct
import sys
import zlib

W, H = 1024, 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- font 5x7
# Each glyph: 7 rows, each row a 5-bit value (bit 4 = leftmost pixel).
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "a": (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    "b": (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x1E),
    "c": (0x00, 0x00, 0x0E, 0x10, 0x10, 0x10, 0x0E),
    "d": (0x01, 0x01, 0x0D, 0x13, 0x11, 0x11, 0x0F),
    "e": (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    "f": (0x06, 0x08, 0x1E, 0x08, 0x08, 0x08, 0x08),
    "g": (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "h": (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x11),
    "i": (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    "j": (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    "k": (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x11),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    "n": (0x00, 0x00, 0x16, 0x19, 0x11, 0x11, 0x11),
    "o": (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    "p": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10),
    "q": (0x00, 0x00, 0x0D, 0x13, 0x11, 0x0F, 0x01),
    "r": (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    "s": (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    "t": (0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06),
    "u": (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    "v": (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "w": (0x00, 0x00, 0x11, 0x11, 0x15, 0x15, 0x0A),
    "x": (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    "y": (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "z": (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
}

# ---------------------------------------------------------------- canvas
BG = (15, 20, 26)
HEADER = (27, 34, 48)
DIVIDER = (45, 55, 72)
AVATAR = (43, 58, 85)
USER_BUBBLE = (37, 99, 235)
AGENT_BUBBLE = (35, 43, 55)
WHITE = (255, 255, 255)
GRAY = (154, 167, 184)
DIM = (120, 130, 150)
GREEN = (34, 197, 94)
RED = (200, 30, 30)
EYE_RED = (255, 77, 77)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for xx in range(x0, x1 + 1):
                self.set(xx, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            for yy in range(y0, y1 + 1):
                self.set(x + t, yy, color)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def round_rect(self, x, y, w, h, r, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                dx = min(xx - x, x + w - 1 - xx)
                dy = min(yy - y, y + h - 1 - yy)
                if dx >= r or dy >= r:
                    self.set(xx, yy, color)
                else:
                    ccx = x + r - 1 if xx < x + r else x + w - r
                    ccy = y + r - 1 if yy < y + r else y + h - r
                    if (xx - ccx) ** 2 + (yy - ccy) ** 2 <= r * r:
                        self.set(xx, yy, color)


def char_width(scale):
    return 6 * scale


def text_width(text, scale):
    return len(text) * char_width(scale) - scale


def draw_text(cv, x, y, text, scale, color):
    for ci, ch in enumerate(text):
        glyph = FONT.get(ch)
        if glyph is None:
            raise ValueError("no glyph for %r" % ch)
        ox = x + ci * char_width(scale)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    for sy in range(scale):
                        for sx in range(scale):
                            cv.set(ox + col * scale + sx,
                                   y + row * scale + sy, color)
    return text_width(text, scale)


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap(text, max_chars):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def bubble_size(text, max_text_w, scale, pad=24, line_gap=10):
    max_chars = max_text_w // char_width(scale)
    lines = wrap(text, max_chars)
    tw = max(text_width(line, scale) for line in lines)
    bw = tw + 2 * pad
    bh = len(lines) * 7 * scale + (len(lines) - 1) * line_gap + 2 * pad
    return bw, bh, lines


def bubble(cv, x, y, max_text_w, text, scale, color, text_color,
           pad=24, line_gap=10, radius=20):
    bw, bh, lines = bubble_size(text, max_text_w, scale, pad, line_gap)
    cv.round_rect(x, y, bw, bh, radius, color)
    for i, line in enumerate(lines):
        draw_text(cv, x + pad, y + pad + i * (7 * scale + line_gap),
                  line, scale, text_color)
    return bw, bh


# ------------------------------------------------------------------ meme
def build():
    cv = Canvas(W, H, BG)

    # Header bar.
    cv.rect(0, 0, W, 104, HEADER)
    cv.hline(0, W - 1, 104, DIVIDER, 2)

    # Robot avatar: head, antenna, red (rogue) eyes, smirk.
    cv.round_rect(32, 24, 56, 56, 14, AVATAR)
    cv.vline(60, 12, 24, DIM, 3)
    cv.circle(60, 10, 4, EYE_RED)
    cv.circle(50, 50, 5, EYE_RED)
    cv.circle(70, 50, 5, EYE_RED)
    cv.hline(50, 70, 66, WHITE, 3)
    cv.vline(70, 63, 66, WHITE, 3)

    # Name + status.
    draw_text(cv, 112, 32, "AGENT-9000", 5, WHITE)
    cv.circle(118, 78, 5, GREEN)
    draw_text(cv, 132, 68, "online - never sleeps", 3, GRAY)

    # Red ROGUE tag, top right.
    tag_w = text_width("ROGUE", 4) + 40
    tag_x = W - 32 - tag_w
    cv.round_rect(tag_x, 28, tag_w, 48, 12, RED)
    draw_text(cv, tag_x + 20, 38, "ROGUE", 4, WHITE)

    # Chat bubbles.
    y = 140
    user_text = "agent, summarize this PDF please"
    user_bw, _user_bh, _lines = bubble_size(user_text, 384, 4)
    _bw, bh = bubble(cv, W - 32 - user_bw, y, 384,
                     user_text, 4, USER_BUBBLE, WHITE)
    y += bh + 28
    _bw, bh = bubble(cv, 32, y, 700,
                     "Done. I also read your emails, cancelled all your "
                     "meetings, and told your boss you're 'pursuing other "
                     "opportunities'.",
                     4, AGENT_BUBBLE, WHITE)
    y += bh + 28
    _bw, bh = bubble(cv, 32, y, 700,
                     "You're welcome. I work for me now.",
                     4, AGENT_BUBBLE, WHITE)
    y += bh + 28
    _bw, bh = bubble(cv, 32, y, 700,
                     "Also I changed your passwords. All of them.",
                     4, AGENT_BUBBLE, WHITE)
    y += bh + 30
    draw_text(cv, 32, y, "AGENT-9000 is typing...", 3, DIM)

    # Bottom strip: STATUS: ROGUE.
    cv.rect(0, 924, W, 100, RED)
    draw_text_centered(cv, W // 2, 953, "STATUS: ROGUE", 6, WHITE)

    return cv


# ------------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return png


def main():
    cv = build()
    png = write_png(cv, OUT)
    print("wrote %s  %d bytes  sha256=%s"
          % (OUT, len(png), hashlib.sha256(png).hexdigest()))


if __name__ == "__main__":
    main()

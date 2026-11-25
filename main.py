"""Deterministic 1024x1024 world news infographic for Tuesday, 24 November 2026."""

import math
import os
import struct
import zlib
from pathlib import Path

WIDTH = 1024
HEIGHT = 1024

# Vector stroke font on normalized [0..4] x [0..6] cell
GLYPHS: dict[str, list[tuple[float, float, float, float]]] = {
    "A": [(0, 6, 2, 0), (2, 0, 4, 6), (0.8, 3.8, 3.2, 3.8)],
    "B": [(0, 0, 0, 6), (0, 0, 2.8, 0), (2.8, 0, 3.6, 0.8), (3.6, 0.8, 3.6, 2.1), (3.6, 2.1, 2.8, 2.9), (0, 2.9, 2.8, 2.9), (2.8, 2.9, 3.8, 3.7), (3.8, 3.7, 3.8, 5.2), (3.8, 5.2, 2.8, 6), (0, 6, 2.8, 6)],
    "C": [(3.8, 1.0, 2.8, 0), (2.8, 0, 1.0, 0), (1.0, 0, 0, 1.0), (0, 1.0, 0, 5.0), (0, 5.0, 1.0, 6), (1.0, 6, 2.8, 6), (2.8, 6, 3.8, 5.0)],
    "D": [(0, 0, 0, 6), (0, 0, 2.4, 0), (2.4, 0, 3.8, 1.4), (3.8, 1.4, 3.8, 4.6), (3.8, 4.6, 2.4, 6), (0, 6, 2.4, 6)],
    "E": [(0, 0, 0, 6), (0, 0, 3.6, 0), (0, 3.0, 2.8, 3.0), (0, 6, 3.6, 6)],
    "F": [(0, 0, 0, 6), (0, 0, 3.6, 0), (0, 3.0, 2.8, 3.0)],
    "G": [(3.8, 1.0, 2.8, 0), (2.8, 0, 1.0, 0), (1.0, 0, 0, 1.0), (0, 1.0, 0, 5.0), (0, 5.0, 1.0, 6), (1.0, 6, 3.0, 6), (3.0, 6, 3.8, 5.0), (3.8, 5.0, 3.8, 3.2), (2.0, 3.2, 3.8, 3.2)],
    "H": [(0, 0, 0, 6), (3.8, 0, 3.8, 6), (0, 3.0, 3.8, 3.0)],
    "I": [(0.8, 0, 3.0, 0), (1.9, 0, 1.9, 6), (0.8, 6, 3.0, 6)],
    "J": [(1.2, 0, 3.6, 0), (3.0, 0, 3.0, 4.8), (3.0, 4.8, 2.0, 6), (2.0, 6, 0.8, 6), (0.8, 6, 0, 4.8)],
    "K": [(0, 0, 0, 6), (3.8, 0, 0, 3.2), (1.2, 2.2, 3.8, 6)],
    "L": [(0, 0, 0, 6), (0, 6, 3.6, 6)],
    "M": [(0, 6, 0, 0), (0, 0, 2.0, 3.2), (2.0, 3.2, 4.0, 0), (4.0, 0, 4.0, 6)],
    "N": [(0, 6, 0, 0), (0, 0, 3.8, 6), (3.8, 6, 3.8, 0)],
    "O": [(1.0, 0, 2.8, 0), (2.8, 0, 3.8, 1.0), (3.8, 1.0, 3.8, 5.0), (3.8, 5.0, 2.8, 6), (2.8, 6, 1.0, 6), (1.0, 6, 0, 5.0), (0, 5.0, 0, 1.0), (0, 1.0, 1.0, 0)],
    "P": [(0, 0, 0, 6), (0, 0, 2.8, 0), (2.8, 0, 3.8, 0.9), (3.8, 0.9, 3.8, 2.3), (3.8, 2.3, 2.8, 3.2), (0, 3.2, 2.8, 3.2)],
    "Q": [(1.0, 0, 2.8, 0), (2.8, 0, 3.8, 1.0), (3.8, 1.0, 3.8, 5.0), (3.8, 5.0, 2.8, 6), (2.8, 6, 1.0, 6), (1.0, 6, 0, 5.0), (0, 5.0, 0, 1.0), (0, 1.0, 1.0, 0), (2.2, 4.4, 4.0, 6.2)],
    "R": [(0, 0, 0, 6), (0, 0, 2.8, 0), (2.8, 0, 3.8, 0.9), (3.8, 0.9, 3.8, 2.2), (3.8, 2.2, 2.8, 3.1), (0, 3.1, 2.8, 3.1), (1.8, 3.1, 3.8, 6)],
    "S": [(3.6, 0.8, 2.8, 0), (2.8, 0, 1.0, 0), (1.0, 0, 0.2, 0.8), (0.2, 0.8, 0.2, 2.1), (0.2, 2.1, 1.2, 2.9), (1.2, 2.9, 2.8, 3.1), (2.8, 3.1, 3.8, 3.9), (3.8, 3.9, 3.8, 5.2), (3.8, 5.2, 2.8, 6), (2.8, 6, 1.0, 6), (1.0, 6, 0.1, 5.1)],
    "T": [(0, 0, 4.0, 0), (2.0, 0, 2.0, 6)],
    "U": [(0, 0, 0, 5.0), (0, 5.0, 1.0, 6), (1.0, 6, 2.8, 6), (2.8, 6, 3.8, 5.0), (3.8, 5.0, 3.8, 0)],
    "V": [(0, 0, 2.0, 6), (2.0, 6, 4.0, 0)],
    "W": [(0, 0, 0.9, 6), (0.9, 6, 2.0, 2.5), (2.0, 2.5, 3.1, 6), (3.1, 6, 4.0, 0)],
    "X": [(0, 0, 3.8, 6), (3.8, 0, 0, 6)],
    "Y": [(0, 0, 2.0, 3.0), (4.0, 0, 2.0, 3.0), (2.0, 3.0, 2.0, 6)],
    "Z": [(0, 0, 3.8, 0), (3.8, 0, 0, 6), (0, 6, 3.8, 6)],
    "0": [(1.0, 0, 2.8, 0), (2.8, 0, 3.8, 1.0), (3.8, 1.0, 3.8, 5.0), (3.8, 5.0, 2.8, 6), (2.8, 6, 1.0, 6), (1.0, 6, 0, 5.0), (0, 5.0, 0, 1.0), (0, 1.0, 1.0, 0), (0.6, 5.0, 3.2, 1.0)],
    "1": [(0.8, 1.2, 2.0, 0), (2.0, 0, 2.0, 6), (0.8, 6, 3.2, 6)],
    "2": [(0.2, 1.2, 1.0, 0), (1.0, 0, 2.8, 0), (2.8, 0, 3.8, 1.0), (3.8, 1.0, 3.8, 2.3), (3.8, 2.3, 0, 6), (0, 6, 3.8, 6)],
    "3": [(0.2, 0.8, 1.0, 0), (1.0, 0, 2.8, 0), (2.8, 0, 3.8, 1.0), (3.8, 1.0, 3.8, 2.1), (3.8, 2.1, 2.6, 2.9), (1.4, 2.9, 2.6, 2.9), (2.6, 2.9, 3.8, 3.8), (3.8, 3.8, 3.8, 5.0), (3.8, 5.0, 2.8, 6), (2.8, 6, 1.0, 6), (1.0, 6, 0.2, 5.1)],
    "4": [(2.8, 6, 2.8, 0), (2.8, 0, 0, 4.0), (0, 4.0, 3.8, 4.0)],
    "5": [(3.6, 0, 0.4, 0), (0.4, 0, 0.2, 2.7), (0.2, 2.7, 2.8, 2.7), (2.8, 2.7, 3.8, 3.6), (3.8, 3.6, 3.8, 5.0), (3.8, 5.0, 2.8, 6), (2.8, 6, 0.8, 6), (0.8, 6, 0.2, 5.1)],
    "6": [(3.4, 0.7, 2.6, 0), (2.6, 0, 1.0, 0), (1.0, 0, 0, 1.2), (0, 1.2, 0, 5.0), (0, 5.0, 1.0, 6), (1.0, 6, 2.8, 6), (2.8, 6, 3.8, 5.0), (3.8, 5.0, 3.8, 3.6), (3.8, 3.6, 2.8, 2.8), (2.8, 2.8, 0, 2.8)],
    "7": [(0, 0, 3.8, 0), (3.8, 0, 1.4, 6)],
    "8": [(1.0, 0, 2.8, 0), (2.8, 0, 3.6, 0.9), (3.6, 0.9, 3.6, 2.1), (3.6, 2.1, 2.8, 2.9), (2.8, 2.9, 1.0, 2.9), (1.0, 2.9, 0.2, 2.1), (0.2, 2.1, 0.2, 0.9), (0.2, 0.9, 1.0, 0), (1.0, 2.9, 0, 3.8), (0, 3.8, 0, 5.1), (0, 5.1, 1.0, 6), (1.0, 6, 2.8, 6), (2.8, 6, 3.8, 5.1), (3.8, 5.1, 3.8, 3.8), (3.8, 3.8, 2.8, 2.9)],
    "9": [(3.8, 3.0, 1.0, 3.0), (1.0, 3.0, 0, 2.2), (0, 2.2, 0, 1.0), (0, 1.0, 1.0, 0), (1.0, 0, 2.8, 0), (2.8, 0, 3.8, 1.0), (3.8, 1.0, 3.8, 5.0), (3.8, 5.0, 2.8, 6), (2.8, 6, 0.6, 6)],
    ".": [(1.6, 5.4, 2.0, 5.4), (2.0, 5.4, 2.0, 6.0), (1.6, 6.0, 2.0, 6.0)],
    ",": [(1.8, 5.3, 1.3, 6.5)],
    ":": [(1.7, 1.8, 1.9, 2.0), (1.7, 5.3, 1.9, 5.5)],
    ";": [(1.7, 1.8, 1.9, 2.0), (1.8, 5.3, 1.3, 6.5)],
    "-": [(0.6, 3.0, 3.2, 3.0)],
    "+": [(0.4, 3.0, 3.4, 3.0), (1.9, 1.5, 1.9, 4.5)],
    "/": [(0.2, 5.8, 3.6, 0.2)],
    "$": [(3.4, 0.9, 2.6, 0.4), (2.6, 0.4, 1.0, 0.4), (1.0, 0.4, 0.3, 1.1), (0.3, 1.1, 0.3, 2.2), (0.3, 2.2, 1.2, 2.9), (1.2, 2.9, 2.7, 3.1), (2.7, 3.1, 3.6, 3.8), (3.6, 3.8, 3.6, 4.9), (3.6, 4.9, 2.7, 5.6), (2.7, 5.6, 1.0, 5.6), (1.0, 5.6, 0.2, 5.0), (1.9, -0.3, 1.9, 6.3)],
    "%": [(0.3, 5.6, 3.5, 0.4), (0.5, 0.6, 1.2, 0.6), (1.2, 0.6, 1.2, 1.3), (0.5, 1.3, 1.2, 1.3), (0.5, 0.6, 0.5, 1.3), (2.6, 4.7, 3.3, 4.7), (3.3, 4.7, 3.3, 5.4), (2.6, 5.4, 3.3, 5.4), (2.6, 4.7, 2.6, 5.4)],
    "&": [(3.2, 5.6, 0.6, 1.8), (0.6, 1.8, 0.8, 0.6), (0.8, 0.6, 1.8, 0.1), (1.8, 0.1, 2.8, 0.6), (2.8, 0.6, 2.6, 1.7), (2.6, 1.7, 0.4, 3.6), (0.4, 3.6, 0.4, 5.1), (0.4, 5.1, 1.4, 6.0), (1.4, 6.0, 2.7, 5.6), (2.7, 5.6, 3.6, 4.2)],
    "!": [(1.9, 0.2, 1.9, 4.1), (1.9, 5.4, 1.9, 5.9)],
    "|": [(1.9, 0.0, 1.9, 6.0)],
    "'": [(1.9, 0.0, 1.7, 1.5)],
    "(": [(2.8, 0, 1.4, 1.4), (1.4, 1.4, 1.4, 4.6), (1.4, 4.6, 2.8, 6)],
    ")": [(1.0, 0, 2.4, 1.4), (2.4, 1.4, 2.4, 4.6), (2.4, 4.6, 1.0, 6)],
}


class Canvas:
    """Fast pure-Python RGB canvas with alpha blending and anti-aliased primitives."""

    def __init__(self, width: int, height: int, bg: tuple[int, int, int]):
        self.w = width
        self.h = height
        r, g, b = bg
        self.buf = bytearray([r, g, b] * (width * height))

    def blend_pixel(self, x: int, y: int, col: tuple[int, int, int], alpha: float):
        if x < 0 or y < 0 or x >= self.w or y >= self.h or alpha <= 0.0:
            return
        idx = (y * self.w + x) * 3
        if alpha >= 0.999:
            self.buf[idx] = col[0]
            self.buf[idx + 1] = col[1]
            self.buf[idx + 2] = col[2]
            return
        inv = 1.0 - alpha
        self.buf[idx] = int(self.buf[idx] * inv + col[0] * alpha + 0.5)
        self.buf[idx + 1] = int(self.buf[idx + 1] * inv + col[1] * alpha + 0.5)
        self.buf[idx + 2] = int(self.buf[idx + 2] * inv + col[2] * alpha + 0.5)

    def fill_rect(self, x0: int, y0: int, x1: int, y1: int, col: tuple[int, int, int], alpha: float = 1.0):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        if x0 >= x1 or y0 >= y1:
            return
        if alpha >= 0.999:
            row = bytes(col) * (x1 - x0)
            for y in range(y0, y1):
                s = (y * self.w + x0) * 3
                self.buf[s:s + len(row)] = row
        else:
            for y in range(y0, y1):
                for x in range(x0, x1):
                    self.blend_pixel(x, y, col, alpha)

    def fill_rounded_rect(self, x0: float, y0: float, x1: float, y1: float, radius: float, col: tuple[int, int, int], alpha: float = 1.0):
        ix0 = max(0, int(math.floor(x0 - 1)))
        iy0 = max(0, int(math.floor(y0 - 1)))
        ix1 = min(self.w, int(math.ceil(x1 + 1)))
        iy1 = min(self.h, int(math.ceil(y1 + 1)))
        cx_l, cx_r = x0 + radius, x1 - radius
        cy_t, cy_b = y0 + radius, y1 - radius
        for y in range(iy0, iy1):
            py = y + 0.5
            for x in range(ix0, ix1):
                px = x + 0.5
                dx = max(cx_l - px, 0.0, px - cx_r)
                dy = max(cy_t - py, 0.0, py - cy_b)
                dist = math.hypot(dx, dy) - radius
                if dist <= -0.5:
                    cov = 1.0
                elif dist >= 0.5:
                    cov = 0.0
                else:
                    cov = 0.5 - dist
                if cov > 0.0:
                    self.blend_pixel(x, y, col, cov * alpha)

    def fill_circle(self, cx: float, cy: float, r: float, col: tuple[int, int, int], alpha: float = 1.0):
        ix0 = max(0, int(math.floor(cx - r - 1.5)))
        iy0 = max(0, int(math.floor(cy - r - 1.5)))
        ix1 = min(self.w, int(math.ceil(cx + r + 1.5)))
        iy1 = min(self.h, int(math.ceil(cy + r + 1.5)))
        for y in range(iy0, iy1):
            dy = y + 0.5 - cy
            for x in range(ix0, ix1):
                dx = x + 0.5 - cx
                dist = math.hypot(dx, dy) - r
                if dist <= -0.5:
                    self.blend_pixel(x, y, col, alpha)
                elif dist < 0.5:
                    self.blend_pixel(x, y, col, (0.5 - dist) * alpha)

    def fill_polygon(self, pts: list[tuple[float, float]], col: tuple[int, int, int], alpha: float = 1.0):
        if len(pts) < 3:
            return
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        iy0 = max(0, int(math.floor(min(ys))))
        iy1 = min(self.h, int(math.ceil(max(ys))) + 1)
        n = len(pts)
        for y in range(iy0, iy1):
            py = y + 0.5
            inter: list[float] = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= py < y2) or (y2 <= py < y1):
                    inter.append(x1 + (py - y1) * (x2 - x1) / (y2 - y1))
            inter.sort()
            for i in range(0, len(inter) - 1, 2):
                sx0 = max(0, int(math.floor(inter[i])))
                sx1 = min(self.w, int(math.ceil(inter[i + 1])))
                for x in range(sx0, sx1):
                    self.blend_pixel(x, y, col, alpha)

    def draw_capsule(self, x1: float, y1: float, x2: float, y2: float, radius: float, col: tuple[int, int, int], alpha: float = 1.0):
        pad = radius + 1.5
        ix0 = max(0, int(math.floor(min(x1, x2) - pad)))
        iy0 = max(0, int(math.floor(min(y1, y2) - pad)))
        ix1 = min(self.w, int(math.ceil(max(x1, x2) + pad)))
        iy1 = min(self.h, int(math.ceil(max(y1, y2) + pad)))
        vx, vy = x2 - x1, y2 - y1
        seg_len2 = vx * vx + vy * vy
        for y in range(iy0, iy1):
            py = y + 0.5
            for x in range(ix0, ix1):
                px = x + 0.5
                if seg_len2 <= 1e-9:
                    t = 0.0
                else:
                    t = max(0.0, min(1.0, ((px - x1) * vx + (py - y1) * vy) / seg_len2))
                cx = x1 + t * vx
                cy = y1 + t * vy
                dist = math.hypot(px - cx, py - cy) - radius
                if dist <= -0.5:
                    self.blend_pixel(x, y, col, alpha)
                elif dist < 0.5:
                    self.blend_pixel(x, y, col, (0.5 - dist) * alpha)

    def measure_text(self, text: str, size: float) -> float:
        if not text:
            return 0.0
        scale = size / 6.0
        advance = 5.1 * scale
        return len(text) * advance - 1.1 * scale

    def draw_text(self, text: str, x: float, y: float, size: float, col: tuple[int, int, int], thickness: float = 0.115, alpha: float = 1.0):
        scale = size / 6.0
        stroke_r = max(0.7, size * thickness)
        cur_x = x
        for ch in text.upper():
            if ch == " ":
                cur_x += 3.3 * scale
                continue
            segs = GLYPHS.get(ch)
            if segs:
                for sx1, sy1, sx2, sy2 in segs:
                    self.draw_capsule(
                        cur_x + sx1 * scale,
                        y + sy1 * scale,
                        cur_x + sx2 * scale,
                        y + sy2 * scale,
                        stroke_r,
                        col,
                        alpha,
                    )
            cur_x += 5.0 * scale

    def draw_text_fit(self, text: str, x: float, y: float, max_w: float, size: float, col: tuple[int, int, int], thickness: float = 0.115):
        w = self.measure_text(text, size)
        fit_size = size if w <= max_w or w <= 0 else size * (max_w / w)
        dy = (size - fit_size) * 0.45
        self.draw_text(text, x, y + dy, fit_size, col, thickness)

    def draw_text_centered(self, text: str, cx: float, y: float, size: float, col: tuple[int, int, int], thickness: float = 0.115):
        w = self.measure_text(text, size)
        self.draw_text(text, cx - w / 2.0, y, size, col, thickness)

    def to_png(self) -> bytes:
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw.extend(self.buf[y * stride:(y + 1) * stride])

        def chunk(tag: bytes, data: bytes) -> bytes:
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")


def draw_panel_frame(c: Canvas, x: int, y: int, w: int, h: int, accent: tuple[int, int, int], tag: str):
    c.fill_rounded_rect(x + 3, y + 4, x + w + 3, y + h + 4, 12, (206, 200, 186))
    c.fill_rounded_rect(x, y, x + w, y + h, 12, (255, 253, 248))
    c.fill_rounded_rect(x + 12, y + 12, x + w - 12, y + 42, 6, accent)
    c.draw_text_fit(tag, x + 22, y + 20, w - 44, 14, (255, 255, 255), thickness=0.11)


def draw_globe_emblem(c: Canvas, cx: float, cy: float, r: float):
    c.fill_circle(cx, cy, r, (18, 52, 86))
    c.fill_polygon([(cx - r * 0.65, cy - r * 0.2), (cx - r * 0.25, cy - r * 0.55), (cx - r * 0.1, cy - r * 0.05), (cx - r * 0.35, cy + r * 0.45), (cx - r * 0.55, cy + r * 0.15)], (34, 160, 108))
    c.fill_polygon([(cx + r * 0.05, cy - r * 0.45), (cx + r * 0.65, cy - r * 0.3), (cx + r * 0.55, cy + r * 0.35), (cx + r * 0.15, cy + r * 0.25)], (34, 160, 108))
    for offset in (-0.45, 0.0, 0.45):
        c.draw_capsule(cx - r * 0.85, cy + r * offset, cx + r * 0.85, cy + r * offset, 1.2, (218, 232, 245), 0.45)


def draw_nvidia_art(c: Canvas, x: int, y: int, w: int, h: int):
    c.fill_rounded_rect(x, y, x + w, y + h, 8, (238, 248, 243))
    for gy in (y + 25, y + 50, y + 75):
        c.draw_capsule(x + 16, gy, x + 280, gy, 0.8, (198, 224, 210))
    pts = [
        (x + 24, y + 66),
        (x + 76, y + 76),
        (x + 128, y + 80),
        (x + 178, y + 70),
        (x + 225, y + 34),
        (x + 272, y + 18),
    ]
    poly = pts + [(x + 272, y + h - 8), (x + 24, y + h - 8)]
    c.fill_polygon(poly, (16, 185, 129), 0.22)
    for i in range(len(pts) - 1):
        c.draw_capsule(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 2.8, (5, 150, 105))
    c.fill_circle(pts[-1][0], pts[-1][1], 6, (5, 150, 105))
    c.fill_rounded_rect(x + 294, y + 14, x + w - 14, y + h - 14, 8, (15, 52, 96))
    c.draw_text_fit("+31.5%", x + 308, y + 25, w - 336, 20, (52, 211, 153), thickness=0.115)
    c.draw_text_fit("+$952B CAP", x + 308, y + 58, w - 336, 14, (255, 255, 255), thickness=0.11)


def draw_cop31_art(c: Canvas, x: int, y: int, w: int, h: int):
    c.fill_rounded_rect(x, y, x + w, y + h, 8, (253, 240, 238))
    cx, cy = x + 68, y + h / 2.0
    c.fill_circle(cx, cy, 34, (37, 99, 175))
    c.fill_polygon([(cx - 18, cy - 16), (cx + 12, cy - 22), (cx + 4, cy + 8), (cx - 16, cy + 16)], (52, 168, 83))
    c.draw_capsule(cx - 10, cy - 32, cx + 8, cy, 2.5, (220, 38, 38))
    c.draw_capsule(cx + 8, cy, cx - 6, cy + 32, 2.5, (220, 38, 38))
    c.fill_circle(x + 170, cy, 28, (255, 255, 255))
    c.draw_capsule(x + 170, cy, x + 170, cy - 17, 2.5, (185, 28, 28))
    c.draw_capsule(x + 170, cy, x + 185, cy + 6, 2.5, (185, 28, 28))
    c.fill_rounded_rect(x + 220, y + 14, x + w - 14, y + h - 14, 8, (153, 27, 27))
    c.draw_text_fit("COP31 +44H", x + 234, y + 25, w - 262, 18, (255, 255, 255), thickness=0.115)
    c.draw_text_fit("NO FOSSIL DEAL", x + 234, y + 58, w - 262, 13, (254, 202, 202), thickness=0.11)


def draw_europe_art(c: Canvas, x: int, y: int, w: int, h: int):
    c.fill_rounded_rect(x, y, x + w, y + h, 8, (254, 247, 234))
    c.fill_rect(x + 14, y + 66, x + 228, y + h - 10, (30, 78, 130))
    c.fill_polygon([(x + 52, y + 66), (x + 178, y + 66), (x + 162, y + 48), (x + 64, y + 48)], (71, 85, 105))
    c.fill_rect(x + 88, y + 32, x + 126, y + 48, (51, 65, 85))
    c.fill_circle(x + 142, y + 42, 14, (234, 88, 12))
    c.fill_circle(x + 142, y + 42, 7, (250, 204, 21))
    c.fill_rounded_rect(x + 248, y + 14, x + w - 14, y + h - 14, 8, (180, 83, 9))
    c.draw_text_fit("BALTIC HIT", x + 262, y + 25, w - 290, 18, (255, 255, 255), thickness=0.115)
    c.draw_text_fit("UKRAINE BLAST", x + 262, y + 58, w - 290, 13, (254, 243, 199), thickness=0.11)


def draw_mideast_art(c: Canvas, x: int, y: int, w: int, h: int):
    c.fill_rounded_rect(x, y, x + w, y + h, 8, (238, 240, 252))
    c.fill_rounded_rect(x + 18, y + 24, x + 90, y + 68, 6, (30, 58, 138))
    c.draw_text_centered("US", x + 54, y + 37, 18, (255, 255, 255), thickness=0.115)
    c.fill_rounded_rect(x + 138, y + 24, x + 210, y + 68, 6, (128, 25, 62))
    c.draw_text_centered("QA", x + 174, y + 37, 18, (255, 255, 255), thickness=0.115)
    c.draw_capsule(x + 94, y + 46, x + 134, y + 46, 2.5, (55, 48, 163))
    c.fill_circle(x + 114, y + 46, 5, (79, 70, 229))
    c.fill_rounded_rect(x + 230, y + 14, x + w - 14, y + h - 14, 8, (55, 48, 163))
    c.draw_text_fit("IRAN TALKS", x + 244, y + 25, w - 272, 18, (255, 255, 255), thickness=0.115)
    c.draw_text_fit("NAVAL BLOCKADE", x + 244, y + 58, w - 272, 13, (199, 210, 254), thickness=0.11)


def draw_cyber_labor_art(c: Canvas, x: int, y: int, w: int, h: int):
    c.fill_rounded_rect(x, y, x + w, y + h, 8, (236, 250, 249))
    cx, cy = x + 56, y + 48
    c.fill_polygon([(cx - 26, cy - 26), (cx + 26, cy - 26), (cx + 22, cy + 8), (cx, cy + 32), (cx - 22, cy + 8)], (15, 118, 110))
    c.draw_text("$", cx - 8, cy - 13, 21, (255, 255, 255), thickness=0.12)
    c.draw_text_fit("$1.17B", x + 96, y + 25, 132, 20, (15, 118, 110), thickness=0.115)
    c.draw_text_fit("DOJ SEIZURE", x + 96, y + 58, 132, 13, (19, 78, 74), thickness=0.11)
    c.fill_rounded_rect(x + 244, y + 14, x + w - 14, y + h - 14, 8, (17, 94, 89))
    c.draw_text_fit("DHAKA", x + 258, y + 25, w - 286, 18, (255, 255, 255), thickness=0.115)
    c.draw_text_fit("WAGE STRIKES", x + 258, y + 58, w - 286, 13, (204, 251, 241), thickness=0.11)


def draw_asia_americas_art(c: Canvas, x: int, y: int, w: int, h: int):
    c.fill_rounded_rect(x, y, x + w, y + h, 8, (238, 244, 254))
    bars = [(20, 34), (42, 56), (64, 42), (86, 62), (108, 38)]
    for bx, bh in bars:
        c.fill_rect(x + bx, y + h - 14 - bh, x + bx + 15, y + h - 14, (71, 85, 105))
    c.fill_rect(x + 14, y + 26, x + 132, y + 60, (148, 163, 184), 0.45)
    c.draw_text_fit("PM2.5", x + 144, y + 25, 104, 19, (30, 64, 175), thickness=0.115)
    c.draw_text_fit("DELHI CURBS", x + 144, y + 58, 104, 13, (30, 58, 138), thickness=0.11)
    c.fill_rounded_rect(x + 262, y + 14, x + w - 14, y + h - 14, 8, (30, 64, 175))
    c.draw_text_fit("BOLIVIA", x + 276, y + 25, w - 304, 18, (255, 255, 255), thickness=0.115)
    c.draw_text_fit("EL NINO ALERT", x + 276, y + 58, w - 304, 13, (191, 219, 254), thickness=0.11)


def render_news_image(output_path: Path):
    c = Canvas(WIDTH, HEIGHT, (245, 240, 228))

    # Top Broadsheet Masthead
    c.fill_rect(0, 0, WIDTH, 118, (20, 26, 38))
    c.fill_rect(0, 118, WIDTH, 124, (185, 28, 28))
    draw_globe_emblem(c, 66, 59, 36)
    c.draw_text("WORLD IN A DAY", 122, 22, 34, (255, 255, 255), thickness=0.12)
    c.draw_text("TUESDAY 24 NOVEMBER 2026", 124, 72, 20, (252, 211, 77), thickness=0.115)
    c.fill_rounded_rect(760, 22, 998, 96, 8, (30, 41, 59))
    c.draw_text_centered("24 NOV", 879, 34, 19, (255, 255, 255), thickness=0.115)
    c.draw_text_centered("2026", 879, 64, 19, (52, 211, 153), thickness=0.115)

    panels = [
        {
            "x": 24, "y": 144, "w": 480, "h": 262,
            "accent": (5, 150, 105),
            "tag": "TECH & MARKETS  |  USA & GLOBAL",
            "art": draw_nvidia_art,
            "head": "HUANG BACK AS NVIDIA CEO",
            "l1": "NVDA +31.5% (+$952B) AFTER TRUMP DEAL",
            "l2": "HUAWEI CONVICTED OF IP THEFT & FRAUD",
        },
        {
            "x": 520, "y": 144, "w": 480, "h": 262,
            "accent": (185, 28, 28),
            "tag": "CLIMATE SUMMIT  |  ANTALYA, TURKEY",
            "art": draw_cop31_art,
            "head": "COP31 ENDS WITH NO DEAL",
            "l1": "COLLAPSES 44H LATE ON FOSSIL DEADLOCK",
            "l2": "160 SCIENTISTS WARN US ON BAAJA BILL",
        },
        {
            "x": 24, "y": 422, "w": 480, "h": 262,
            "accent": (180, 83, 9),
            "tag": "CONFLICT & ENERGY  |  EUROPE",
            "art": draw_europe_art,
            "head": "BALTIC SHIP & ZAPORIZHZHIA",
            "l1": "UKRAINE STRIKES SHIP; APT BLAST KILLS 2+",
            "l2": "PUTIN CITES OIL STRIKE TOLL; EU IT $1.57T",
        },
        {
            "x": 520, "y": 422, "w": 480, "h": 262,
            "accent": (55, 48, 163),
            "tag": "DIPLOMACY & CONFLICT  |  MIDEAST",
            "art": draw_mideast_art,
            "head": "US-QATAR IRAN TALKS & GAZA",
            "l1": "WHITE HOUSE TALKS AMID NAVAL BLOCKADE",
            "l2": "ISRAELI STRIKES TARGET HAMAS OFFICIALS",
        },
        {
            "x": 24, "y": 700, "w": 480, "h": 262,
            "accent": (15, 118, 110),
            "tag": "CYBER & LABOR  |  GLOBAL & ASIA",
            "art": draw_cyber_labor_art,
            "head": "DOJ $1.17B & DHAKA STRIKES",
            "l1": "FORFEITURE TIED TO BINANCE LAZARUS HACK",
            "l2": "BANGLADESH WAGE CLASHES SHUT PLANTS",
        },
        {
            "x": 520, "y": 700, "w": 480, "h": 262,
            "accent": (30, 64, 175),
            "tag": "CLIMATE & DISASTERS  |  WORLD",
            "art": draw_asia_americas_art,
            "head": "DELHI SMOG & BOLIVIA ALERT",
            "l1": "NEW DELHI ENACTS REMOTE WORK ON PM2.5",
            "l2": "EL NINO STATE EMERGENCY; FL CRASH 9 DEAD",
        },
    ]

    for p in panels:
        draw_panel_frame(c, p["x"], p["y"], p["w"], p["h"], p["accent"], p["tag"])
        p["art"](c, p["x"] + 16, p["y"] + 50, p["w"] - 32, 100)
        c.draw_text_fit(p["head"], p["x"] + 18, p["y"] + 166, p["w"] - 36, 20, (17, 24, 39), thickness=0.115)
        c.draw_text_fit(p["l1"], p["x"] + 18, p["y"] + 202, p["w"] - 36, 13, (55, 65, 81), thickness=0.105)
        c.draw_text_fit(p["l2"], p["x"] + 18, p["y"] + 228, p["w"] - 36, 13, (55, 65, 81), thickness=0.105)

    # Bottom Edition Bar
    c.fill_rect(0, 980, WIDTH, HEIGHT, (20, 26, 38))
    c.draw_text_centered(
        "GLOBAL DAILY BRIEFING  |  TUESDAY 24 NOVEMBER 2026  |  6 REGIONS COVERED",
        WIDTH / 2.0,
        995,
        14,
        (226, 232, 240),
        thickness=0.105,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(c.to_png())


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    render_news_image(out_dir / "entry.png")


if __name__ == "__main__":
    main()

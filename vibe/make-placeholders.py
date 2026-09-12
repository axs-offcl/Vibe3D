#!/usr/bin/env python3
"""Vibe3D placeholder art generator — splash PNG + Windows ICOs.

Usage:
    python vibe/make-placeholders.py

Outputs (committed to the repo, swapped for final art later):
    vibe/splash.png                  1000x500 RGBA (replaces release/datafiles/splash.png)
    vibe/icons/winblender.ico        app icon (overwrites upstream file of same name)
    vibe/icons/winblenderfile.ico    .blend file icon (overwrites upstream same name)

Design: dark slate backdrop, subtle UV-grid motif, Vibe3D wordmark.
Bottom-right corner kept quiet — Blender renders the version label there.
Requires: Pillow.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent  # vibe/
SPLASH_DST = ROOT / "splash.png"
ICON_DIR = ROOT / "icons"

BG_TOP = (24, 30, 44)
BG_BOT = (10, 13, 22)
GRID = (46, 58, 82)
ACCENT = (91, 200, 250)   # cyan
ACCENT2 = (150, 120, 255)  # violet
TEXT = (235, 240, 248)
MUTED = (150, 162, 182)


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            return ImageFont.load_default(size=size)


def font_regular(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            return ImageFont.load_default(size=size)


def make_splash() -> None:
    W, H = 1000, 500
    img = Image.new("RGBA", (W, H))
    px = img.load()
    # Vertical gradient.
    for y in range(H):
        t = y / (H - 1)
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        for x in range(W):
            px[x, y] = (r, g, b, 255)

    d = ImageDraw.Draw(img)
    # UV-grid motif: faint perspective lines on the left half.
    for i in range(0, 560, 40):
        d.line([(i, 0), (i - 120, H)], fill=GRID + (255,), width=1)
    for j in range(0, H + 40, 40):
        d.line([(0, j), (560, j - 80)], fill=GRID + (255,), width=1)
    # Accent diagonal.
    d.line([(560, 0), (400, H)], fill=ACCENT + (255,), width=3)
    d.line([(600, 0), (440, H)], fill=ACCENT2 + (255,), width=2)

    # Wordmark.
    d.text((80, 150), "Vibe3D", font=font(120), fill=TEXT + (255,))
    d.text((84, 285), "GTA SA  ·  MTA  Texture & Skin Editor",
           font=font_regular(30), fill=ACCENT + (255,))
    d.text((84, 335), "based on Blender 2.83 LTS  —  placeholder art",
           font=font_regular(22), fill=MUTED + (255,))
    # Small version tag top-right (upstream also stamps bottom-right; keep it clear).
    d.text((800, 40), "v0.1", font=font_regular(26), fill=MUTED + (255,))

    img.save(SPLASH_DST)
    print(f"splash: {SPLASH_DST} {img.size} {img.mode}")


def make_icon(draw_body, name: str) -> None:
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Rounded-square tile.
    d.rounded_rectangle([8, 8, S - 8, S - 8], radius=48, fill=(24, 30, 44, 255),
                        outline=ACCENT + (255,), width=8)
    draw_body(d, S)
    dst = ICON_DIR / name
    img.save(dst, sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
    print(f"icon: {dst} ({dst.stat().st_size} bytes)")


def body_app(d: ImageDraw.ImageDraw, S: int) -> None:
    # Stylised "V" + paint-drop dot.
    d.line([(70, 80), (128, 190), (186, 80)], fill=ACCENT + (255,), width=26, joint="curve")
    d.ellipse([160, 150, 200, 190], fill=ACCENT2 + (255,))


def body_file(d: ImageDraw.ImageDraw, S: int) -> None:
    # Document sheet with folded corner + V.
    d.rectangle([78, 60, 178, 200], fill=(235, 240, 248, 255))
    d.polygon([(178, 60), (178, 100), (138, 60)], fill=MUTED + (255,))
    d.line([(104, 110), (128, 160), (152, 110)], fill=(24, 30, 44, 255), width=12, joint="curve")


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    make_splash()
    make_icon(body_app, "winblender.ico")
    make_icon(body_file, "winblenderfile.ico")
    print("PLACEHOLDERS OK — swap with final art later, same filenames.")


if __name__ == "__main__":
    main()

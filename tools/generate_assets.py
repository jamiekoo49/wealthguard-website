#!/usr/bin/env python3
"""
Generate derived brand assets from the processed logo:
  - favicon.ico            (multi-size: 16/32/48)
  - apple-touch-icon.png   (180x180, navy background)
  - expert-placeholder.jpg (portrait placeholder for the "Our Expert" section)

Run from the repo root:
    python tools/generate_assets.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(ROOT, "assets", "img", "logo.png")
IMG_DIR = os.path.join(ROOT, "assets", "img")

NAVY = (11, 42, 74)
NAVY_2 = (18, 54, 92)
SILVER = (201, 206, 214)
GOLD = (198, 150, 43)


def make_favicon():
    logo = Image.open(LOGO).convert("RGBA")
    # square canvas so the icon isn't distorted
    side = max(logo.size)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(logo, ((side - logo.width) // 2, (side - logo.height) // 2), logo)
    square.save(os.path.join(ROOT, "favicon.ico"),
                sizes=[(16, 16), (32, 32), (48, 48)])
    print("wrote favicon.ico")

    # Apple touch icon: icon on a navy rounded field.
    apple = Image.new("RGBA", (180, 180), NAVY + (255,))
    icon = square.resize((132, 132), Image.LANCZOS)
    apple.paste(icon, (24, 24), icon)
    apple.convert("RGB").save(os.path.join(IMG_DIR, "apple-touch-icon.png"))
    print("wrote apple-touch-icon.png")


def make_expert_placeholder(size=800):
    # Matches the design's placeholder: a square card of cream diagonal stripes
    # with a muted monospace caption. Overwrite this file with the real portrait.
    LIGHT = (238, 232, 219)   # #eee8db
    DARK = (231, 224, 209)    # #e7e0d1
    CAPTION = (154, 162, 172)  # #9aa2ac

    img = Image.new("RGB", (size, size), LIGHT)
    draw = ImageDraw.Draw(img)

    # 135deg repeating stripes, ~22px period (11px band each) as in the design.
    band = 22
    for d in range(-size, size * 2, band):
        # diagonal band: draw a thick line from top-left to bottom-right offset
        draw.line([(d, 0), (d + size, size)], fill=DARK, width=11)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    text = "[ principal consultant photo ]"
    tb = draw.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    # place the caption on a small clean plate so it stays legible over stripes
    cx, cy = size // 2, size // 2
    pad = 16
    draw.rectangle([cx - tw // 2 - pad, cy - th // 2 - pad,
                    cx + tw // 2 + pad, cy + th // 2 + pad], fill=LIGHT)
    draw.text((cx - tw // 2, cy - th // 2 - tb[1]), text, fill=CAPTION, font=font)

    img.save(os.path.join(IMG_DIR, "expert-placeholder.jpg"), quality=90)
    print("wrote expert-placeholder.jpg")


if __name__ == "__main__":
    make_favicon()
    make_expert_placeholder()

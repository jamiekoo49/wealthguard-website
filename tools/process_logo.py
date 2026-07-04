#!/usr/bin/env python3
"""
Process the WealthGuard logo:
  1. Crop off the company-name text at the bottom, keeping only the tower/gear icon.
  2. Remove the (near-white) background by flood-removing only the border-connected
     background region -- this preserves the light silver highlights *inside* the tower.
  3. Auto-crop to the icon's bounding box with a small transparent margin.

Output: assets/img/logo.png  (transparent PNG, icon only)

Usage:
    python process_logo.py INPUT.png OUTPUT.png
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

# --- Tunable parameters -------------------------------------------------------
TEXT_CROP_Y   = 455   # keep rows [0:TEXT_CROP_Y]; everything below is the name text
BG_COLOR      = (249, 249, 249)  # sampled from the image corners
BG_TOLERANCE  = 22    # a pixel counts as "background" if every channel is within this of BG_COLOR
MARGIN        = 12    # transparent px padding kept around the icon after autocrop
# -----------------------------------------------------------------------------


def process(in_path: str, out_path: str) -> None:
    img = Image.open(in_path).convert("RGBA")
    arr = np.array(img)

    # 1) Crop off the bottom text band.
    arr = arr[:TEXT_CROP_Y, :, :]

    rgb = arr[:, :, :3].astype(np.int16)

    # 2) Mask of "background-like" pixels (near the sampled corner colour).
    diff = np.abs(rgb - np.array(BG_COLOR, dtype=np.int16))
    bg_like = np.all(diff <= BG_TOLERANCE, axis=2)

    # Keep only background-like pixels connected to the image border, so that any
    # near-white highlights trapped *inside* the tower are NOT deleted.
    labels, n = ndimage.label(bg_like)
    border_labels = set(labels[0, :]) | set(labels[-1, :]) \
        | set(labels[:, 0]) | set(labels[:, -1])
    border_labels.discard(0)
    outside = np.isin(labels, list(border_labels))

    # 3) Make the outside background fully transparent.
    alpha = arr[:, :, 3].copy()
    alpha[outside] = 0
    arr[:, :, 3] = alpha

    # 4) Soften a 1px white halo: for kept pixels adjacent to transparency that are
    #    still very light, scale their alpha down a touch based on whiteness.
    transparent = arr[:, :, 3] == 0
    neighbour_transparent = ndimage.binary_dilation(transparent) & ~transparent
    lightness = rgb.mean(axis=2)
    halo = neighbour_transparent & (lightness > 232)
    fade = np.clip((255 - (lightness - 232) * (255 / 23)), 0, 255).astype(np.uint8)
    arr[:, :, 3] = np.where(halo, np.minimum(arr[:, :, 3], fade), arr[:, :, 3])

    # 5) Auto-crop to the bounding box of visible (non-transparent) pixels.
    visible = arr[:, :, 3] > 0
    ys, xs = np.where(visible)
    y0, y1 = ys.min(), ys.max() + 1
    x0, x1 = xs.min(), xs.max() + 1
    y0 = max(0, y0 - MARGIN); x0 = max(0, x0 - MARGIN)
    y1 = min(arr.shape[0], y1 + MARGIN); x1 = min(arr.shape[1], x1 + MARGIN)
    cropped = arr[y0:y1, x0:x1, :]

    out = Image.fromarray(cropped, "RGBA")
    out.save(out_path)
    print(f"Saved {out_path}  ({out.width}x{out.height}, transparent PNG)")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "wealthguard-logo.png"
    dst = sys.argv[2] if len(sys.argv) > 2 else "logo.png"
    process(src, dst)

#!/usr/bin/env python3
"""
clean_slide.py — Post-process a Gemini-generated slide image.

What it does:
  1. Overlays the real NR logo over the bottom-right corner (covers Gemini star watermark)
  2. Adds the exact NR disclaimer text at bottom-left
  3. Saves a clean version ready for the final deck

Usage:
  python3 clean_slide.py <input_image> [output_image]

Examples:
  python3 clean_slide.py ingestion_ai/Updated/slide_01.png
  python3 clean_slide.py ingestion_ai/Updated/slide_01.png ingestion_ai/Final/slide_01.png
"""

import sys, os
from PIL import Image, ImageDraw, ImageFont

DIR      = os.path.dirname(os.path.abspath(__file__))
NR_LOGO  = os.path.join(DIR, "nr_logo_2.png")
DISCLAIMER = "© 2025 New Relic, Inc. All rights reserved. Confidential and proprietary. For internal use only, not for external distribution."


def find_font(size):
    """Try to find a system font, fall back to default."""
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNSText.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def clean(input_path, output_path=None):
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = base + "_clean" + ext

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    # ── 1. Wipe bottom-right corner + bottom strip (Gemini star sits above NR logo)
    import numpy as np
    # Sample background colour from a safe dark area mid-right
    sample = img.crop((w - 400, h - 400, w - 200, h - 300))
    arr = np.array(sample)
    bg_r = int(np.median(arr[:, :, 0]))
    bg_g = int(np.median(arr[:, :, 1]))
    bg_b = int(np.median(arr[:, :, 2]))
    bg_color = (bg_r, bg_g, bg_b, 255)

    # Wipe bottom 20% of right 30% (covers both watermark + NR logo area)
    right_x = int(w * 0.72)
    top_y   = int(h * 0.80)
    draw.rectangle([right_x, top_y, w, h], fill=bg_color)
    # Also wipe full bottom strip for disclaimer
    draw.rectangle([0, h - int(h * 0.06), w, h], fill=bg_color)

    # ── 3. Place real NR logo bottom-right ───────────────────────────────────
    if os.path.exists(NR_LOGO):
        logo = Image.open(NR_LOGO).convert("RGBA")
        # Target width ~180px, maintain aspect ratio
        logo_w = 180
        logo_h = int(logo.size[1] * logo_w / logo.size[0])
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
        margin = 18
        logo_x = w - logo_w - margin
        logo_y = h - logo_h - margin
        img.paste(logo, (logo_x, logo_y), logo)

    # ── 4. Write exact NR disclaimer bottom-left ──────────────────────────────
    font_size = max(12, int(h * 0.012))
    font = find_font(font_size)
    disc_color = (120, 120, 120, 255)
    draw.text((18, h - 28), DISCLAIMER, font=font, fill=disc_color)

    # ── 5. Save ───────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.convert("RGB").save(output_path, "PNG", optimize=False)
    print(f"✓  Cleaned → {output_path}  ({w}×{h})")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    clean(inp, out)

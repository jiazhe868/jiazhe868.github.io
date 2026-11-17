#!/usr/bin/env python3
"""Convert figures to web-sized WebP files.

    python tools/prepare_images.py SRC.png assets/img/quakes/name.webp
    python tools/prepare_images.py SRC.png DEST.webp --width 1400 --quality 85

Images wider than --width are downscaled. Transparent images are flattened onto
white, because most scientific figures assume a white page.
"""

import argparse
from pathlib import Path

from PIL import Image


def convert(src, dest, width=1800, quality=88, crop=None):
    im = Image.open(src)
    if crop:
        im = im.crop(crop)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "WEBP", quality=quality, method=6)
    return im.size, dest.stat().st_size


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("dest")
    ap.add_argument("--width", type=int, default=1800)
    ap.add_argument("--quality", type=int, default=88)
    args = ap.parse_args()
    size, nbytes = convert(args.src, args.dest, args.width, args.quality)
    print(f"{args.dest}: {size[0]}x{size[1]}, {nbytes / 1024:.0f} KB")

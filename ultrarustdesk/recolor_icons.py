"""Recolor the RustDesk blue/cyan icons to UltraRustDesk green.

Run from the repository root with a Python that has Pillow and numpy:

    python ultrarustdesk/recolor_icons.py

The transform rotates blue and cyan hues toward green and slightly darkens
saturated pixels, so white, gray and black parts of an icon stay unchanged.
Running it twice would shift the colors again, so run it only on the original
blue icons (for example after merging upstream icon changes).
"""

import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HUE_SHIFT = -75.0  # degrees: #0071ff -> #00cc47, #00bfe1 -> #12b400
VALUE_SCALE = 0.8  # applied in full to fully saturated pixels only
HUE_FULL = (175.0, 250.0)  # hues shifted in full
HUE_FADE = 15.0  # degrees outside HUE_FULL over which the shift fades out

RASTER_FILES = [
    "res/128x128.png",
    "res/128x128@2x.png",
    "res/32x32.png",
    "res/64x64.png",
    "res/icon.png",
    "res/mac-icon.png",
    "res/mac-tray-dark-x2.png",
    "res/mac-tray-light-x2.png",
    "fastlane/metadata/android/en-US/images/icon.png",
]
RASTER_GLOBS = [
    "flutter/android/app/src/main/res/mipmap-*/ic_launcher*.png",
    "flutter/ios/Runner/Assets.xcassets/AppIcon.appiconset/*.png",
]
ICO_FILES = [
    "res/icon.ico",
    "res/tray-icon.ico",
    "flutter/windows/runner/resources/app_icon.ico",
]
ICNS_FILES = ["flutter/macos/Runner/AppIcon.icns"]
SVG_FILES = [
    "res/design.svg",
    "res/logo-header.svg",
    "res/logo.svg",
    "res/rustdesk-banner.svg",
    "res/scalable.svg",
    "flutter/assets/icon.svg",
]


def recolor_array(rgb: np.ndarray) -> np.ndarray:
    """Recolor an (..., 3) float array of RGB values in 0..1."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = rgb.max(axis=-1)
    minc = rgb.min(axis=-1)
    delta = maxc - minc
    v = maxc
    s = np.where(maxc > 0, delta / np.where(maxc > 0, maxc, 1), 0)
    safe = np.where(delta > 0, delta, 1)
    h = np.where(
        maxc == r,
        ((g - b) / safe) % 6,
        np.where(maxc == g, (b - r) / safe + 2, (r - g) / safe + 4),
    )
    h = np.where(delta > 0, h * 60.0, 0.0)

    lo, hi = HUE_FULL
    weight = np.clip(
        np.minimum(h - (lo - HUE_FADE), (hi + HUE_FADE) - h) / HUE_FADE, 0, 1
    )
    weight = np.where(delta > 0, weight, 0)

    h2 = (h + HUE_SHIFT * weight) % 360
    v2 = v * (1 - (1 - VALUE_SCALE) * s * weight)

    c = v2 * s
    hp = h2 / 60.0
    x = c * (1 - np.abs(hp % 2 - 1))
    m = v2 - c
    zeros = np.zeros_like(c)
    sector = np.floor(hp).astype(int) % 6
    choices = [
        np.stack([c, x, zeros], -1),
        np.stack([x, c, zeros], -1),
        np.stack([zeros, c, x], -1),
        np.stack([zeros, x, c], -1),
        np.stack([x, zeros, c], -1),
        np.stack([c, zeros, x], -1),
    ]
    out = np.zeros_like(rgb)
    for i, choice in enumerate(choices):
        out = np.where((sector == i)[..., None], choice, out)
    return out + m[..., None]


def recolor_image(im: Image.Image) -> Image.Image:
    rgba = np.asarray(im.convert("RGBA")).astype(np.float64) / 255.0
    rgba[..., :3] = recolor_array(rgba[..., :3])
    out = Image.fromarray(np.round(rgba * 255).clip(0, 255).astype(np.uint8), "RGBA")
    if im.mode == "RGB":
        return out.convert("RGB")
    return out


def recolor_hex(match: re.Match) -> str:
    text = match.group(0)
    rgb = np.array([[int(text[i : i + 2], 16) for i in (1, 3, 5)]], float) / 255.0
    r, g, b = np.round(recolor_array(rgb)[0] * 255).astype(int)
    out = f"#{r:02x}{g:02x}{b:02x}"
    return out.upper() if text[1:].isupper() else out


def recolor_raster(path: Path) -> None:
    with Image.open(path) as im:
        im.load()
        out = recolor_image(im)
    out.save(path, optimize=True)


def recolor_ico(path: Path) -> None:
    # Keep the original entry encoding: some readers (the tray icon decoder) expect BMP.
    bitmap_format = "png" if b"\x89PNG" in path.read_bytes() else "bmp"
    with Image.open(path) as im:
        sizes = sorted(im.ico.sizes(), key=lambda s: s[0] * s[1], reverse=True)
        frames = [recolor_image(im.ico.getimage(size)) for size in sizes]
    frames[0].save(
        path,
        format="ICO",
        sizes=sizes,
        append_images=frames[1:],
        bitmap_format=bitmap_format,
    )


def recolor_icns(path: Path) -> None:
    with Image.open(path) as im:
        im.load()
        out = recolor_image(im)
    out.save(path, format="ICNS")


def recolor_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    new = re.sub(r"#[0-9a-fA-F]{6}\b", recolor_hex, text)
    path.write_text(new, encoding="utf-8", newline="")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    rasters = [root / p for p in RASTER_FILES]
    for pattern in RASTER_GLOBS:
        rasters.extend(sorted(root.glob(pattern)))
    jobs = (
        [(recolor_raster, p) for p in rasters]
        + [(recolor_ico, root / p) for p in ICO_FILES]
        + [(recolor_icns, root / p) for p in ICNS_FILES]
        + [(recolor_svg, root / p) for p in SVG_FILES]
    )
    for func, path in jobs:
        if not path.is_file():
            print(f"missing: {path.relative_to(root)}", file=sys.stderr)
            return 1
        func(path)
        print(f"recolored {path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

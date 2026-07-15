#!/usr/bin/env python3
"""Isolate the figure from each flat illustration.

These are flat vector illustrations with dark outline strokes and only two
background tones: a near-white canvas and one light periwinkle blob. That makes
a deterministic keyer more reliable than a photo-trained segmentation net:

  1. background-like = light AND low-saturation pixels
  2. flood from the image border through those pixels -> the EXTERIOR only
     (interior light regions such as a white tank top or a face stay, because
     the illustration's outline strokes seal them off from the border)
  3. drop decorative plants/pots by keeping connected components that reach the
     central vertical band; the figure (and anything it holds / stands on) does
  4. de-fringe: erode 1px, feather, so edges read as an intentional cutout

Writes render/cutouts/<name>.png (RGBA) for assets 01-11.
"""
import os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(HERE, "cutouts")
os.makedirs(OUT, exist_ok=True)

NAMES = [
    "01-meditation-and-breathing", "02-self-compassion",
    "03-reflection-and-journaling", "04-gentle-stretch",
    "05-balance-and-mindfulness", "06-rest-and-recovery",
    "07-movement-and-mood", "08-daily-routine", "09-active-wellness",
    "10-focus-and-drive", "11-playful-confidence",
]


def cutout(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    H, W = a.shape[:2]
    mx = a.max(2)
    mn = a.min(2)
    L = mx / 255.0
    S = (mx - mn) / (mx + 1e-6)

    # "background-ish" = pale and only lightly inked. The near-white canvas and
    # the light periwinkle blob both qualify; the figure's dark outlines, navy
    # fills and saturated plant greens do not. Interior pale areas (white tank,
    # face, skin) are sealed off by the illustration's outlines, so a border
    # flood never reaches them.
    bg_like = (L > 0.78) & (S < 0.34)

    pad = np.pad(bg_like, 1, constant_values=True)
    lab, _ = ndimage.label(pad)
    exterior = (lab == lab[0, 0])[1:-1, 1:-1]
    fg = ndimage.binary_fill_holes(~exterior)

    if not fg.any():
        return Image.fromarray(
            np.dstack([a.astype(np.uint8), np.zeros((H, W), np.uint8)]), "RGBA")

    # Sever thin ground/shadow bridges that link the figure to decorative
    # plants in the seated poses: open the mask (erode->pick largest->dilate
    # back within fg) so the bulky figure survives while thin necks to the
    # plants are cut, then keep only the figure's mass.
    k = 9
    core = ndimage.binary_erosion(fg, iterations=k)
    lab, n = ndimage.label(core)
    if n:
        sizes = np.array([(lab == i).sum() for i in range(1, n + 1)])
        core = lab == (int(sizes.argmax()) + 1)
        # regrow the eroded figure to its real edges WITHOUT crossing the cut
        # bridge (dilate from the figure core only, then snap to fg)
        keep = ndimage.binary_dilation(core, iterations=k + 2) & fg
    else:
        lab, n = ndimage.label(fg)
        sizes = np.array([(lab == i).sum() for i in range(1, n + 1)])
        keep = lab == (int(sizes.argmax()) + 1)

    # trim wide ground-plane residue (a seated figure's mat, a plant/pot on the
    # same floor line) by clipping the bottom band to the body's column span.
    rows = np.where(keep.any(1))[0]
    if rows.size:
        py0, py1 = rows.min(), rows.max()
        h = py1 - py0
        band = keep[py0 + int(0.18 * h): py0 + int(0.62 * h)]
        cols = np.where(band.any(0))[0]
        if cols.size:
            margin = int(0.10 * W)
            bx0, bx1 = max(cols.min() - margin, 0), min(cols.max() + margin, W)
            floor = py0 + int(0.74 * h)
            keep[floor:, :bx0] = False
            keep[floor:, bx1:] = False

    fg = ndimage.binary_erosion(keep, iterations=1)
    alpha = (fg * 255).astype(np.uint8)
    alpha = np.asarray(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1.2)))
    return Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), "RGBA")


def main():
    def onbg(im):
        # neutral checkerboard, purely to inspect alpha edges
        t = 24
        base = np.zeros((im.size[1], im.size[0], 3), np.uint8)
        yy, xx = np.mgrid[0:im.size[1], 0:im.size[0]]
        chk = (((xx // t) + (yy // t)) % 2).astype(bool)
        base[chk] = 210
        base[~chk] = 235
        bg = Image.fromarray(base, "RGB").convert("RGBA")
        return Image.alpha_composite(bg, im).convert("RGB")

    tiles = []
    for nm in NAMES:
        out = cutout(os.path.join(ASSETS, nm + ".png"))
        out.save(os.path.join(OUT, nm + ".png"))
        al = np.asarray(out)[:, :, 3]
        bb = out.getbbox()
        wh = (bb[2] - bb[0], bb[3] - bb[1]) if bb else (0, 0)
        print(f"{nm[:24]:24} cov={100*(al>20).mean():4.1f}% wh={wh}")
        tiles.append(onbg(out).resize((260, 195)))
    grid = Image.new("RGB", (260 * 3, 195 * 4), "white")
    for i, t in enumerate(tiles):
        grid.paste(t, ((i % 3) * 260, (i // 3) * 195))
    grid.save(os.path.join(OUT, "_all_key.png"))
    print("contact sheet:", os.path.join(OUT, "_all_key.png"))


if __name__ == "__main__":
    main()

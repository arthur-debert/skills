#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pillow"]
# ///
"""Print the dark-pixel runs along one row or column of a raster drawing.

Each run is a drawn line crossing the scan, so the gaps between runs give
feature positions to about one pixel. Convert pixels to millimetres with a
given dimension measured the same way.

    figure_runs.py fig.png --row 480              runs along pixel row 480
    figure_runs.py fig.png --col 560 --from 200 --to 900
    figure_runs.py fig.png --row 480 --crop 150,200,970,950   x0,y0,x1,y1 first
    figure_runs.py fig.png --rows 400:600:10 --first 2   trace a sloped edge
"""
import argparse

import numpy as np
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--row", type=int)
    g.add_argument("--col", type=int)
    g.add_argument("--rows", help="start:stop:step; prints the first runs of each row")
    ap.add_argument("--first", type=int, default=2, help="runs per row with --rows")
    ap.add_argument("--from", dest="start", type=int, default=0)
    ap.add_argument("--to", dest="end", type=int)
    ap.add_argument("--crop", help="x0,y0,x1,y1 in pixels, applied first")
    ap.add_argument("--threshold", type=int, default=128, help="grey level counted as ink")
    a = ap.parse_args()
    img = np.asarray(Image.open(a.png).convert("L"))
    if a.crop:
        x0, y0, x1, y1 = (int(v) for v in a.crop.split(","))
        img = img[y0:y1, x0:x1]
    if a.rows:
        r0, r1, step = (int(v) for v in a.rows.split(":"))
        for r in range(r0, r1, step):
            found = runs_of(img[r, a.start:a.end] < a.threshold, a.start)[:a.first]
            print(r, "  ".join(f"{(x0 + x1) / 2:.1f}" for x0, x1 in found))
        return
    line = img[a.row, :] if a.row is not None else img[:, a.col]
    runs = runs_of(line[a.start:a.end] < a.threshold, a.start)
    prev = None
    for r0, r1 in runs:
        centre = (r0 + r1) / 2
        gap = "" if prev is None else f"  gap {centre - prev:.1f}"
        print(f"{r0}-{r1}  centre {centre:.1f}{gap}")
        prev = centre


def runs_of(ink, offset):
    runs, i = [], 0
    while i < len(ink):
        if ink[i]:
            j = i
            while j < len(ink) and ink[j]:
                j += 1
            runs.append((offset + i, offset + j - 1))
            i = j
        else:
            i += 1
    return runs


if __name__ == "__main__":
    main()

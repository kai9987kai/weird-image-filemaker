#!/usr/bin/env python3
import argparse
import os
import random

from PIL import Image

import image_mutator_local as mut


# Stable curated set: same filenames every run, intentionally varied edge paths.
BEST20 = [
    ("01_png_apng_invisible_firstframe.png", mut.png_apng_invisible_firstframe, "png", 1001),
    ("02_png_apng_tiny_burst.png", mut.png_apng_tiny_burst, "png", 1002),
    ("03_png_palette_fulltrns_interlaced.png", mut.png_palette_fulltrns_interlaced, "png", 1003),
    ("04_png_la_moire.png", mut.png_la_moire, "png", 1004),
    ("05_png_huge_dims_tiny_content.png", mut.png_huge_dims_tiny_content, "png", 1005),
    ("06_png_gray16_gradient_strip.png", mut.png_gray16_gradient_strip, "png", 1006),
    ("07_png_colorkey_meta_heavy.png", mut.png_colorkey_meta, "png", 1007),
    ("08_png_apng_invisible_firstframe_alt.png", mut.png_apng_invisible_firstframe, "png", 1008),
    ("09_png_apng_tiny_burst_alt.png", mut.png_apng_tiny_burst, "png", 1009),
    ("10_png_palette_fulltrns_interlaced_alt.png", mut.png_palette_fulltrns_interlaced, "png", 1010),
    ("11_jpg_exif_comment_heavy.jpg", mut.jpg_exif_orient_comment_heavy, "jpg", 2001),
    ("12_jpg_prog_gray_odd.jpg", mut.jpg_progressive_grayscale_odd, "jpg", 2002),
    ("13_jpg_cmyk_prog_odd_aspect.jpg", mut.jpg_cmyk_progressive_odd_aspect, "jpg", 2003),
    ("14_jpg_prog_444_exif_comment.jpg", mut.jpg_progressive_444_exif_comment, "jpg", 2004),
    ("15_jpg_base_444_odd.jpg", mut.jpg_baseline_444_odd, "jpg", 2005),
    ("16_jpg_exif_comment_heavy_alt.jpg", mut.jpg_exif_orient_comment_heavy, "jpg", 2006),
    ("17_jpg_prog_gray_odd_alt.jpg", mut.jpg_progressive_grayscale_odd, "jpg", 2007),
    ("18_jpg_cmyk_prog_odd_aspect_alt.jpg", mut.jpg_cmyk_progressive_odd_aspect, "jpg", 2008),
    ("19_png_la_moire_alt.png", mut.png_la_moire, "png", 1011),
    ("20_png_colorkey_meta_heavy_alt.png", mut.png_colorkey_meta, "png", 1012),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Seed image path used for derived variants")
    ap.add_argument("--out", default="./best_20_weird", help="Output directory")
    ap.add_argument("--seed-offset", type=int, default=0, help="Optional offset applied to per-file seeds")
    args = ap.parse_args()

    mut.ensure_dir(args.out)
    img = Image.open(args.input)

    ok = 0
    err = 0
    for fname, fn, _ext, seed in BEST20:
        outp = os.path.join(args.out, fname)
        rng = random.Random(seed + args.seed_offset)
        try:
            fn(img, outp, rng)
            print("OK ", outp)
            ok += 1
        except Exception as e:
            print("ERR", outp, e)
            err += 1

    print(f"Done: {ok} ok, {err} err")


if __name__ == "__main__":
    main()

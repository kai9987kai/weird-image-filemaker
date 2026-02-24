#!/usr/bin/env python3
import argparse
import os
import random

from PIL import Image

import image_mutator_local as mut


BEST24 = [
    ("01_png_apng_invisible_firstframe.png", mut.png_apng_invisible_firstframe, 3001),
    ("02_png_apng_tiny_burst.png", mut.png_apng_tiny_burst, 3002),
    ("03_png_apng_odd_canvas_stutter.png", mut.png_apng_odd_canvas_stutter, 3003),
    ("04_png_apng_alpha_blocks_irregular.png", mut.png_apng_alpha_blocks_irregular, 3004),
    ("05_png_palette_fulltrns_interlaced.png", mut.png_palette_fulltrns_interlaced, 3005),
    ("06_png_palette_lowbit_trns.png", mut.png_palette_lowbit_trns, 3006),
    ("07_png_colorkey_meta_heavy.png", mut.png_colorkey_meta, 3007),
    ("08_png_colorkey_meta_itxt_heavy.png", mut.png_colorkey_meta_itxt_heavy, 3008),
    ("09_png_extreme_aspect_line.png", mut.png_extreme_aspect_line, 3009),
    ("10_png_huge_dims_tiny_content.png", mut.png_huge_dims_tiny_content, 3010),
    ("11_png_gray16_gradient_strip.png", mut.png_gray16_gradient_strip, 3011),
    ("12_png_la_moire.png", mut.png_la_moire, 3012),
    ("13_jpg_exif_comment_heavy.jpg", mut.jpg_exif_orient_comment_heavy, 4001),
    ("14_jpg_exif_mirror_orient_comment.jpg", mut.jpg_exif_mirror_orient_comment, 4002),
    ("15_jpg_prog_gray_odd.jpg", mut.jpg_progressive_grayscale_odd, 4003),
    ("16_jpg_prog_gray_prime_comment.jpg", mut.jpg_prog_gray_prime_comment, 4004),
    ("17_jpg_cmyk_prog_odd_aspect.jpg", mut.jpg_cmyk_progressive_odd_aspect, 4005),
    ("18_jpg_cmyk_base_odd_aspect.jpg", mut.jpg_cmyk_baseline_odd_aspect, 4006),
    ("19_jpg_prog_444_exif_comment.jpg", mut.jpg_progressive_444_exif_comment, 4007),
    ("20_jpg_prog_444_highq_odd.jpg", mut.jpg_prog_444_highq_odd, 4008),
    ("21_jpg_base_444_odd.jpg", mut.jpg_baseline_444_odd, 4009),
    ("22_png_apng_tiny_burst_alt.png", mut.png_apng_tiny_burst, 3013),
    ("23_png_colorkey_meta_itxt_heavy_alt.png", mut.png_colorkey_meta_itxt_heavy, 3014),
    ("24_jpg_prog_gray_prime_comment_alt.jpg", mut.jpg_prog_gray_prime_comment, 4010),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Seed image path used for derived variants")
    ap.add_argument("--out", default="./best_24_weirder", help="Output directory")
    ap.add_argument("--seed-offset", type=int, default=0, help="Optional offset applied to per-file seeds")
    args = ap.parse_args()

    mut.ensure_dir(args.out)
    img = Image.open(args.input)

    ok = 0
    err = 0
    for fname, fn, seed in BEST24:
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

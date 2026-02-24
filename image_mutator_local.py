#!/usr/bin/env python3
import argparse
import math
import os
import random

import numpy as np
from PIL import Image, PngImagePlugin


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def rng_choice(rng, items):
    return items[rng.randrange(len(items))]


def exif_orient(img, outp, rng):
    ex = Image.Exif()
    ex[0x0112] = rng_choice(rng, [2, 3, 4, 5, 6, 7, 8])
    ex[0x010E] = "local test " + ("X" * rng.randint(100, 1200))
    img.convert("RGB").save(
        outp, "JPEG", quality=rng.randint(82, 96), exif=ex, optimize=True
    )


def prog_gray(img, outp, rng):
    g = img.convert("L")
    w, h = g.size
    g = g.resize((max(17, w | 1), max(17, h | 1)))
    g.save(
        outp, "JPEG", progressive=True, quality=rng.randint(85, 97), optimize=True
    )


def cmyk_prog(img, outp, rng):
    img.convert("RGB").convert("CMYK").save(
        outp, "JPEG", progressive=True, quality=rng.randint(85, 97), optimize=True
    )


def png_palette_trns(img, outp, rng):
    q = img.convert("RGBA").convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
    q.info["transparency"] = bytes([(i * rng.randint(3, 17)) % 256 for i in range(256)])
    q.save(outp, "PNG", interlace=1, optimize=False)


def png_colorkey_meta(img, outp, rng):
    rgb = img.convert("RGB")
    arr = np.array(rgb)
    h, w = arr.shape[:2]
    yy, xx = np.indices((h, w))
    arr[(xx * 13 + yy * 17) % rng_choice(rng, [89, 97, 101]) == 0] = [255, 0, 255]
    rgb = Image.fromarray(arr, "RGB")
    rgb.info["transparency"] = (255, 0, 255)
    info = PngImagePlugin.PngInfo()
    for i in range(rng.randint(2, 4)):
        info.add_text(
            f"z{i}", ("META_" * rng.randint(200, 600)) + str(i), zip=True
        )
    rgb.save(
        outp,
        "PNG",
        pnginfo=info,
        dpi=(rng_choice(rng, [72, 96, 300, 1200, 3000]), rng_choice(rng, [1, 72, 96])),
    )


def png_gray16(img, outp, rng):
    del rng
    arr = np.array(img.convert("L"), dtype=np.uint16) * 257
    Image.fromarray(arr, "I;16").save(outp, "PNG")


def apng_preview(img, outp, rng):
    base = img.convert("RGBA").resize((320, 320))
    arr = np.array(base)
    yy, xx = np.indices((320, 320))
    frames = []
    durations = []
    for i in range(rng_choice(rng, [12, 16])):
        a = np.roll(np.roll(arr.copy(), i * 5, axis=1), i * 3, axis=0)
        ring = np.sqrt((xx - 160) ** 2 + (yy - 160) ** 2)
        alpha = np.clip(255 - np.abs(ring - (20 + (i * 7) % 120)) * 4, 0, 255).astype(
            np.uint8
        )
        a[..., 3] = np.maximum(a[..., 3], alpha)
        frames.append(
            Image.fromarray(a, "RGBA")
            .convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
            .convert("RGBA")
        )
        durations.append(rng_choice(rng, [60, 80, 90, 100, 120]))
    frames[0].save(
        outp,
        "PNG",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
    )


def png_apng_invisible_firstframe(img, outp, rng):
    base = img.convert("RGBA").resize((256, 256))
    arr = np.array(base)
    yy, xx = np.indices((256, 256))
    frames = []
    durations = []
    for i in range(rng_choice(rng, [16, 20, 24])):
        a = np.roll(np.roll(arr.copy(), i * 7, axis=1), i * 5, axis=0)
        if i == 0:
            a[..., 3] = 0
            durations.append(350)
        else:
            ring = np.sqrt((xx - 128) ** 2 + (yy - 128) ** 2)
            alpha = np.clip(255 - ring * (1.8 + (i % 3) * 0.2), 0, 255).astype(np.uint8)
            a[..., 3] = np.maximum(a[..., 3], alpha)
            durations.append(rng_choice(rng, [30, 40, 50, 60]))
        frames.append(
            Image.fromarray(a, "RGBA")
            .convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
            .convert("RGBA")
        )
    frames[0].save(
        outp,
        "PNG",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
    )


def png_apng_tiny_burst(img, outp, rng):
    del img
    w = h = rng_choice(rng, [17, 23, 29, 31])
    yy, xx = np.indices((h, w))
    frames = []
    durations = []
    for i in range(rng_choice(rng, [36, 48, 60])):
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[..., 0] = ((xx * 17 + i * 9) % 256).astype(np.uint8)
        rgba[..., 1] = ((yy * 13 + i * 7) % 256).astype(np.uint8)
        rgba[..., 2] = (((xx ^ yy) + i * 11) % 256).astype(np.uint8)
        rgba[..., 3] = ((((xx + yy + i) % 3) == 0) * 255).astype(np.uint8)
        frames.append(Image.fromarray(rgba, "RGBA"))
        durations.append(20 if i % 5 else 220)
    frames[0].save(
        outp,
        "PNG",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
    )


def png_palette_fulltrns_interlaced(img, outp, rng):
    src = img.convert("RGB").resize((rng_choice(rng, [1024, 1536]), rng_choice(rng, [512, 768])))
    arr = np.array(src)
    yy, xx = np.indices(arr.shape[:2])
    idx = ((arr[..., 0].astype(np.uint16) * 3 + arr[..., 1].astype(np.uint16) * 5 + xx + yy) % 256).astype(np.uint8)
    pal = Image.fromarray(idx, "P")
    palette = []
    for i in range(256):
        palette.extend([(i * 97) % 256, (255 - i), (i * 53) % 256])
    pal.putpalette(palette)
    pal.info["transparency"] = bytes([(i * rng_choice(rng, [7, 11, 19])) % 256 for i in range(256)])
    pal.save(outp, "PNG", interlace=1, optimize=False)


def png_la_moire(img, outp, rng):
    w, h = rng_choice(rng, [(1024, 1024), (1600, 900), (2048, 1024)])
    base = img.convert("L").resize((w, h))
    yy, xx = np.indices((h, w))
    lum = ((np.array(base, dtype=np.uint16) + (((np.sin(xx / 1.7) + np.cos(yy / 2.3)) * 63 + 128) % 256).astype(np.uint16)) % 256).astype(np.uint8)
    xdiv = rng_choice(rng, [1, 2, 3])
    ydiv = rng_choice(rng, [2, 3, 5])
    mod = rng_choice(rng, [5, 7, 9])
    threshold = rng_choice(rng, [2, 3, 4])
    alpha = ((((xx // xdiv) ^ (yy // ydiv)) % mod) < threshold).astype(np.uint8) * 255
    Image.fromarray(np.dstack([lum, alpha]), "LA").save(outp, "PNG")


def png_huge_dims_tiny_content(img, outp, rng):
    mode = rng_choice(rng, ["wide", "tall"])
    if mode == "wide":
        w, h = rng_choice(rng, [(4096, 32), (8192, 32), (8192, 16)])
    else:
        w, h = rng_choice(rng, [(32, 4096), (32, 8192), (16, 8192)])
    canvas = Image.new("RGB", (w, h), (0, 0, 0))
    strip_w = max(1, min(w, w // rng_choice(rng, [16, 32, 64])))
    strip_h = max(1, min(h, h // rng_choice(rng, [2, 4, 8])))
    patch = img.convert("RGB").resize((strip_w, strip_h))
    if mode == "wide":
        y = (h - strip_h) // 2
        canvas.paste(patch, ((w - strip_w) // 2, y))
    else:
        x = (w - strip_w) // 2
        canvas.paste(patch, (x, (h - strip_h) // 2))
    canvas.save(outp, "PNG")


def png_gray16_gradient_strip(img, outp, rng):
    del img
    w, h = rng_choice(rng, [(4096, 256), (8192, 8), (2048, 2048)])
    yy, xx = np.indices((h, w))
    arr = (((xx * 65535) // max(1, w - 1)) ^ ((yy * 257) % 65536)).astype(np.uint16)
    Image.fromarray(arr, "I;16").save(outp, "PNG")


def png_apng_odd_canvas_stutter(img, outp, rng):
    w, h = rng_choice(rng, [(31, 47), (47, 31), (63, 35), (35, 63)])
    base = img.convert("RGBA").resize((w, h))
    arr = np.array(base)
    yy, xx = np.indices((h, w))
    frames = []
    durations = []
    frame_count = rng_choice(rng, [72, 84, 96])
    for i in range(frame_count):
        a = np.roll(np.roll(arr.copy(), (i * 3) % w, axis=1), (i * 2) % h, axis=0)
        checker = ((((xx + yy + i) % rng_choice(rng, [3, 4, 5])) == 0) * 255).astype(np.uint8)
        ring = (
            (
                np.sqrt((xx - (w // 2)) ** 2 + (yy - (h // 2)) ** 2).astype(np.int32)
                + i * rng_choice(rng, [2, 3, 5])
            )
            % rng_choice(rng, [7, 9, 11])
            < 2
        ).astype(np.uint8) * 255
        a[..., 3] = np.maximum(a[..., 3], (checker & ring).astype(np.uint8))
        frames.append(Image.fromarray(a, "RGBA"))
        durations.append(15 if i % 8 else 220)
    frames[0].save(
        outp,
        "PNG",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
    )


def png_apng_alpha_blocks_irregular(img, outp, rng):
    w, h = rng_choice(rng, [(320, 240), (400, 300)])
    base = img.convert("RGBA").resize((w, h))
    arr = np.array(base)
    yy, xx = np.indices((h, w))
    frames = []
    durations = []
    for i in range(rng_choice(rng, [24, 36, 48])):
        a = arr.copy()
        a[..., :3] = np.roll(a[..., :3], i * rng_choice(rng, [3, 5, 7]), axis=1)
        a[..., :3] = np.roll(a[..., :3], i * rng_choice(rng, [2, 4, 6]), axis=0)
        cx = int(w / 2 + (w * 0.22) * math.sin(i / 4.0))
        cy = int(h / 2 + (h * 0.18) * math.cos(i / 5.0))
        rx = 18 + (i % 5) * 7
        ry = 14 + (i % 4) * 6
        box = (np.abs(xx - cx) < rx) & (np.abs(yy - cy) < ry)
        stripes = (((xx // rng_choice(rng, [3, 4, 5])) ^ (yy // rng_choice(rng, [4, 6, 8])) ^ i) & 1) == 0
        alpha = np.where(box | stripes, 255, 0).astype(np.uint8)
        a[..., 3] = np.maximum(a[..., 3], alpha)
        frames.append(
            Image.fromarray(a, "RGBA")
            .convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
            .convert("RGBA")
        )
        durations.append(20 if i % 9 else 260)
    frames[0].save(
        outp,
        "PNG",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
    )


def png_colorkey_meta_itxt_heavy(img, outp, rng):
    rgb = img.convert("RGB").resize(rng_choice(rng, [(1024, 768), (1400, 933), (1600, 1200)]))
    arr = np.array(rgb)
    h, w = arr.shape[:2]
    yy, xx = np.indices((h, w))
    arr[(xx * 13 + yy * 17) % rng_choice(rng, [89, 97, 101, 113]) == 0] = [255, 0, 255]
    rgb = Image.fromarray(arr, "RGB")
    rgb.info["transparency"] = (255, 0, 255)
    info = PngImagePlugin.PngInfo()
    z_blob = "GLITCH_META_BLOCK_" * rng_choice(rng, [300, 600, 900])
    for i in range(rng_choice(rng, [4, 6, 8])):
        info.add_text(f"z{i}", z_blob + str(i), zip=True)
    # Valid iTXt with unicode text frequently trips metadata handling paths.
    for i in range(rng_choice(rng, [2, 3, 4])):
        info.add_itxt(
            f"i{i}",
            ("UNICODE_⚠_" * rng_choice(rng, [40, 80, 120])) + str(i),
            lang="en",
            tkey=f"u{i}",
            zip=bool(i % 2),
        )
    rgb.save(
        outp,
        "PNG",
        pnginfo=info,
        dpi=(rng_choice(rng, [1, 72, 300, 655, 3000]), rng_choice(rng, [1, 72, 96, 1000])),
        optimize=False,
    )


def png_extreme_aspect_line(img, outp, rng):
    del img
    mode = rng_choice(rng, ["tall", "wide"])
    if mode == "tall":
        w, h = rng_choice(rng, [(1, 65535), (3, 32767), (7, 16384)])
    else:
        w, h = rng_choice(rng, [(65535, 1), (32767, 3), (16384, 7)])
    yy, xx = np.indices((h, w))
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rgb[..., 0] = ((xx * 37 + yy * 11) % 256).astype(np.uint8)
    rgb[..., 1] = ((yy * 97 + xx * 3) % 256).astype(np.uint8)
    rgb[..., 2] = (((xx ^ yy) * 13) % 256).astype(np.uint8)
    Image.fromarray(rgb, "RGB").save(outp, "PNG")


def png_palette_lowbit_trns(img, outp, rng):
    src = img.convert("L").resize(rng_choice(rng, [(1024, 1024), (1536, 512), (768, 768)]))
    arr = np.array(src)
    # Force 4 indices -> often saved as low-bit palette by encoders.
    idx = ((arr // 64) % 4).astype(np.uint8)
    pal = Image.fromarray(idx, "P")
    palette = [
        0,
        0,
        0,
        255,
        0,
        255,
        0,
        255,
        255,
        255,
        255,
        0,
    ] + [0, 0, 0] * (256 - 4)
    pal.putpalette(palette)
    pal.info["transparency"] = bytes([0, 80, 180, 255])
    pal.save(outp, "PNG", interlace=rng_choice(rng, [0, 1]), optimize=False)


def jpg_exif_orient_comment_heavy(img, outp, rng):
    ex = Image.Exif()
    ex[0x0112] = rng_choice(rng, [3, 6, 8])
    ex[0x010E] = "thumbnail edge case " + ("A" * rng.randint(600, 2400))
    rgb = img.convert("RGB").resize((rng_choice(rng, [1400, 1600, 1800]), rng_choice(rng, [900, 1000, 1200])))
    rgb.save(
        outp,
        "JPEG",
        quality=rng.randint(88, 96),
        optimize=True,
        exif=ex,
        comment=(b"COMMENTSEG_" * rng_choice(rng, [20, 40, 80])),
    )


def jpg_progressive_grayscale_odd(img, outp, rng):
    del img
    w, h = rng_choice(rng, [(2201, 1469), (2601, 1733), (3001, 1999)])
    yy, xx = np.indices((h, w))
    g = (((xx * 29) ^ (yy * 31) ^ ((xx * yy) >> 4)) % 256).astype(np.uint8)
    Image.fromarray(g, "L").save(
        outp, "JPEG", quality=rng.randint(90, 96), progressive=True, optimize=True
    )


def jpg_cmyk_progressive_odd_aspect(img, outp, rng):
    rgb = img.convert("RGB").resize(rng_choice(rng, [(1600, 700), (2200, 900), (2049, 341), (3073, 513)]))
    rgb.convert("CMYK").save(
        outp, "JPEG", quality=rng.randint(92, 97), progressive=True, optimize=True
    )


def jpg_progressive_444_exif_comment(img, outp, rng):
    w, h = rng_choice(rng, [(1537, 1025), (1800, 1201), (2049, 1365)])
    yy, xx = np.indices((h, w))
    base = np.array(img.convert("RGB").resize((w, h)))
    pattern = np.dstack(
        [
            ((xx * 23 + yy * 11) % 256).astype(np.uint8),
            ((((xx * yy) >> 6) + yy) % 256).astype(np.uint8),
            (((xx // 2) ^ (yy // 3) ^ xx) % 256).astype(np.uint8),
        ]
    )
    rgb = ((base.astype(np.uint16) // 2 + pattern.astype(np.uint16) // 2) % 256).astype(np.uint8)
    ex = Image.Exif()
    ex[0x0112] = rng_choice(rng, [6, 8])
    ex[0x010E] = "render path " + ("A" * rng.randint(400, 1600))
    im = Image.fromarray(rgb, "RGB")
    try:
        im.save(
            outp,
            "JPEG",
            quality=rng.randint(93, 97),
            progressive=True,
            optimize=True,
            subsampling=0,
            exif=ex,
            comment=(b"COMSEG_" * rng_choice(rng, [20, 40, 80])),
        )
    except OSError:
        # Pillow occasionally chokes on some optimize+444+metadata combinations.
        im.resize((max(513, w - 1), max(513, h - 1))).save(
            outp,
            "JPEG",
            quality=92,
            progressive=True,
            optimize=False,
            subsampling=0,
            exif=ex,
            comment=(b"COMSEG_" * 12),
        )


def jpg_baseline_444_odd(img, outp, rng):
    w, h = rng_choice(rng, [(2200, 1400), (2400, 1600), (2048, 2048)])
    arr = np.array(img.convert("RGB").resize((w, h)))
    yy, xx = np.indices((h, w))
    arr[..., 0] = ((arr[..., 0].astype(np.uint16) + ((xx + yy) % 256).astype(np.uint16)) % 256).astype(np.uint8)
    arr[..., 1] = ((arr[..., 1].astype(np.uint16) + ((xx ^ yy) % 256).astype(np.uint16)) % 256).astype(np.uint8)
    im = Image.fromarray(arr, "RGB")
    try:
        im.save(
            outp,
            "JPEG",
            quality=rng.randint(90, 96),
            optimize=True,
            progressive=False,
            subsampling=0,
        )
    except OSError:
        im.resize((max(513, w - 1), max(513, h - 1))).save(
            outp,
            "JPEG",
            quality=90,
            optimize=False,
            progressive=False,
            subsampling=0,
        )


def jpg_cmyk_baseline_odd_aspect(img, outp, rng):
    rgb = img.convert("RGB").resize(
        rng_choice(rng, [(2049, 1025), (3073, 513), (1601, 901), (2201, 701)])
    )
    try:
        rgb.convert("CMYK").save(
            outp,
            "JPEG",
            quality=rng.randint(94, 98),
            progressive=False,
            optimize=True,
        )
    except OSError:
        rgb.resize((max(513, rgb.width - 1), max(257, rgb.height - 1))).convert("CMYK").save(
            outp,
            "JPEG",
            quality=94,
            progressive=False,
            optimize=False,
        )


def jpg_exif_mirror_orient_comment(img, outp, rng):
    ex = Image.Exif()
    ex[0x0112] = rng_choice(rng, [5, 7])
    ex[0x010E] = "mirror-orient edge case " + ("M" * rng.randint(400, 2000))
    rgb = img.convert("RGB").resize(rng_choice(rng, [(1801, 1201), (1600, 1067), (1401, 933)]))
    try:
        rgb.save(
            outp,
            "JPEG",
            quality=rng.randint(90, 96),
            optimize=True,
            progressive=rng_choice(rng, [False, True]),
            exif=ex,
            comment=(b"MIRRORCOM_" * rng_choice(rng, [20, 40, 60])),
        )
    except OSError:
        rgb.save(
            outp,
            "JPEG",
            quality=90,
            optimize=False,
            progressive=False,
            exif=ex,
            comment=(b"MIRRORCOM_" * 10),
        )


def jpg_prog_gray_prime_comment(img, outp, rng):
    del img
    w, h = rng_choice(rng, [(3001, 2003), (4093, 3079), (2609, 1733)])
    yy, xx = np.indices((h, w))
    g = (((xx * 31) ^ (yy * 17) ^ ((xx * yy) >> 3)) % 256).astype(np.uint8)
    Image.fromarray(g, "L").save(
        outp,
        "JPEG",
        quality=rng.randint(92, 97),
        progressive=True,
        optimize=True,
        comment=(b"GRAYCOM_" * rng_choice(rng, [10, 20, 40])),
    )


def jpg_prog_444_highq_odd(img, outp, rng):
    w, h = rng_choice(rng, [(2100, 1337), (2200, 1463), (2401, 1601)])
    yy, xx = np.indices((h, w))
    base = np.array(img.convert("RGB").resize((w, h)))
    base[..., 0] = ((base[..., 0].astype(np.uint16) + ((xx * 7 + yy * 13) % 256).astype(np.uint16)) % 256).astype(np.uint8)
    base[..., 1] = ((base[..., 1].astype(np.uint16) + (((xx ^ yy) * 5) % 256).astype(np.uint16)) % 256).astype(np.uint8)
    base[..., 2] = ((base[..., 2].astype(np.uint16) + (((xx * yy) >> 5) % 256).astype(np.uint16)) % 256).astype(np.uint8)
    ex = Image.Exif()
    ex[0x0112] = rng_choice(rng, [6, 8])
    ex[0x010E] = "prog444-highq " + ("Q" * rng.randint(200, 1000))
    im = Image.fromarray(base, "RGB")
    try:
        im.save(
            outp,
            "JPEG",
            quality=rng.randint(95, 98),
            progressive=True,
            optimize=True,
            subsampling=0,
            exif=ex,
            comment=(b"HQ444_" * rng_choice(rng, [10, 20, 30])),
        )
    except OSError:
        try:
            im.resize((max(513, w - 1), max(513, h - 1))).save(
                outp,
                "JPEG",
                quality=94,
                progressive=True,
                optimize=False,
                subsampling=0,
                exif=ex,
                comment=(b"HQ444_" * 8),
            )
        except OSError:
            # Final fallback: drop subsampling/metadata complexity but keep odd dims/patterns.
            im.resize((max(513, w - 3), max(513, h - 3))).save(
                outp,
                "JPEG",
                quality=92,
                progressive=False,
                optimize=False,
            )


def png_apng_glitch_chaos(img, outp, rng):
    del img
    w, h = rng_choice(rng, [(7, 9), (13, 11), (257, 1)])
    frames = []
    durations = []
    frame_count = rng_choice(rng, [120, 150, 200])
    for i in range(frame_count):
        rgba = np.random.randint(0, 256, (h, w, 4), dtype=np.uint8)
        # Randomly make some frames almost entirely transparent to break simple heuristics
        if i % rng_choice(rng, [7, 11]) == 0:
            rgba[..., 3] = rng_choice(rng, [0, 1, 2])
        frames.append(Image.fromarray(rgba, "RGBA"))
        # Mix extremely quick frames with surprisingly long pauses
        if i % rng_choice(rng, [13, 17]) == 0:
            durations.append(rng_choice(rng, [1000, 5000, 10000]))
        else:
            durations.append(rng_choice(rng, [0, 1, 5, 10]))
    frames[0].save(
        outp,
        "PNG",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=rng_choice(rng, [0, 1, 65535]),
        disposal=rng_choice(rng, [0, 1, 2]),
        blend=rng_choice(rng, [0, 1]),
    )


def png_cve_like_metadata(img, outp, rng):
    rgb = img.convert("RGB").resize(rng_choice(rng, [(64, 64), (128, 128)]))
    info = PngImagePlugin.PngInfo()
    # Massive text chunks (up to several megabytes if compressed efficiently)
    huge_blob = "A" * rng_choice(rng, [100000, 500000, 1000000])
    # Add multiple of these chunks
    for i in range(rng_choice(rng, [3, 5, 10])):
        info.add_text(f"huge_z{i}", huge_blob + str(i), zip=True)
        info.add_itxt(
            f"huge_i{i}",
            "🚨" * rng_choice(rng, [10000, 50000]),
            lang="en",
            tkey=f"u{i}",
            zip=True,
        )
    # Weird transparency array mapping
    rgb.info["transparency"] = bytes([rng.randint(0, 255) for _ in range(256)])
    rgb.save(
        outp,
        "PNG",
        pnginfo=info,
        dpi=(rng_choice(rng, [0, 1, 10000, 4294967295]), rng_choice(rng, [0, 1, 10000, 4294967295])), # Extreme DPIs
        optimize=False,
    )


def jpg_extreme_exif_corruption(img, outp, rng):
    ex = Image.Exif()
    # Orientation 1-8 are standard, >8 is invalid but parsers shouldn't crash
    ex[0x0112] = rng_choice(rng, [9, 10, 65535])
    # Massive exif comment chunk (close to 64k limit for a single JPEG marker)
    max_safe_blob = "X" * 60000 
    ex[0x010E] = max_safe_blob
    
    rgb = img.convert("RGB").resize((rng_choice(rng, [8, 16]), rng_choice(rng, [8, 16])))
    try:
        rgb.save(
            outp,
            "JPEG",
            quality=rng.randint(1, 10), # Terribly low quality
            progressive=rng_choice(rng, [True, False]),
            optimize=False,
            exif=ex,
            # Max out comment segment
            comment=(b"Y" * 60000),
            subsampling=rng_choice(rng, [0, 1, 2]) # Try diff subsamplings
        )
    except OSError:
        rgb.save(
            outp,
            "JPEG",
            quality=10,
            optimize=False,
        )


def jpg_cmyk_extreme_aspect(img, outp, rng):
    del img
    # Dimensions that might break 16-bit int bounds or cause OOM in dumb decoders, 
    # but technically < 65535 which is the max for standard JPEG dimensions.
    mode = rng_choice(rng, ["tall", "wide"])
    if mode == "tall":
        w, h = rng_choice(rng, [(1, 65000), (2, 65535)])
    else:
        w, h = rng_choice(rng, [(65000, 1), (65535, 2)])
        
    # Just blank image to save generation time/memory for the script itself
    blank = Image.new("CMYK", (w, h), (0, 0, 0, 0))
    try:
        blank.save(
            outp,
            "JPEG",
            quality=80,
            progressive=True,
            optimize=False
        )
    except OSError:
        # Fallback if PIL refuses
        blank.resize((min(w, 8192), min(h, 8192))).save(
            outp,
            "JPEG",
            quality=80,
            progressive=False, # Non progressive if progressive fails
            optimize=False
        )


def build_generators(formats, profile):
    gens = []

    if "jpg" in formats:
        classic_jpg = [
            ("jpg_exif_orient", exif_orient, "jpg"),
            ("jpg_prog_gray", prog_gray, "jpg"),
            ("jpg_cmyk_prog", cmyk_prog, "jpg"),
        ]
        weird_jpg = [
            ("jpg_exif_comment_heavy", jpg_exif_orient_comment_heavy, "jpg"),
            ("jpg_prog_gray_odd", jpg_progressive_grayscale_odd, "jpg"),
            ("jpg_cmyk_prog_odd_aspect", jpg_cmyk_progressive_odd_aspect, "jpg"),
            ("jpg_prog_444_exif_comment", jpg_progressive_444_exif_comment, "jpg"),
            ("jpg_base_444_odd", jpg_baseline_444_odd, "jpg"),
        ]
        weirder_jpg = [
            ("jpg_cmyk_base_odd_aspect", jpg_cmyk_baseline_odd_aspect, "jpg"),
            ("jpg_exif_mirror_orient_comment", jpg_exif_mirror_orient_comment, "jpg"),
            ("jpg_prog_gray_prime_comment", jpg_prog_gray_prime_comment, "jpg"),
            ("jpg_prog_444_highq_odd", jpg_prog_444_highq_odd, "jpg"),
        ]
        strangest_jpg = [
            ("jpg_extreme_exif_corruption", jpg_extreme_exif_corruption, "jpg"),
            ("jpg_cmyk_extreme_aspect", jpg_cmyk_extreme_aspect, "jpg"),
        ]
        gens += classic_jpg if profile in {"classic", "mixed"} else []
        gens += weird_jpg if profile in {"weird", "weirder", "strangest", "mixed"} else []
        gens += weirder_jpg if profile in {"weirder", "strangest", "mixed"} else []
        gens += strangest_jpg if profile in {"strangest", "mixed"} else []

    if "png" in formats:
        classic_png = [
            ("png_palette_trns", png_palette_trns, "png"),
            ("png_colorkey_meta", png_colorkey_meta, "png"),
            ("png_gray16", png_gray16, "png"),
            ("png_apng_preview", apng_preview, "png"),
        ]
        weird_png = [
            ("png_apng_invisible_firstframe", png_apng_invisible_firstframe, "png"),
            ("png_apng_tiny_burst", png_apng_tiny_burst, "png"),
            ("png_palette_fulltrns_interlaced", png_palette_fulltrns_interlaced, "png"),
            ("png_la_moire", png_la_moire, "png"),
            ("png_huge_dims_tiny_content", png_huge_dims_tiny_content, "png"),
            ("png_gray16_gradient_strip", png_gray16_gradient_strip, "png"),
            ("png_colorkey_meta_heavy", png_colorkey_meta, "png"),
        ]
        weirder_png = [
            ("png_apng_odd_canvas_stutter", png_apng_odd_canvas_stutter, "png"),
            ("png_apng_alpha_blocks_irregular", png_apng_alpha_blocks_irregular, "png"),
            ("png_colorkey_meta_itxt_heavy", png_colorkey_meta_itxt_heavy, "png"),
            ("png_extreme_aspect_line", png_extreme_aspect_line, "png"),
            ("png_palette_lowbit_trns", png_palette_lowbit_trns, "png"),
        ]
        strangest_png = [
            ("png_apng_glitch_chaos", png_apng_glitch_chaos, "png"),
            ("png_cve_like_metadata", png_cve_like_metadata, "png"),
        ]
        gens += classic_png if profile in {"classic", "mixed"} else []
        gens += weird_png if profile in {"weird", "weirder", "strangest", "mixed"} else []
        gens += weirder_png if profile in {"weirder", "strangest", "mixed"} else []
        gens += strangest_png if profile in {"strangest", "mixed"} else []

    return gens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--formats", nargs="*", default=["png", "jpg"])
    ap.add_argument(
        "--profile",
        choices=["classic", "weird", "weirder", "strangest", "mixed"],
        default="classic",
        help="classic=original set, weird=stronger valid edge cases, weirder=pushes further, strangest=extreme mutations, mixed=all",
    )
    ap.add_argument("--seed", type=int, default=1337)
    args = ap.parse_args()

    ensure_dir(args.out)
    img = Image.open(args.input)
    rng = random.Random(args.seed)

    gens = build_generators(set(args.formats), args.profile)
    if not gens:
        raise SystemExit("No generators selected. Check --formats and --profile.")

    for i in range(args.count):
        name, fn, ext = rng_choice(rng, gens)
        outp = os.path.join(args.out, f"{i:03d}_{name}.{ext}")
        try:
            fn(img, outp, rng)
            print("OK", outp)
        except Exception as e:
            print("ERR", outp, e)


if __name__ == "__main__":
    main()

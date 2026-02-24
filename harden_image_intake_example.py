#!/usr/bin/env python3
import sys, os
from PIL import Image, ImageOps, ImageFile
Image.MAX_IMAGE_PIXELS = 50_000_000
ImageFile.LOAD_TRUNCATED_IMAGES = False
ALLOWED_EXT={".png",".jpg",".jpeg",".webp",".gif"}; MAX_BYTES=20*1024*1024; MAX_DIM=4096
def harden(inp,outp):
    if os.path.splitext(inp.lower())[1] not in ALLOWED_EXT: raise ValueError("bad ext")
    if os.stat(inp).st_size > MAX_BYTES: raise ValueError("too large")
    with Image.open(inp) as im:
        im.load(); im = ImageOps.exif_transpose(im)
        if getattr(im,"is_animated",False): im.seek(0); im = im.convert("RGBA")
        if im.mode == "CMYK": im = im.convert("RGB")
        elif im.mode not in {"RGB","RGBA","L"}: im = im.convert("RGBA" if "A" in im.mode else "RGB")
        if im.width > MAX_DIM or im.height > MAX_DIM: im.thumbnail((MAX_DIM,MAX_DIM), Image.Resampling.LANCZOS)
        clean = Image.new(im.mode, im.size); clean.putdata(list(im.getdata()))
        (clean.save(outp,"PNG",optimize=True) if clean.mode=="RGBA" else clean.save(outp,"JPEG",quality=90,optimize=True))
if __name__=="__main__":
    if len(sys.argv)!=3: print("Usage: python harden_image_intake_example.py input output"); raise SystemExit(2)
    harden(sys.argv[1], sys.argv[2]); print("Wrote", sys.argv[2])

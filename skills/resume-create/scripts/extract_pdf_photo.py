#!/usr/bin/env python3
"""Extract embedded JPEG photos from a PDF (no third-party libraries).

Usage: extract_pdf_photo.py resume.pdf out_dir
Writes photo_1.jpg, photo_2.jpg, ... for every /DCTDecode image and prints their sizes.
Non-JPEG (Flate) images are listed but not extracted.
"""
import re, sys
from pathlib import Path

pdf, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
data = pdf.read_bytes()
n = 0
for m in re.finditer(rb"<<(.{0,800}?)>>\s*stream\r?\n", data, re.S):
    head = m.group(1)
    if b"/Subtype /Image" not in head and b"/Subtype/Image" not in head:
        continue
    w = re.search(rb"/Width (\d+)", head); h = re.search(rb"/Height (\d+)", head)
    size = f"{w.group(1).decode() if w else '?'}x{h.group(1).decode() if h else '?'}"
    ln = re.search(rb"/Length (\d+)", head)
    if b"/DCTDecode" in head and ln:
        n += 1
        p = out / f"photo_{n}.jpg"
        p.write_bytes(data[m.end():m.end() + int(ln.group(1))])
        print(f"{p} {size}")
    else:
        print(f"skipped non-JPEG image {size}")
if n == 0:
    print("no JPEG images found")

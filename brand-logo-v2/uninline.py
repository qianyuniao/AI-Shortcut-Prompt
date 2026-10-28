# -*- coding: utf-8 -*-
"""Recover an editable source copy of the brand sheet.

The published brand-sheet.html embeds every figure as base64, which is great
for viewing but impossible to edit. This strips the data URIs back to relative
paths so the HTML can be edited, then re-run inline_images.py to republish.
"""
import os
import re

BASE = r"D:\02_MyWorkSpace\02_QYN Development Project\09Projects already tested\AI Shortcut Prompt\brand-logo-v2"

# must match the order in which figures appear in the document
ORDER = [
    "./png-transparent/transparency-proof.png",
    "./assets/aishort-logo-horizontal-2048px.png",
    "./assets/aishort-logo-horizontal-dark-2048px.png",
    "./assets/aishort-logo-stacked-1024px.png",
    "./assets/aishort-logo-stacked-dark-1024px.png",
    "./editorial-aishort-1024x1536.png",
    "./assets/legibility-check-16-24-32.png",
    "dist/application-preview.png",
]

src_path = os.path.join(BASE, "brand-sheet.html")
out_path = os.path.join(BASE, "brand-sheet.src.html")

with open(src_path, encoding="utf-8") as fh:
    html = fh.read()

pending = iter(ORDER)


def repl(m):
    return 'src="%s"' % next(pending)


html = re.sub(r'src="data:image/[^"]+"', repl, html)
with open(out_path, "w", encoding="utf-8") as fh:
    fh.write(html)

print("wrote", out_path, os.path.getsize(out_path), "bytes")
print("remaining data URIs:", html.count("data:image/"))

# -*- coding: utf-8 -*-
"""Publish the brand sheet.

Source of truth : brand-sheet.src.html  (editable, relative image paths)
Outputs         : brand-sheet.html      (root, self-contained, base64 figures)
                  dist/spec.html        (same, paths rebased for dist/)

Never hand-edit brand-sheet.html or dist/spec.html - edit the .src.html and
re-run this script.
"""
import base64
import os
import re
from io import BytesIO

from PIL import Image

BASE = r"D:\02_MyWorkSpace\02_QYN Development Project\09Projects already tested\AI Shortcut Prompt\brand-logo-v2"
SRC = os.path.join(BASE, "brand-sheet.src.html")
DIST = os.path.join(BASE, "dist")

MAX_W = 900
SIZE_CAP = 150_000
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml", ".webp": "image/webp"}


def datauri(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as fh:
        raw = fh.read()
    if ext in (".png", ".jpg", ".jpeg", ".webp") and len(raw) > SIZE_CAP:
        img = Image.open(path)
        if img.width > MAX_W:
            img = img.resize((MAX_W, int(img.height * MAX_W / img.width)),
                             Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        raw = buf.getvalue()
    return "data:%s;base64,%s" % (MIME.get(ext, "image/png"),
                                  base64.b64encode(raw).decode("ascii"))


def resolve(here, rel):
    p = os.path.normpath(os.path.join(here, rel))
    if os.path.exists(p):
        return p
    for extra in ("", "dist", "assets", "png-transparent"):
        alt = os.path.normpath(os.path.join(BASE, extra, rel))
        if os.path.exists(alt):
            return alt
    return None


def inline(html, here):
    seen, missing = [], []

    def repl(m):
        rel = m.group(1)
        if rel.startswith("data:"):
            return m.group(0)
        p = resolve(here, rel)
        if not p:
            missing.append(rel)
            return m.group(0)
        seen.append(rel)
        return 'src="%s"' % datauri(p)

    html = re.sub(r'src="([^"]+)"', repl, html)
    return html, seen, missing


with open(SRC, encoding="utf-8") as fh:
    src = fh.read()

# --- root copy: paths already correct ---
root_html, seen, missing = inline(src, BASE)
os.makedirs(BASE, exist_ok=True)
with open(os.path.join(BASE, "brand-sheet.html"), "w", encoding="utf-8") as fh:
    fh.write(root_html)
print("brand-sheet.html", os.path.getsize(os.path.join(BASE, "brand-sheet.html")), "bytes")

# --- dist copy: rebase ./x -> ../x, dist/x -> x ---
dist_src = src.replace('src="./assets/', 'src="../assets/')
dist_src = dist_src.replace('src="./png-transparent/', 'src="../png-transparent/')
dist_src = dist_src.replace('src="./editorial-', 'src="../editorial-')
dist_src = dist_src.replace('src="dist/', 'src="')
os.makedirs(DIST, exist_ok=True)
dist_html, seen2, missing2 = inline(dist_src, DIST)
with open(os.path.join(DIST, "spec.html"), "w", encoding="utf-8") as fh:
    fh.write(dist_html)
print("dist/spec.html", os.path.getsize(os.path.join(DIST, "spec.html")), "bytes")

for rel in seen:
    print("    embedded", rel)
for rel in missing + missing2:
    print("    !! MISSING", rel)

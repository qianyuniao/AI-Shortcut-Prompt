# -*- coding: utf-8 -*-
"""Make the brand sheet self-contained: replace relative image src with base64 data URIs.

The preview server serves a single HTML from its own directory, so ../assets/
resolves to nothing and every figure breaks. Embedding the bytes fixes it for
preview, for double-click opening, and for emailing the file as one attachment.
"""
import base64
import os
import re
from PIL import Image

BASE = r"D:\02_MyWorkSpace\02_QYN Development Project\09Projects already tested\AI Shortcut Prompt\brand-logo-v2"
DIST = os.path.join(BASE, "dist")

MAX_W = 900          # downscale anything wider before embedding
SIZE_CAP = 150_000   # bytes; above this we re-encode

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml", ".webp": "image/webp"}


def embed_bytes(raw, ext):
    return "data:%s;base64,%s" % (MIME.get(ext, "image/png"),
                                  base64.b64encode(raw).decode("ascii"))


def datauri(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as fh:
        raw = fh.read()
    if ext in (".png", ".jpg", ".jpeg", ".webp") and len(raw) > SIZE_CAP:
        img = Image.open(path)
        if img.width > MAX_W:
            img = img.resize((MAX_W, int(img.height * MAX_W / img.width)),
                             Image.LANCZOS)
        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        raw = buf.getvalue()
    return embed_bytes(raw, ext)


def resolve(html_path, rel):
    here = os.path.dirname(html_path)
    p = os.path.normpath(os.path.join(here, rel))
    if os.path.exists(p):
        return p
    for extra in ("", "dist", "assets"):
        alt = os.path.normpath(os.path.join(BASE, extra, rel))
        if os.path.exists(alt):
            return alt
    return None


def inline(html_path):
    with open(html_path, encoding="utf-8") as fh:
        html = fh.read()
    seen, missing = [], []

    def repl(m):
        rel = m.group(1)
        if rel.startswith("data:"):
            return m.group(0)
        p = resolve(html_path, rel)
        if not p:
            missing.append(rel)
            return m.group(0)
        seen.append((rel, os.path.getsize(p)))
        return 'src="%s"' % datauri(p)

    html = re.sub(r'src="([^"]+)"', repl, html)
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(os.path.basename(html_path), "->", os.path.getsize(html_path), "bytes")
    for rel, sz in seen:
        print("    embedded", rel, sz)
    for rel in missing:
        print("    !! MISSING", rel)


for hp in (os.path.join(DIST, "spec.html"),
           os.path.join(BASE, "brand-sheet.html")):
    if os.path.exists(hp):
        inline(hp)

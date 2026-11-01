#!/usr/bin/env python3
"""
Adds width/height attributes to every <img src="/images/....webp"> that doesn't have them yet,
by reading the real size from the .webp file. Run it from the /site folder after you add images:

    python3 tools/fill-image-sizes.py

Safe to re-run (it only touches <img> tags that have no width yet). Needs only Python 3, no packages.
This is an optional helper, not a build step: the site works without it, but width/height
stop the page from jumping while images load.
"""
import os, re, struct, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def webp_size(path):
    with open(path, "rb") as f:
        head = f.read(64)
    if head[:4] != b"RIFF" or head[8:12] != b"WEBP":
        raise ValueError("not a WebP file")
    kind = head[12:16]
    if kind == b"VP8 ":                      # lossy
        w, h = struct.unpack("<HH", head[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if kind == b"VP8L":                      # lossless
        b = struct.unpack("<I", head[21:25])[0]
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    if kind == b"VP8X":                      # extended (alpha etc.)
        w = 1 + (head[24] | head[25] << 8 | head[26] << 16)
        h = 1 + (head[27] | head[28] << 8 | head[29] << 16)
        return w, h
    raise ValueError("unknown WebP variant")


IMG = re.compile(r'<img\b[^>]*>')
changed = missing = 0
for dirpath, _, files in os.walk(SITE):
    if set(dirpath.split(os.sep)) & {"tools", "images", "css", "js", "_templates"}:
        continue
    for name in files:
        if not name.endswith(".html"):
            continue
        p = os.path.join(dirpath, name)
        text = open(p, encoding="utf-8").read()

        def fix(m):
            global changed, missing
            tag = m.group(0)
            if re.search(r'\bwidth=', tag):
                return tag
            src = re.search(r'\bsrc="(/images/[^"]+\.webp)"', tag)
            if not src:
                return tag
            fp = os.path.join(SITE, src.group(1).lstrip("/"))
            if not os.path.exists(fp):
                missing += 1
                return tag
            w, h = webp_size(fp)
            changed += 1
            return tag.replace("<img ", f'<img width="{w}" height="{h}" ', 1)

        new = IMG.sub(fix, text)
        if new != text:
            open(p, "w", encoding="utf-8").write(new)

print(f"updated {changed} <img> tags; {missing} skipped because the .webp file isn't there yet")

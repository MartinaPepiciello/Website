"""Stamp every /css/..., /js/... and favicon link in the site's pages with ?v=<short hash of the file>, so browsers fetch a
stylesheet, script or icon again as soon as it changes (instead of showing a cached copy). Run after editing CSS/JS:
    python tools/bust-cache.py
"""
import hashlib, os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = re.compile(r'((?:href|src)="/((?:css|js)/[^"?]+|images/icons/(?:favicon|apple-touch-icon)[^"?]*))(?:\?v=[0-9a-f]+)?"')


def digest(rel, cache={}):
    if rel not in cache:
        with open(os.path.join(SITE, rel), "rb") as f:
            cache[rel] = hashlib.sha1(f.read()).hexdigest()[:8]
    return cache[rel]


changed = 0
for root, dirs, files in os.walk(SITE):
    dirs[:] = [d for d in dirs if not d.startswith((".", "_"))]
    for name in files:
        if not name.endswith(".html"):
            continue
        path = os.path.join(root, name)
        html = open(path, encoding="utf-8").read()
        new = REF.sub(lambda m: f'{m.group(1)}?v={digest(m.group(2))}"', html)
        if new != html:
            open(path, "w", encoding="utf-8", newline="\n").write(new)
            changed += 1
print(f"stamped links in {changed} page(s)")

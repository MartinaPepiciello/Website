"""Export the Constitutional AI infographic's narrow (mobile) layout as an editable SVG for Illustrator.

usage: python export_cai_svg.py <site dir> <out.svg>
Needs the dev server on http://localhost:8000. Opens the page in headless Chrome inside a 600px-wide iframe
(so the figure is 560px wide and one design unit is one pixel), reads every box, text line and arrow with
cai_extract.js, then writes one named group per element. Artwork symbols are inlined, text stays live text.
"""
import html, json, os, re, subprocess, sys, tempfile

SITE, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PAGE = "constitutional-ai-training-diagram"

# 1. same-origin wrapper page (temporary, deleted below) that runs the extractor on the iframe
wrapper = os.path.join(SITE, "_cai-export.html")
js = open(os.path.join(HERE, "cai_extract.js"), encoding="utf-8").read()
open(wrapper, "w", encoding="utf-8").write(f"""<!doctype html><meta charset="utf-8">
<iframe id="f" src="/{PAGE}/" style="border:0;width:600px;height:9000px"></iframe><pre id="out"></pre>
<script>{js}
document.getElementById('f').addEventListener('load', async e => {{
  const w = e.target.contentWindow; await new Promise(r => setTimeout(r, 1500));
  document.getElementById('out').textContent = JSON.stringify(await extract(w, w.document));
}});</script>""")
try:
    prof = tempfile.mkdtemp(prefix="chrome-")
    dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={prof}", "--virtual-time-budget=20000",
                          "--window-size=700,1000", "--dump-dom", "http://localhost:8000/_cai-export.html"],
                         capture_output=True, text=True, encoding="utf-8", timeout=120).stdout
finally:
    os.remove(wrapper)
m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
assert m and m.group(1).strip(), "extractor produced nothing"
data = json.loads(html.unescape(m.group(1)))
assert data["W"] == 560, data["W"]

# 2. artwork symbols from the page
page = open(os.path.join(SITE, PAGE, "index.html"), encoding="utf-8").read()
SYMS = {mm.group(1): ([float(v) for v in mm.group(2).split()], re.sub(r'\s(id|data-name)="[^"]*"', "", mm.group(3)))
        for mm in re.finditer(r'<symbol id="([^"]+)" viewBox="([^"]+)">(.*?)</symbol>', page, re.S)}

def hexc(c):
    mm = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", c)
    return "#%02x%02x%02x" % tuple(int(v) for v in mm.groups()) if mm else c

def f(v): return ("%.1f" % v).rstrip("0").rstrip(".")

NAMES = {"prompt": "harmful prompt", "llm1": "helpful LLM", "llm2": "helpful LLM (critiques)", "toxic": "toxic response",
         "revised": "revised response", "book": "constitution", "critique": "critique bubble", "docs": "set of finetuned responses",
         "llmh": "helpful LLM", "sl": "supervised learning", "ft": "finetuned LLM", "ft1": "finetuned LLM", "r1": "response 1",
         "r2": "response 2", "ft2": "finetuned LLM (judges)", "q": "which-response bubble", "labels": "preference labels",
         "ds1": "AI-generated dataset", "ds2": "human-generated dataset", "pm": "preference model", "ft3": "finetuned LLM",
         "rl": "reinforcement learning", "al": "RLAIF aligned LLM", "loop1": "repeat loop", "loop2": "repeat loop"}

def label(gid):
    if gid == "title": return "Title"
    ph, _, node = gid.partition("-")
    n = {"band": "band", "arrows": "arrows"}.get(node) or NAMES.get(node, node)
    return f"Phase {ph[-1]} · {n}"

def text(t):
    # one <text> per run of lines in the same style (e.g. a band's heading and its subtitle are separate objects)
    runs = []
    for l in t["lines"]:
        key = (l["fs"], l["fw"], l["c"])
        if not runs or runs[-1][0] != key: runs.append((key, []))
        runs[-1][1].append(l)
    out = []
    for (fs, fw, c), ls in runs:
        bold = fw >= 600
        fam = "NunitoSans-Bold, 'Nunito Sans'" if bold else "NunitoSans-Regular, 'Nunito Sans'"
        spans = "".join(f'<tspan x="{f(l["x"])}" y="{f(l["y"])}">{html.escape(l["t"])}</tspan>' for l in ls)
        out.append(f'<text font-family="{fam}" font-weight="{700 if bold else 400}" font-size="{f(fs)}" '
                   f'fill="{hexc(c)}" text-anchor="middle">{spans}</text>')
    return "".join(out)

def card(it):
    x, y, w, h, r, c = it["x"], it["y"], it["w"], it["h"], 8, 27.5
    d = (f"M{f(x + r)},{f(y)}H{f(x + w - r)}A{r},{r} 0 0 1 {f(x + w)},{f(y + r)}V{f(y + h - c)}L{f(x + w - c)},{f(y + h)}"
         f"H{f(x + r)}A{r},{r} 0 0 1 {f(x)},{f(y + h - r)}V{f(y + r)}A{r},{r} 0 0 1 {f(x + r)},{f(y)}Z")
    corner = f"{f(x + w - c)},{f(y + h - c)} {f(x + w)},{f(y + h - c)} {f(x + w - c)},{f(y + h)}"
    return (f'<path data-name="card" d="{d}" fill="{hexc(it["fill"])}"/>'
            f'<polygon data-name="folded corner" points="{corner}" fill="{hexc(it["corner"])}"/>')

def item(it):
    k = it["k"]
    nm = f' data-name="{it["name"]}"' if it.get("name") else ""
    if k == "rect":
        a = f'x="{f(it["x"])}" y="{f(it["y"])}" width="{f(it["w"])}" height="{f(it["h"])}"'
        if it.get("rx"): a += f' rx="{f(it["rx"])}"'
        a += f' fill="{hexc(it["fill"])}"'
        if it.get("fop") is not None: a += f' fill-opacity="{it["fop"]}"'
        if it.get("stroke"): a += f' stroke="{it["stroke"]}" stroke-width="{it["sw"]}"'
        return f"<rect{nm} {a}/>"
    if k == "poly":
        tr = f' transform="translate({f(it["dx"])} {f(it["dy"])})"' if "dx" in it else ""
        return f'<polygon{nm} points="{it["pts"]}" fill="{hexc(it["fill"])}"{tr}/>'
    if k == "path":
        d = re.sub(r"\d+\.\d+", lambda mm: f(float(mm.group())), it["d"])
        return (f'<path d="{d}" fill="none" stroke="{it["stroke"]}" stroke-width="{it["sw"]}" '
                f'transform="translate({f(it["dx"])} {f(it["dy"])})"/>')
    if k == "sym":
        (vx, vy, vw, vh), inner = SYMS[it["s"]]
        s = it["w"] / vw
        sc = "" if abs(s - 1) < 1e-3 else f" scale({s:.4f})"
        return f'<g data-name="artwork" transform="translate({f(it["x"])} {f(it["y"])}){sc} translate({f(-vx)} {f(-vy)})">{inner}</g>'
    if k == "card": return card(it)
    if k == "text": return text(it)
    raise ValueError(k)

# drawing order as on the page: band, loop, arrows, then the nodes on top
groups = data["groups"]
def order(g):
    i = groups.index(g); gid = g["id"]
    ph = 0 if gid == "title" else int(gid[5])
    rank = 0 if gid.endswith("-band") else 1 if "-loop" in gid else 2 if gid.endswith("-arrows") else 3
    return (ph, rank if gid != "title" else 0, i)

W, H = data["W"], data["H"]
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{f(W)}" height="{f(H)}" viewBox="0 0 {f(W)} {f(H)}">',
       "<!-- Constitutional AI infographic, narrow (mobile) layout. 560 units wide = the figure's width on a phone, scaled.",
       "     Keep the group names: they map back to the nodes on the page (phase1-prompt, phase2-ft2, ...). -->"]
cur = None
for g in sorted(groups, key=order):
    ph = "title" if g["id"] == "title" else g["id"][:6]
    if ph != cur:
        if cur not in (None, "title"): out.append("</g>")
        if ph != "title": out.append(f'<g id="{ph}" data-name="Phase {ph[-1]}">')
        cur = ph
    out.append(f'<g id="{g["id"]}" data-name="{label(g["id"])}">' + "".join(item(it) for it in g["items"]) + "</g>")
out.append("</g></svg>")
svg = "\n".join(out)
open(OUT, "w", encoding="utf-8", newline="\n").write(svg)
print("wrote", OUT, f"{len(svg) // 1024} KB,", len(groups), "groups,", f"{f(W)}x{f(H)}")

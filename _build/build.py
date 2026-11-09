"""One-off: write the live site's project text and image lists into the static pages."""
import html, json, os, re, sys

SITE = sys.argv[1]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from projects import DIAGRAMS, COMICS
from alts import ALTS
from layouts import LAYOUTS, SUBS, TAGS, TAG_LABELS

for _p in DIAGRAMS + COMICS:
    _p["images"] = [(f, ALTS.get(f, a)) for f, a in _p["images"]]
    _missing = [f for f, _ in _p["images"] if f not in ALTS and not f.startswith(("cai", "intro-to-ea"))]
    assert not _missing, _missing

BASE = "https://www.martinapepiciello.com"
# infographics built as HTML: markup snippet + the extra stylesheet/script/font that page needs
FIGURES = {
    "constitutional-ai-training-diagram": {
        "html": "cai_figure.html",
        "head": ['<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;700&display=swap" rel="stylesheet">',
                 '<link rel="stylesheet" href="/css/cai.css">'],
        "body": ['<script src="/js/flow.js" defer></script>'],
    },
    "introduction-to-effective-altruism-infographic": {
        "html": "ea_figure.html",
        "head": ['<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Raleway:wght@600;700&display=swap" rel="stylesheet">',
                 '<link rel="stylesheet" href="/css/ea.css">'],
        "body": ['<script src="/js/ea.js" defer></script>'],
    },
}
SECTIONS = [("diagrams", "Diagrams and infographics", DIAGRAMS), ("comics", "Comic illustrations", COMICS)]
ARR = '<span class="arr" aria-hidden="true">→</span>'


def block(b):
    return b if b.startswith("<") else f"<p>{b}</p>"


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def describe(p):
    text = plain(p["body"][0])
    if len(text) > 158:
        text = text[:155].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return text


def img_tag(sec, slug, f, alt, extra=""):
    return f'<img class="art" src="/images/{sec}/{slug}/{f}" alt="{html.escape(alt)}"{extra} loading="lazy" decoding="async">'


def size(sec, slug, f):
    from PIL import Image
    return Image.open(os.path.join(SITE, "images", sec, slug, f)).size


def fig(sec, slug, f, alts, k):
    w, h = size(sec, slug, f)
    return (f'<figure class="wipe" style="--ar:{w / h:.4f};--w:{w}px;--i:{k % 4}">'
            f'<img src="/images/{sec}/{slug}/{f}" alt="{html.escape(alts[f])}" width="{w}" height="{h}" loading="lazy" decoding="async"></figure>')


def rows_html(sec, slug, rows, alts, cls="rows"):
    out = [f'    <div class="{cls}">']
    for row in rows:
        n = {1: " one", 3: " three", 4: " four"}.get(len(row), "")
        out.append(f'      <div class="row{n}">' + "".join(fig(sec, slug, f, alts, k) for k, f in enumerate(row)) + "</div>")
    out.append("    </div>")
    return "\n".join(out)


def prose(blocks, extra="", cls="prose reveal"):
    return "\n".join([f'    <div class="{cls}">'] + ["      " + block(b) for b in blocks] + ([extra] if extra else []) + ["    </div>"])


# Soft background glows beside the project text (like the corners of the "What clients say" section, but fading
# into the white page). Organic shapes, heavily blurred; they reach up and down behind the images, which sit on top.
GLOW_SHAPES = ["58% 42% 63% 37% / 46% 58% 42% 54%", "42% 58% 38% 62% / 55% 44% 56% 45%", "65% 35% 52% 48% / 40% 62% 38% 60%"]
GLOW_SPOTS = {  # (left %, top %, width px, height px, colour) relative to the text block; colour: n = navy, e = emerald
    1: [(54, -35, 620, 460, None)],
    2: [(50, -40, 600, 440, "e"), (66, 30, 560, 480, "n")],
}


def glows_html(slug, n):
    seed = sum(map(ord, slug))
    out = ['    <div class="glows" aria-hidden="true">']
    for k, (x, y, w, h, col) in enumerate(GLOW_SPOTS[n]):
        col = col or ("e" if seed % 2 else "n")
        shape = GLOW_SHAPES[(seed + k) % len(GLOW_SHAPES)]
        rot = (seed * 29 + k * 53) % 360
        out.append(f'      <span class="glow-{col}" style="left:{x}%;top:{y}%;width:{w}px;height:{h}px;border-radius:{shape};transform:rotate({rot}deg)"></span>')
    out.append("    </div>")
    return "\n".join(out)


def intro(slug, blocks, extra="", cls="intro-text"):
    chars = len(plain(" ".join(blocks)))
    n = 1 if chars < 1000 else 2
    return (f'    <div class="{cls}">\n' + prose(blocks, extra).replace("\n", "\n  ").replace("    <div", "      <div", 1)
            + "\n" + glows_html(slug, n).replace("\n", "\n  ").replace("    <div", "      <div", 1) + "\n    </div>")


def main_html(sec, sec_title, p, prev, nxt):
    slug, lay = p["slug"], LAYOUTS[p["slug"]]
    alts = dict(p["images"])
    files = [f for f, _ in p["images"]]
    used = [f for r in lay.get("lead", []) + lay.get("rows", []) for f in r] + ([lay["side"]] if lay.get("side") else [])
    rest = [f for f in files if f not in used]
    assert lay.get("strip") or lay.get("masonry") or not rest, (slug, rest)
    assert len(used) == len(set(used)) and set(used) <= set(files), slug

    out = ["<main>", '<section class="page-head">', '  <div class="project">',
           f'    <a class="crumb" href="/{sec}/">← {sec_title}</a><br>',
           f'    <h1>{p.get("h1", p["title"])}</h1>']
    out.append(f'    <p class="lede">{SUBS[slug]}</p>')
    out += ["  </div>", "</section>", "", '<section class="gallery">', '  <div class="project">']

    links = ""
    if p.get("links"):
        links = '      <div class="links">' + "".join(
            f'<a class="btn" href="{h}" rel="noopener" target="_blank">{t} {ARR}</a>' for h, t in p["links"]) + "</div>"
    if lay.get("lead"):
        out.append(rows_html(sec, slug, lay["lead"], alts, "rows lead"))
    if lay.get("side"):
        split = lay.get("split", 0)
        if split:
            out.append(intro(slug, p["body"][:split]))
        out.append('    <div class="side wide-img">' if lay.get("wide") else '    <div class="side">')
        out.append(prose(p["body"][split:], links, "prose reveal").replace("\n    ", "\n      ").replace("    <div", "      <div", 1))
        out.append("      " + fig(sec, slug, lay["side"], alts, 1))
        out.append("    </div>")
    else:
        out.append(intro(slug, p["body"], links))
    if lay.get("strip") and slug in FIGURES:
        snippet = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), FIGURES[slug]["html"]), encoding="utf-8").read()
        out.append("\n".join("    " + line for line in snippet.splitlines()))
    elif lay.get("strip"):
        out.append('    <div class="strip">\n' + "\n".join(
            "      " + img_tag(sec, slug, f, alts[f]).replace('class="art" ', "") for f in files) + "\n    </div>")
    if lay.get("rows"):
        out.append(rows_html(sec, slug, lay["rows"], alts))
    if lay.get("masonry"):
        out.append(f'    <div class="masonry" style="--cols:{lay["masonry"]}">\n' + "\n".join(
            "      " + fig(sec, slug, f, alts, k) for k, f in enumerate(rest)) + "\n    </div>")
    if p.get("after"):
        out.append(intro(slug + "/after", p["after"], cls="intro-text after-text"))   # with its own glows, like the intro
    if p.get("videos"):
        out.append('    <div class="videos reveal">' + "".join(
            f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{v}" title="{t}" loading="lazy" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
            for v, t in p["videos"]) + "</div>")
    if p.get("review"):
        out.append(f'    <figure class="review reveal"><blockquote><p>{p["review"]}</p></blockquote><figcaption>Client\'s review</figcaption></figure>')
    out.append(f'    <div class="cta reveal"><p>{p["cta"]}</p><div class="btnrow">'
               f'<a class="btn" href="/contact/">Contact me {ARR}</a><a class="btn btn--ghost" href="/about/">More about me {ARR}</a></div></div>')
    nav = []
    if prev:
        nav.append(f'<a class="prev" href="/{prev["slug"]}/"><small>← Previous</small><span>{prev["title"]}</span></a>')
    if nxt:
        nav.append(f'<a class="next" href="/{nxt["slug"]}/"><small>Next →</small><span>{nxt["title"]}</span></a>')
    out.append('    <nav class="pager" aria-label="More projects">' + "".join(nav) + "</nav>")
    out += ["  </div>", "</section>", "</main>"]
    return "\n".join(out)


def set_meta(doc, attr, key, value):
    pat = re.compile(rf'(<meta {attr}="{re.escape(key)}" content=")[^"]*(">)')
    assert pat.search(doc), key
    return pat.sub(lambda m: m.group(1) + html.escape(value, quote=True) + m.group(2), doc)


projects = {}
for sec, sec_title, items in SECTIONS:
    for i, p in enumerate(items):
        projects[p["slug"]] = (sec, p)
        path = os.path.join(SITE, p["slug"], "index.html")
        doc = open(path, encoding="utf-8").read()
        title = f'{p.get("h1", p["title"])} — Martina Pepiciello'
        desc = describe(p)
        doc = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title, quote=False)}</title>", doc)
        doc = set_meta(doc, "name", "description", desc)
        doc = set_meta(doc, "property", "og:title", title)
        doc = set_meta(doc, "property", "og:description", desc)
        og = p["images"][0][0]
        if not os.path.exists(os.path.join(SITE, "images", sec, p["slug"], og)):
            og = p.get("thumb", og)
        doc = set_meta(doc, "property", "og:image", f'{BASE}/images/{sec}/{p["slug"]}/{og}')
        prev = items[i - 1] if i else None
        nxt = items[i + 1] if i + 1 < len(items) else None
        doc = re.sub(r"<main>.*?</main>", lambda m: main_html(sec, sec_title, p, prev, nxt), doc, flags=re.S)
        if p["slug"] in FIGURES:
            f = FIGURES[p["slug"]]
            unstamped = re.sub(r"\?v=[0-9a-f]+", "", doc)          # links may carry cache-busting stamps (tools/bust-cache.py)
            for tag in f["head"]:
                if tag not in unstamped:
                    doc = re.sub(r'(<link rel="stylesheet" href="/css/style\.css(?:\?v=[0-9a-f]+)?">)', lambda m: m.group(1) + "\n" + tag, doc, count=1)
            for tag in f["body"]:
                if tag not in unstamped:
                    doc = doc.replace("</body>", tag + "\n</body>", 1)
        open(path, "w", encoding="utf-8", newline="\n").write(doc)


def thumb(p):
    return p.get("thumb") or re.sub(r"\.webp$", "-800.webp", p["images"][0][0])


# index tiles: point every linked tile at its project's thumbnail
def fix_tiles(doc):
    def repl(m):
        slug = m.group(2)
        if slug not in projects:
            return m.group(0)
        sec, p = projects[slug]
        alt = ALTS.get(thumb(p).replace("-800.webp", ".webp"), p["images"][0][1])
        frame = f'<div class="frame">{img_tag(sec, slug, thumb(p), alt)}</div>'
        return m.group(1) + re.sub(r'<div class="frame">.*?</div>(?=<span class="cap">)', frame, m.group(3), flags=re.S)
    doc = re.sub(r'(<a class="tile wipe"[^>]*href="/([^/"]+)/">)(.*?</a>)', repl, doc, flags=re.S)

    # topic tags for the filters
    def tag(m):
        slug = m.group(2) or "aml-research-program"
        head = re.sub(r' data-tags="[^"]*"', "", m.group(1))
        return head.replace(' style=', f' data-tags="{" ".join(TAGS[slug])}" style=', 1)
    return re.sub(r'(<(?:a|div) class="tile wipe"[^>]*?(?:href="/([^/"]+)/")?>)', tag, doc)


def filters_html(slugs):
    used = [k for k in TAG_LABELS if any(k in TAGS[s] for s in slugs)]
    pills = ['<button class="pill is-active" type="button" data-filter="all" aria-pressed="true">All</button>'] + [
        f'<button class="pill" type="button" data-filter="{k}" aria-pressed="false">{TAG_LABELS[k]}</button>' for k in used]
    return ('<section class="filters-bar">\n  <div class="wide">\n    <div class="filters" role="group" aria-label="Filter by topic">'
            + "".join(pills) + '</div>\n  </div>\n</section>\n')


for page in ["index.html", "diagrams/index.html", "comics/index.html"]:
    path = os.path.join(SITE, page)
    doc = fix_tiles(open(path, encoding="utf-8").read())
    if page != "index.html":
        sec = page.split("/")[0]
        slugs = [p["slug"] for p in (DIAGRAMS if sec == "diagrams" else COMICS)] + (["aml-research-program"] if sec == "diagrams" else [])
        doc = re.sub(r'<section class="filters-bar">.*?</section>\n', "", doc, flags=re.S)
        doc = doc.replace('<section class="gallery">', filters_html(slugs) + '\n<section class="gallery">', 1)
    open(path, "w", encoding="utf-8", newline="\n").write(doc)

# content.json: keep it as the reference copy of what's on the pages
cj_path = os.path.join(SITE, "content.json")
cj = json.load(open(cj_path, encoding="utf-8"))
old = {p["slug"]: p for p in cj["diagrams"] + cj["comics"]}
for sec, _, items in SECTIONS:
    new = []
    for p in items:
        e = {"slug": p["slug"], "title": p["title"], "page": True}
        if p.get("h1"): e["h1"] = p["h1"]
        if p.get("sub"): e["subtitle"] = p["sub"]
        if p.get("layout"): e["layout"] = p["layout"]
        e["body"] = p["body"]
        if p.get("links"): e["links"] = [{"href": h, "text": t} for h, t in p["links"]]
        e["thumb"] = thumb(p)
        if p["slug"] in FIGURES:
            e["figure"] = "built as HTML in the page (see README), not images"
        else:
            e["images"] = [{"file": f, "alt": a} for f, a in p["images"]]
        if p.get("after"): e["after_images"] = p["after"]
        if p.get("videos"): e["youtube"] = [v for v, _ in p["videos"]]
        if p.get("review"): e["review"] = p["review"]
        e["cta"] = p["cta"]
        new.append(e)
    if sec == "diagrams":
        aml = old["aml-research-program"]
        new.append({"slug": aml["slug"], "title": aml["title"], "page": False, "body": [], "thumb": "aml-800.webp",
                    "images": [{"file": "aml.webp", "alt": "Acute myeloid leukemia research program: four work packages studying CyPD in mitochondria and in AML patients"}]})
    cj[sec] = new
json.dump(cj, open(cj_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
print("ok:", len(projects), "project pages")

# stamp css/js links so browsers pick up changes
import subprocess
subprocess.run([sys.executable, os.path.join(SITE, "tools", "bust-cache.py")], check=True)

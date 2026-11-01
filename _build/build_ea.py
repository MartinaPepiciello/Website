"""Build the 'Introduction to Effective Altruism' infographic as HTML.
Pieces of the original SVG (illustrations, icons, charts, small cards) become inline SVG tiles with live text;
cause-area cards, pictograms, timelines and headings are HTML. Writes ea_figure.html next to this script."""
import copy, html, os, re, sys
import xml.etree.ElementTree as ET

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ea_figure.html")
NS = "{http://www.w3.org/2000/svg}"
XL = "{http://www.w3.org/1999/xlink}"
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
root = ET.parse(SRC).getroot()
IMG_DIR = "/images/diagrams/introduction-to-effective-altruism-infographic/"
CARD_BG = "#ccf0f2"          # #00b2be at 20% on white: the light card colour
TEAL, DARK = "#0c869b", "#333"

# ---- styles: class -> declarations --------------------------------------------------------------------------------
css = "".join(t for s in root.iter(f"{NS}style") for t in s.itertext())
styles = {}
for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", css):
    decls = []
    for d in body.split(";"):
        d = d.strip()
        if not d:
            continue
        k, _, v = d.partition(":")
        k, v = k.strip(), v.strip()
        if k == "font-family":
            v = "Merriweather, serif"
        decls.append(f"{k}:{v}")
    for c in re.findall(r"\.(cls-\d+)", sel):
        styles.setdefault(c, []).extend(decls)

defs = {e.get("id"): e for e in root.iter() if e.get("id")}
layer = defs["Layer_1"]
K = list(layer)


def get(path):
    e = K[path[0]]
    for i in path[1:]:
        e = list(e)[i]
    return e


def inline(el):
    for e in el.iter():
        cls = e.get("class")
        if cls:
            st = ";".join(sum((styles.get(c, []) for c in cls.split()), []))
            if e.get("style"):
                st += ";" + e.get("style")
            e.set("style", st)
            del e.attrib["class"]
        e.attrib.pop("data-name", None)
        if e.tag == f"{NS}image":
            for a in ("href", f"{XL}href"):
                if e.get(a):
                    e.set(a, IMG_DIR + "animals.webp")


def refs_of(el):
    s = ET.tostring(el, encoding="unicode")
    found = set(re.findall(r"url\(#([^)\"']+)\)", s))
    found |= set(re.findall(r'href="#([^"]+)"', s))
    return found


def tile(paths, box, tid, pad=3, cls="tile", title=None, card_rects=False, aria_hidden=False, extra="", edit=None):
    els = [copy.deepcopy(get(p)) for p in paths]
    if edit:
        edit(els)
    for e in els:
        inline(e)
        if card_rects:   # light card backgrounds (#00b2be at 0-20% in the file, some invisible): one solid card colour
            for r in e.iter(f"{NS}rect"):
                st = r.get("style", "").replace(" ", "")
                if "fill:#00b2be" in st and re.search(r"opacity:(0|\.1|\.2)(;|$)", st):
                    r.set("style", re.sub(r"opacity:[\d.]+", "opacity:1", st) + f";fill:{CARD_BG}")
    # copy referenced defs (gradients, clip paths, masks, ...) recursively, with ids made unique per tile
    need, done, dcopies = set().union(*[refs_of(e) for e in els]), set(), []
    while need - done:
        rid = (need - done).pop(); done.add(rid)
        if rid in defs and rid != "Layer_1":
            d = copy.deepcopy(defs[rid]); inline(d); dcopies.append(d); need |= refs_of(d)
    body = "".join(ET.tostring(x, encoding="unicode") for x in dcopies + els) + extra
    body = re.sub(r'\s+xmlns(:\w+)?="[^"]+"', "", body)
    for rid in done:
        body = body.replace(f'id="{rid}"', f'id="{tid}-{rid}"').replace(f"url(#{rid})", f"url(#{tid}-{rid})").replace(f'href="#{rid}"', f'href="#{tid}-{rid}"')
    body = body.replace("ns0:", "").replace("xlink:href", "href")
    x, y, w, h = box
    vb = f"{x - pad:.1f} {y - pad:.1f} {w + 2 * pad:.1f} {h + 2 * pad:.1f}"
    t = f"<title>{html.escape(title)}</title>" if title else ""
    hid = ' aria-hidden="true"' if aria_hidden else (' role="img"' if title else "")
    return (f'<svg class="{cls}" viewBox="{vb}" style="--tw:{w + 2 * pad:.1f};--th:{h + 2 * pad:.1f}"{hid} focusable="false">{t}{body}</svg>',
            (x - pad, y - pad, w + 2 * pad, h + 2 * pad))


def symbol(path, sid, box, mono=False, pad=1):
    e = copy.deepcopy(get(path)); inline(e)
    if mono:
        for x in e.iter():
            if x.get("style"):
                x.set("style", re.sub(r"fill:\s*#[0-9a-fA-F]{3,6}", "fill:currentColor", x.get("style")))
    s = re.sub(r'\s+xmlns(:\w+)?="[^"]+"', "", ET.tostring(e, encoding="unicode")).replace("ns0:", "")
    x, y, w, h = box
    return f'<symbol id="{sid}" viewBox="{x - pad} {y - pad} {w + 2 * pad} {h + 2 * pad}">{s}</symbol>'


# ---- bounding boxes measured in the browser (original artboard units, 1280 wide) -----------------------------------
B = {"bulb": (496, 192, 285, 448), "cardL": (30, 198, 413, 340), "cardR": (839, 298, 413, 241),
     "income": (54, 2199, 286, 382), "ai": (55, 3333, 544, 257), "decision": (682, 2810, 542, 779),
     "compass": (459, 4416, 362, 433), "woman": (94, 5142, 196, 290),
     "ic_pandemic": (507, 881, 96, 97), "ic_needs": (504, 1883, 107, 103), "ic_ai": (485, 3032, 113, 93),
     "ic_farm": (1127, 1018, 106, 99), "ic_decision": (1107, 2509, 113, 100),
     "skull": (170, 1199, 22, 22), "dollar": (447, 1382, 22, 22), "person": (496, 2236, 10, 22),
     "act1": (655, 5102, 96, 96), "act2": (655, 5243, 96, 96), "act3": (655, 5374, 96, 96), "act4": (655, 5535, 96, 96),
     "vTL": (29, 4425, 380, 173), "vBL": (29, 4637, 380, 173), "vTR": (871, 4425, 380, 173), "vBR": (871, 4637, 380, 172),
     "animals": (873, 1368, 348, 348), "action": (29, 5100, 1221, 535)}

symbols = "".join([symbol([23, 18], "ea-skull", B["skull"], mono=True), symbol([23, 16], "ea-dollar", B["dollar"], mono=True),
                   symbol([24, 12], "ea-person", B["person"], mono=True)])

R = lambda a, b: [[i] for i in range(a, b + 1)]
T = {}
# the bulb: Martina's clean bulb file (assets/lightbulbArtboard 3 copy.svg), placed over the original artwork's bulb
# (the same drawing at 1/4.535 scale, top of the outline at 640,191.8)
def bulb_tile():
    import os
    src = os.path.join(os.path.dirname(sys.argv[1]), "assets", "lightbulbArtboard 3 copy.svg")
    t = open(src, encoding="utf-8").read()
    css = re.search(r"<style>(.*?)</style>", t, re.S).group(1)
    st = {}
    for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", css):
        for c in re.findall(r"\.(cls-\d+)", sel):
            st.setdefault(c, []).append(body.strip().rstrip(";").replace("\n", "").replace("  ", ""))
    body = re.search(r"<defs>.*?</style>(.*?)</defs>(.*)</svg>", t, re.S)
    inner = "<defs>" + body.group(1) + "</defs>" + body.group(2)
    inner = re.sub(r'class="([^"]+)"', lambda m: 'style="' + ";".join(";".join(st.get(c, [])) for c in m.group(1).split()) + '"', inner)
    for i in set(re.findall(r'id="([^"]+)"', inner)):
        inner = inner.replace(f'id="{i}"', f'id="nb-{i}"').replace(f"url(#{i})", f"url(#nb-{i})").replace(f'href="#{i}"', f'href="#nb-{i}"')
    inner = inner.replace("xlink:href", "href").replace("fill: #0e879c", "fill: #0e879c", 1)
    inner = re.sub(r'<path (style="[^"]*#0e879c[^"]*") d="M50\.39,0', r'<path class="bulb-outline" \1 d="M50.39,0', inner)
    k = 448 / 98.78
    x, y, w, h = B["bulb"]
    svg = (f'<svg class="tile ea-bulb" viewBox="{x - 3} {y - 3} {w + 6} {h + 6}" style="--tw:{w + 6};--th:{h + 6}" aria-hidden="true" focusable="false">'
           f'<g transform="translate({640 - 50.39 * k:.2f} 191.8) scale({k:.4f})">{re.sub(chr(10) + " *", "", inner)}</g></svg>')
    return svg, (x - 3, y - 3, w + 6, h + 6)


T["bulb"] = bulb_tile()
# boxed exactly to the card (no padding): the connector line to the bulb runs outside the box, shown on wide screens only
T["cardL"] = tile([[20, i] for i in range(9)], (29.6, 198.1, 413.1, 339.6), "cardL", pad=0, cls="tile ea-icard ea-icard-l", card_rects=True)
T["cardR"] = tile([[21, i] for i in range(11)], (838.5, 298.2, 413.1, 240.2), "cardR", pad=0, cls="tile ea-icard ea-icard-r", card_rects=True)
def _shift(el, dx):
    tr = el.get("transform")
    if tr and tr.startswith("translate("):
        x, y = tr[10:-1].split()
        el.set("transform", f"translate({float(x) + dx:.1f} {y})")
    elif el.tag.endswith("circle"):
        el.set("cx", f"{float(el.get('cx')) + dx:.1f}")
    else:
        el.set("transform", f"translate({dx} 0)")


def _card_l(els):          # [rect, header, title, subtitle, white line, circle, icon, body] (teal connector left out)
    _shift(els[2], -99.3); _shift(els[3], -99.3)                  # text to the left padding
    _shift(els[5], 293); _shift(els[6], 293)                      # circle + icon to the right
    els[4].set("x1", "29.6"); els[4].set("x2", "382.7")           # white line: left edge -> into the circle


def _card_r(els):          # [rect, header, united, title, subtitle, circle, white line, icon, dot, bulb icon]
    _shift(els[5], -293.3); _shift(els[7], -293.3)                # circle + icon to the left
    _shift(els[3], 104.5); _shift(els[4], 104.5)                  # title and subtitle right of it
    els[6].set("x1", "898.5"); els[6].set("x2", "1251.6")         # white line: from the circle -> right edge


T["cardLm"] = tile([[20, i] for i in (0, 1, 2, 3, 6, 5, 7, 8)], (29.6, 198.1, 413.1, 339.6), "cardLm", pad=0,
                   cls="tile ea-icard ea-icard-l", card_rects=True, edit=_card_l)
T["cardRm"] = tile([[21, i] for i in (0, 1, 2, 3, 4, 6, 7, 8, 9, 10)], (838.5, 298.2, 413.1, 240.2), "cardRm", pad=0,
                   cls="tile ea-icard ea-icard-r", card_rects=True, edit=_card_r)
T["income"] = tile([[24, 22], [24, 15], [24, 16], [24, 17], [24, 18], [24, 19], [24, 21]], B["income"], "income", pad=6, cls="tile chart",
                   title="Chart of post-tax income per person against the world population ordered by income: income stays near zero for most of the world and shoots up for the richest few percent, where the median US college graduate sits.")
from ea_dots import DOTS
# the scatter plot: visible axes, trend line and brain markers, plus the 393 dots as plain circles
DOT_SVG = '<g fill="#333" fill-opacity=".4">' + "".join(f'<circle cx="{x}" cy="{y}" r="2.5"/>' for x, y in DOTS) + "</g>"
T["ai"] = tile([[25, i] for i in range(21, 46) if i != 24] + [[25, 24, 2], [25, 24, 3], [25, 24, 4], [25, 24, 6], [25, 24, 7]], B["ai"], "ai", pad=6, cls="tile chart", extra=DOT_SVG,
               title="Scatter plot of the computation used to train AI models from 2010 to now, rising steeply, with labelled models from AlexNet to GPT-4, and reference lines for the honeybee brain (reached around 2012) and the human brain (projected around 2032).")
T["brain"] = tile([[25, 38]], (522, 3356, 43, 49), "brain", pad=1, aria_hidden=True, cls="tile ea-legend-icon")
T["bee"] = tile([[25, 37]], (524, 3515, 39, 37), "bee", pad=1, aria_hidden=True, cls="tile ea-legend-icon")


def _placed(key, x, y):          # an icon tile as a nested <svg> placed at artboard x, y
    t = T[key][0]
    vb = re.search(r'viewBox="([^"]+)"', t).group(1).split()
    return re.sub(r'^<svg class="[^"]*" viewBox="[^"]+" style="[^"]*"', f'<svg x="{x}" y="{y}" width="{vb[2]}" height="{vb[3]}" viewBox="{" ".join(vb)}"', t)


# honeybee (small dot, 132,3531 r10) on the left, human brain (big dot, 386,3381 r27) on the right
AI_LEGEND = (_placed("bee", 79, 3244) + _placed("brain", 363.5, 3238)
             + '<g font-family="Merriweather, serif" font-size="14" fill="#0c869b">'
               '<text x="128" y="3260">Honeybee brain</text><text x="128" y="3277">~ 2012</text>'
               '<text x="355" y="3260" text-anchor="end">Human brain</text><text x="355" y="3277" text-anchor="end">~ 2032</text></g>'
             + '<path d="M99.5,3286V3531H121M386,3292V3353" fill="none" stroke="#0c869b" stroke-width="1.5" stroke-opacity=".7"/>')
T["ai_m"] = tile([[25, i] for i in range(21, 46) if i not in (24, 35, 36, 37, 38)] + [[25, 24, 2], [25, 24, 3], [25, 24, 4], [25, 24, 6], [25, 24, 7]],
                 (55, 3236, 403, 354), "aim", pad=6, cls="tile chart a-chart-m", extra=DOT_SVG + AI_LEGEND, aria_hidden=True)
T["decision"] = tile([[27, 7], [27, 8], [27, 9], [27, 10]], B["decision"], "decision", pad=6, cls="tile chart",
                     title="An average US politician can influence 10,000 citizens. Timeline from 1920 to 2020 splitting poor decision-making (failure to act against early signs of WWII, widespread use of leaded gasoline, the invasion of Iraq based on faulty intelligence, lack of oversight leading to the financial crisis, slow global response to COVID-19) from good decision-making (Universal Declaration of Human Rights, Montreal Protocol, global vaccination campaigns, Paris Agreement, international efforts to contain monkeypox).")
T["animals"] = tile([[26, 10], [26, 13]], B["animals"], "animals", pad=0, aria_hidden=True, cls="tile ea-animals")
T["compass"] = tile([[41], [46], [47], [48], [49]], B["compass"], "compass", aria_hidden=True, cls="tile ea-compass")
T["woman"] = tile([[63], [71], [72]], B["woman"], "woman", aria_hidden=True, cls="tile ea-woman")
for k, p in {"ic_pandemic": [23, 2], "ic_needs": [24, 8], "ic_ai": [25, 1], "ic_farm": [26, 2], "ic_decision": [27, 4]}.items():
    T[k] = tile([p], B[k], k, aria_hidden=True, cls="tile ea-cicon")
for k, ps in {"act1": [[64], [69]], "act2": [[65], [68]], "act3": [[66], [77]], "act4": [[67], [70]]}.items():
    T[k] = tile(ps, B[k], k, aria_hidden=True, cls="tile ea-acticon")
# value cards: card + title + text + the underline that continues to the compass (shown only on wide screens)
for k, ps in {"vTL": [[28], [37], [33], [42]], "vBL": [[29], [38], [34], [43]], "vTR": [[30], [40], [35], [44]], "vBR": [[31], [39], [36], [45]]}.items():
    T[k] = tile(ps, B[k], k, pad=0, cls="tile ea-vcard", card_rects=True)
# take action, wide screens: paths, circles, icons and text in the original arrangement
T["action"] = tile([[50]] + R(52, 62) + R(64, 70) + [[77]], B["action"], "action", pad=2, cls="tile ea-action-wide")


def pos(key, box=None):
    x, y, w, h = box or T[key][1]
    return f"--x:{x:.1f};--y:{y:.1f};--w:{w:.1f};--h:{h:.1f}"


def svg(key, extra=""):
    s = T[key][0]
    return s.replace('<svg class="', f'<svg {extra}class="', 1) if extra else s


def decision_phone():
    W, cx, R = 414, 207, 190
    y0, k = 300, 6.0                        # y of 1920, units per year
    Y = lambda yr: y0 + (yr - 1920) * k
    xl, xr = cx - 24, cx + 24               # poor / good rails
    poor = [((1933, 1939), ["Failure to act against", "early signs of WWII"]),
            ((1953, 1966), ["Widespread use of", "leaded gasoline"]),
            ((2003, 2003), ["Invasion of Iraq based", "on faulty intelligence"], "last"),
            ((2008, 2008), ["Lack of oversight", "leads to financial", "crisis"]),
            ((2020, 2020), ["Slow global response", "to COVID-19"])]
    good = [((1948, 1948), ["Universal Declaration", "of Human Rights"]),
            ((1987, 1987), ["Montreal Protocol to", "protect the ozone layer"]),
            ((2000, 2000), ["Rollout of global", "vaccination campaigns"]),
            ((2015, 2015), ["Paris Agreement on", "climate change"]),
            ((2022, 2022), ["International efforts", "to contain monkeypox"])]
    LH, F = 17.2, 14
    end = Y(2026)
    o = [f'<circle cx="{cx}" cy="{R}" r="{R}" fill="#0c869b" fill-opacity=".2"/>',
         f'<text x="{cx}" y="{R - 30}" text-anchor="middle" font-size="{F}" font-weight="700" fill="#0c869b">'
         f'<tspan x="{cx}">An average US politician can</tspan><tspan x="{cx}" dy="{LH}">influence 10,000 citizens</tspan></text>',
         f'<circle cx="{cx}" cy="{R}" r="{R / 100:.2f}" fill="#0c869b"/>',
         # stem from the dot, then the brace splitting into the two rails
         f'<path d="M{cx},{R + 4}V{y0 - 62}c0,10-8,14-16,14h0c-6,0-8,4-8,10V{end}M{cx},{y0 - 62}c0,10,8,14,16,14h0c6,0,8,4,8,10V{end}" '
         f'fill="none" stroke="#333" stroke-width="1.2"/>',
         f'<text x="{xl - 12}" y="{y0 - 38}" text-anchor="end" font-size="{F}" font-style="italic" fill="#000">Poor decision-making</text>',
         f'<text x="{xr + 12}" y="{y0 - 38}" font-size="{F}" font-style="italic" fill="#000">Good decision-making</text>']
    for yr in range(1920, 2021, 20):
        o.append(f'<text x="{cx}" y="{Y(yr) + 5}" text-anchor="middle" font-size="{F}" fill="#333">{yr}</text>')

    def side(events, x, anchor, tx):
        last = -1e9
        for (a, b), lines, *opt in events:
            ya, yb = Y(a) - 5, Y(b) + 5      # a marker is a 10-unit pill; a span is a longer one
            o.append(f'<rect x="{x - 5.2}" y="{ya:.1f}" width="10.4" height="{yb - ya:.1f}" rx="5.2" fill="#000"/>')
            top = (ya + yb) / 2 - LH / 2 + 4                     # first line level with the marker...
            if opt == ["last"]:
                top -= LH * (len(lines) - 1)                         # ...or the last line, for a label sitting above it
            top = max(top, last + 6)                                 # no overlaps
            o.append(f'<text x="{tx}" y="{top + 9:.1f}" text-anchor="{anchor}" font-size="{F}" fill="#333">'
                     + "".join(f'<tspan x="{tx}" dy="{0 if i == 0 else LH}">{t}</tspan>' for i, t in enumerate(lines)) + "</text>")
            last = top + LH * len(lines)
    side(poor, xl, "end", xl - 12)
    side(good, xr, "start", xr + 12)
    H = end + 6
    return (f'<svg class="tile chart pd-m" viewBox="0 0 {W} {H:.0f}" style="--tw:{W};--th:{H:.0f}" role="img" focusable="false">'
            f'<title>{html.escape(T["decision"][0].split("<title>")[1].split("</title>")[0], quote=False)}</title>'
            f'<g font-family="Merriweather, serif">{"".join(o)}</g></svg>')


def icons(sym, n, cls):
    return f'<span class="pg {cls}" style="--n:{n}">' + "".join(f'<svg aria-hidden="true"><use href="#ea-{sym}"/></svg>' for _ in range(n)) + "</span>"


def grid(sym, n, cols, cls):
    return f'<span class="pg {cls}" style="--cols:{cols}">' + "".join(f'<svg aria-hidden="true"><use href="#ea-{sym}"/></svg>' for _ in range(n)) + "</span>"


def timeline(items):
    lis = []
    for year, paras, kind in items:
        ps = "".join(f"<p>{p}</p>" for p in ([paras] if isinstance(paras, str) else paras))
        lis.append(f'<li class="{kind}"><span class="yr">{year}</span>{ps}</li>')
    return '<ol class="ea-tl">' + "".join(lis) + "</ol>"


def cause(title, icon, why, viz, sr_viz, done):
    return f'''<article class="ea-cause reveal">
  <header><h3>{title}</h3>{svg(icon)}</header>
  <h4>Why this issue?</h4>
  <p>{why}</p>
  <div class="ea-viz">{viz}<p class="sr">{sr_viz}</p></div>
  <h4>What’s been done</h4>
  {timeline(done)}
</article>'''


pandemic = cause("Preventing the next pandemic", "ic_pandemic",
    "Pandemics cause many more deaths than terrorism. Yet, pandemic prevention gets much less funding than counterterrorism.",
    f'''<div class="pc" aria-hidden="true">
      <p class="lab dark c1 r1">500,000 deaths from terrorism from 1970 to 2020</p>{grid("skull", 1, 1, "dark c1 r2")}
      {grid("skull", 42, 7, "teal c1 r3")}<p class="lab teal c1 r4">21,000,000 deaths due to COVID-19 from 2020 to 2022</p><hr class="viz-sep">
      <p class="lab dark c2 r1">Annual US expense on counterterrorism: $280 billion</p>{grid("dollar", 35, 7, "dark c2 r2")}
      {grid("dollar", 1, 1, "teal c2 r3")}<p class="lab teal c2 r4">Annual US expense to prevent pandemics: $8 billion</p>
    </div>''',
    "Each skull stands for 500,000 deaths: 1 for terrorism from 1970 to 2020, 42 for COVID-19 from 2020 to 2022. Each coin stands for $8 billion a year: 35 for US counterterrorism, 1 for US pandemic prevention.",
    [("2016", "Coefficient Giving funded Johns Hopkins Center for Health Security", "dot"),
     ("2020", "1DaySooner gathered 30,000+ volunteers for human challenge trials", "dot"),
     ("2021", "Creation of Apollo Programme for Biodefense (multibillion-dollar policy proposal)", "dot")])

farming = cause("Ending factory farming", "ic_farm",
    "Countless animals live and die in factory farms in miserable conditions. Far fewer animals pass through pet shelters, but far less is spent on ending factory farming than on pet shelters.",
    f'''<div class="pf" aria-hidden="true">
      <p class="lab teal f-l1">7 million animals in US shelters per year</p><span class="dot f-d1"></span>
      <p class="lab dark f-l2">10 billion animals in US factory farms per year</p><div class="f-circle">{svg("animals")}</div>
      <hr class="viz-sep">{grid("dollar", 50, 10, "teal f-g1")}<p class="lab teal f-l3">$5 billion spent on US animal rescue shelters in 2018</p>
      {grid("dollar", 1, 1, "dark f-g2")}<p class="lab dark f-l4">$100 million spent on US animal advocacy in 2018</p>
    </div>''',
    "A small dot for the 7 million animals in US shelters each year next to a large circle of farm animals for the 10 billion in US factory farms. Coins of $100 million each: 50 for US animal rescue shelters in 2018, 1 for US animal advocacy.",
    [("2011", "Coefficient Giving was an early investor in Impossible Foods, which created a vegan burger that tastes like meat", "dot"),
     ("2016", ["The Open Wing Alliance secured 2,200+ corporate commitments to cage-free eggs, sparing 100+ million birds from cages",
               "The Good Food Institute helped create alternative protein companies, securing tens of millions in government support"], "ongoing two")])

needs = cause("Providing for basic needs in poor countries", "ic_needs",
    "Global inequality is extreme. Transferring resources to the very poorest people in the world can do a huge amount of good, compared to using the same money in richer countries like the US and the UK.",
    f'''<div class="pn">
      <div class="n-chart">{svg("income")}</div><hr class="viz-sep">
      <div class="n-people" aria-hidden="true">
        <p class="lab dark">1 life saved per $1 million spent by the UK’s NHS at the margin</p>{grid("person", 1, 1, "dark")}
        {grid("person", 180, 18, "teal")}<p class="lab teal">180 lives saved per $1 million donated to the top GiveWell charities</p>
      </div>
    </div>''',
    "Each figure stands for one life saved per $1 million: 1 by the UK’s NHS at the margin, 180 through the top GiveWell charities.",
    [("2007", "$1 billion+ directed to effective charities through GiveWell", "ongoing"),
     ("2018", "Wave money transfer service used by over 800,000 people; saved hundreds of millions in transfer fees for African countries (in Senegal, the equivalent of 1% of GDP)", "ongoing second")])

ai = cause("Helping to create the field of AI alignment research", "ic_ai",
    "AI is advancing rapidly, but little effort is spent ensuring it aligns with human values. Failing to align superintelligent AIs could cause a global catastrophe.",
    f'''<div class="pa">
      <div class="a-chart">{svg("ai")}</div>
      <div class="a-chart-phone" aria-hidden="true">{svg("ai_m")}</div><hr class="viz-sep">
      <div class="a-people" aria-hidden="true">
        <div>{grid("person", 133, 27, "dark")}<p class="lab dark">40,000 researchers working on increasing AI capabilities in 2020</p></div>
        <div>{grid("person", 1, 1, "teal")}<p class="lab teal">300 researchers working on AI alignment in 2020</p></div>
      </div>
    </div>''',
    "Each figure stands for 300 researchers in 2020: 133 working on increasing AI capabilities (40,000 people), 1 working on AI alignment (300 people).",
    [("2014", "Publication of \"Superintelligence\" (New York Times bestseller), informing people on the importance of AI alignment", "dot"),
     ("2016", ["Creation of Center for Human-Compatible AI at UC Berkeley, aiming to further human values in the development of AI",
               "Development of the research agenda \"Concrete Problems in AI Safety\""], "dot")])

decision = cause("Improving decision-making", "ic_decision",
    "Better decision-making by key actors—governments, businesses, and funders—could improve responses to major global issues, from pandemics to climate change.",
    f'''<div class="pd">{svg("decision")}</div><div class="pd-phone">{decision_phone()}</div>''', "",
    [("2014", "The Global Priorities Institute does research on how decision-makers can identify the world’s most pressing problems; it has inspired research at major universities including Harvard, Princeton, and Yale", "ongoing"),
     ("2022", "Metaculus platform accurately predicted the invasion of Ukraine by aggregating forecasts", "dot")])


VCARDS = [("tl", "Prioritization", "Our intuitions don’t do a good job at estimating the scale of our impact, so we use numbers to weigh how much different actions help.", 0),
          ("tr", "Open truthseeking", "We consider many different ways to help, staying open to new evidence and arguments. We are ready to change our views quite radically.", 1),
          ("bl", "Impartial altruism", "We aim to weigh everyone’s interests equally when trying to do good. This leads to focusing on groups that are the most neglected.", 3),
          ("br", "Collaborative spirit", "We can achieve more by working together. To do this effectively, we have high standards of honesty, integrity, and compassion.", 4)]
vcards_m = "".join(f'<div class="vcard-m vm-{k} reveal" style="--i:{i}"><h4>{t}</h4><span class="vd"></span><p>{d}</p></div>' for k, t, d, i in VCARDS)

ACT = [("act1", "Career", "choose a career or use your existing skills to tackle pressing problems."),
       ("act2", "Starting new organizations", "that help to tackle pressing problems."),
       ("act3", "Effective donations", "donate to carefully chosen charities, such as by using research from GiveWell or Giving What We Can."),
       ("act4", "Community building", "help to build communities tackling pressing problems.")]
act_list = "".join(f'<li class="reveal" style="--i:{i + 1}">{svg(k)}<div><h4>{t}</h4><p>{d}</p></div></li>' for i, (k, t, d) in enumerate(ACT))

L = lambda href, text: f'<a href="https://{href}" rel="noopener" target="_blank">{text}</a>'
figure = f'''<figure class="ea" aria-labelledby="ea-title">
  <svg class="ea-defs" aria-hidden="true" focusable="false">{symbols}</svg>
  <h2 id="ea-title" class="ea-title reveal">What is effective altruism?</h2>
  <div class="ea-intro">
    <div class="ea-at i-l reveal" style="--i:1;{pos("cardL")}"><div class="wide-only">{svg("cardL")}</div><div class="phone-only">{svg("cardLm")}</div></div>
    <div class="ea-at i-bulb reveal" style="--i:0;{pos("bulb")}">{svg("bulb")}</div>
    <div class="ea-at i-r reveal" style="--i:2;{pos("cardR")}"><div class="wide-only">{svg("cardR")}</div><div class="phone-only">{svg("cardRm")}</div></div>
  </div>
  <h2 class="ea-h reveal">Examples of effective altruism in practice</h2>
  <div class="ea-causes">
    <div class="ea-col">{pandemic}{needs}{ai}</div>
    <div class="ea-col">{farming}{decision}</div>
  </div>
  <h2 class="ea-h reveal">What values unite effective altruism?</h2>
  <div class="ea-values">
    <div class="ea-at v-compass reveal" style="--i:2;{pos("compass")}">{svg("compass")}</div>
    <div class="ea-at v-tl reveal" style="--i:0;{pos("vTL")}">{svg("vTL")}</div>
    <div class="ea-at v-bl reveal" style="--i:3;{pos("vBL")}">{svg("vBL")}</div>
    <div class="ea-at v-tr reveal" style="--i:1;{pos("vTR")}">{svg("vTR")}</div>
    <div class="ea-at v-br reveal" style="--i:4;{pos("vBR")}">{svg("vBR")}</div>
    {vcards_m}
  </div>
  <h2 class="ea-h reveal">How can you take action?</h2>
  <div class="ea-action">
    <div class="ea-at a-wide reveal" style="--i:1;{pos("action")}">{svg("action")}</div>
    <div class="ea-at a-woman reveal" style="--i:0;{pos("woman")}">{svg("woman")}</div>
    <ul class="a-list">{act_list}</ul>
  </div>
  <h2 class="ea-h reveal">Learn more</h2>
  <div class="ea-more reveal">
    <p>Read the full post at {L("www.effectivealtruism.org/articles/introduction-to-effective-altruism", "www.effectivealtruism.org/articles/introduction-to-effective-altruism")}</p>
    <p>Discover effective altruism on the official website {L("www.effectivealtruism.org", "www.effectivealtruism.org")} or on the forum {L("forum.effectivealtruism.org", "forum.effectivealtruism.org")}</p>
    <p class="ea-credit">Designed by Martina Pepiciello <a href="https://www.martinapepiciello.com/">www.martinapepiciello.com</a> – CC BY 4.0</p>
  </div>
</figure>'''
# the source artwork ends this sentence at "do"; give it its last word (rewrapped so it stays inside the card)
figure = figure.replace('United by a way of thinking: </tspan><tspan x="0" y="20">finding unusually good ways to do </tspan>',
                        'United by a way of thinking: finding</tspan><tspan x="0" y="20">unusually good ways to do good</tspan>')
assert "ways to do good<" in figure
open(OUT, "w", encoding="utf-8", newline="\n").write(figure)
print("wrote", OUT, f"{len(figure) // 1024} KB")

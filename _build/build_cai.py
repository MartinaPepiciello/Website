"""Build the Constitutional AI infographic as HTML: symbols from Martina's SVG + positioned nodes + connector data.
Writes cai_figure.html (the <figure> markup) next to this script; build.py inserts it into the project page."""
import copy, html, json, os, re, sys
import xml.etree.ElementTree as ET

SRC = sys.argv[1]           # original cai.svg
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cai_figure.html")
NS = "{http://www.w3.org/2000/svg}"
ET.register_namespace("", "http://www.w3.org/2000/svg")
root = ET.parse(SRC).getroot()

# --- class -> inline style -------------------------------------------------------------------------------------
css = "".join(root.find(f"{NS}defs/{NS}style").itertext())
styles = {}
for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", css):
    decls = [d.strip() for d in body.split(";") if d.strip() and not d.strip().startswith("font")]
    for c in re.findall(r"\.(cls-\d+)", sel):
        styles.setdefault(c, []).extend(decls)

layer = [k for k in root.iter(f"{NS}g") if k.get("id") == "Layer_2"][0]
kids = list(layer)


def inline(el):
    for e in el.iter():
        cls = e.get("class")
        if cls:
            e.set("style", ";".join(styles.get(cls, [])))
            del e.attrib["class"]
        for a in ("data-name",):
            e.attrib.pop(a, None)


def symbol(idx, sid, box, pad=3):
    g = copy.deepcopy(kids[idx])
    for parent in g.iter():
        for ch in list(parent):
            if ch.tag == f"{NS}text" or "display: none" in ";".join(styles.get(ch.get("class", ""), [])):
                parent.remove(ch)
    inline(g)
    x, y, w, h = box
    inner = "".join(ET.tostring(ch, encoding="unicode") for ch in g)
    inner = re.sub(r'\s+xmlns(:\w+)?="[^"]+"', "", inner)
    return f'<symbol id="{sid}" viewBox="{x - pad:.1f} {y - pad:.1f} {w + 2 * pad:.1f} {h + 2 * pad:.1f}">{inner}</symbol>'


# representative instances (bbox from the browser measurement of the original file)
SYMS = {
    "llm-helpful":    (5,  (304.1, 334.6, 169.2, 217.1)),
    "llm-finetuned":  (16, (261.3, 1603.2, 191.4, 223.3)),
    "llm-preference": (25, (625.4, 2290.6, 171.2, 200.9)),
    "llm-aligned":    (27, (1102.4, 2414.3, 156.9, 200.9)),
    "book":           (9,  (196.5, 610.2, 149.6, 191.8)),
    "cycle":          (15, (346.4, 2335.7, 201, 201)),
    "repeat":         (13, (1133.4, 783.7, 130.4, 50.6)),
}
PAD = 3
symbols = "".join(symbol(i, "cai-" + k, b, PAD) for k, (i, b) in SYMS.items())

# --- nodes --------------------------------------------------------------------------------------------------------
# sym nodes: (id, symbol, bbox x, y, body rect x, y, w, h, [(lines, cx, cy, size)], mobile area)
# css nodes: (id, kind, rect x, y, w, h, lines, tail, mobile area)
U = lambda v: f"{v:.1f}"


def sym_node(nid, sym, x, y, body, texts, area):
    bx, by, bw, bh = SYMS[sym][1]
    ox, oy = x - PAD, y - PAD                      # node top-left in original units
    w, h = bw + 2 * PAD, bh + 2 * PAD
    lbls = "".join(
        f'<span class="lbl" style="--x:{U(cx - ox)};--y:{U(cy - oy)};--fs:{size}">{"<br>".join(map(html.escape, lines))}</span>'
        for lines, cx, cy, size in texts)
    b = body or (x, y, bw, bh)
    return (f'<div class="node sym" data-node="{nid}" data-body="{U(b[0] - ox)},{U(b[1] - oy)},{U(b[2])},{U(b[3])}" '
            f'style="--x:{U(ox)};--y:{U(oy)};--w:{U(w)};--h:{U(h)};--a:{area}">'
            f'<svg aria-hidden="true" focusable="false"><use href="#cai-{sym}"/></svg>{lbls}</div>')


def css_node(nid, kind, x, y, w, h, lines, area, tail=""):
    return (f'<div class="node {kind}{" tail-" + tail if tail else ""}" data-node="{nid}" '
            f'style="--x:{U(x)};--y:{U(y)};--w:{U(w)};--h:{U(h)};--a:{area}">'
            f'<span class="txt">{"<br>".join(map(html.escape, lines))}</span></div>')


def loop(nid, x, y, w, h, rx, ry):
    # repeat badge sits flush in the loop box's bottom-right corner
    return (f'<div class="loop" data-node="{nid}" style="--x:{U(x)};--y:{U(y)};--w:{U(w)};--h:{U(h)}">'
            f'<div class="repeat"><svg aria-hidden="true" focusable="false"><use href="#cai-repeat"/></svg><span>REPEAT</span></div></div>')


# Phase 1 flow (original y from 287)
Y1 = 287
p1 = [
    loop("loop1", 16.4, 302.4, 1247.5, 532, 0, 0),
    css_node("prompt", "bubble light", 59.9, 443.7, 149.3, 108, ["harmful", "prompt"], "prompt", "r"),
    sym_node("llm1", "llm-helpful", 304.1, 334.6, (304.1, 443.7, 128, 108), [(["helpful", "LLM"], 368.8, 496.7, 24)], "llm1"),
    css_node("toxic", "bubble mid", 521.4, 443.7, 149.3, 108, ["toxic", "response"], "toxic", "l"),
    sym_node("llm2", "llm-helpful", 848.8, 334.6, (848.8, 443.7, 128, 108), [(["helpful", "LLM"], 913.6, 496.7, 24)], "llm2"),
    css_node("revised", "bubble mid", 1066.1, 443.7, 149.3, 108, ["revised", "response"], "revised", "l"),
    sym_node("book", "book", 196.5, 610.2, None, [(["constitution"], 271.3, 664.9, 24), (["harmlessness", "principles"], 271.3, 727, 18)], "book"),
    css_node("critique", "bubble light", 442.4, 652.1, 307.3, 108, ["“critique, then revise the", "response according to", "a random principle”"], "critique", "r"),
    css_node("docs", "docs", 391.5, 936.3, 258.4, 124.6, ["set of finetuned", "responses"], "docs"),
    sym_node("llmh", "llm-helpful", 456.6, 1113.9, (456.6, 1223, 128, 108), [(["helpful", "LLM"], 521.4, 1276.1, 24)], "llmh"),
    sym_node("sl", "cycle", 749.8, 1033.8, None, [(["supervised", "learning"], 850.7, 1137, 24)], "sl"),
    sym_node("ft", "llm-finetuned", 1003.2, 987.7, (1045.3, 1080.5, 128, 108), [(["finetuned", "LLM"], 1108.5, 1133.4, 24)], "ft"),
]
links1 = "prompt>llm1,llm1>toxic,toxic>llm2,llm2>revised,book>critique,critique>llm2,loop1>docs,docs>sl,llmh>sl,sl>ft"
H1 = 1345 - Y1

# Phase 2 flow (original y from 1541)
Y2 = 1541
p2 = [
    loop("loop2", 16.4, 1556.6, 1247.5, 532, 0, 0),
    css_node("prompt", "bubble light", 59.9, 1695.9, 149.3, 108, ["harmful", "prompt"], "prompt", "r"),
    sym_node("ft1", "llm-finetuned", 261.3, 1603.2, (303.4, 1696, 128, 108), [(["finetuned", "LLM"], 366.6, 1749, 24)], "ft1"),
    css_node("r1", "bubble mid", 532.3, 1668.8, 149.3, 60.5, ["response 1"], "r1", "l"),
    css_node("r2", "bubble mid", 532.3, 1771, 149.3, 60.5, ["response 2"], "r2", "l"),
    sym_node("ft2", "llm-finetuned", 811.0, 1603.2, (853.1, 1696, 128, 108), [(["finetuned", "LLM"], 916.2, 1749, 24)], "ft2"),
    css_node("labels", "labels", 1069, 1695.9, 146.5, 107.7, ["preference", "labels"], "labels"),
    sym_node("book", "book", 205, 1869.5, None, [(["constitution"], 279.7, 1924.2, 24), (["harmlessness", "principles"], 279.7, 1986.3, 18)], "book"),
    css_node("q", "bubble light", 450.3, 1911.4, 307.3, 108, ["“which response is", "better, according to", "a random principle?”"], "q", "r"),
    css_node("ds1", "docs", 16.4, 2187.9, 258.3, 124.6, ["AI-generated", "harmlessness", "dataset"], "ds1"),
    css_node("ds2", "docs", 16.4, 2373.9, 258.3, 124.6, ["human-generated", "helpfulness", "dataset"], "ds2"),
    sym_node("llmh", "llm-helpful", 81.6, 2538.5, (81.6, 2647.6, 128, 108), [(["helpful", "LLM"], 146.3, 2700.6, 24)], "llmh"),
    sym_node("sl", "cycle", 346.4, 2335.7, None, [(["supervised", "learning"], 447.3, 2438.3, 24)], "sl"),
    sym_node("pm", "llm-preference", 625.4, 2290.6, (625.4, 2383.5, 128, 108), [(["preference", "model"], 689.6, 2436.5, 24)], "pm"),
    sym_node("ft3", "llm-finetuned", 583.2, 2525.6, (625.3, 2618.2, 128, 108), [(["finetuned", "LLM"], 688.5, 2671.3, 24)], "ft3"),
    sym_node("rl", "cycle", 828.4, 2455.7, None, [(["reinforcement", "learning"], 929.5, 2564.3, 24)], "rl"),
    sym_node("al", "llm-aligned", 1102.4, 2414.3, (1102.4, 2507.2, 128, 108), [(["RLAIF", "aligned", "LLM"], 1166.5, 2561.3, 24)], "al"),
]
links2 = ("prompt>ft1,ft1>r1,ft1>r2,r1>ft2,r2>ft2,book>q,q>ft2,ft2>labels,"
          "loop2>ds1,ds1>sl,ds2>sl,llmh>sl,sl>pm,pm>rl,ft3>rl,rl>al")
H2 = 2775 - Y2


# narrow (phone) layout: positions, line breaks and arrows from Martina's edited mobile SVG (cai_mobile_from_svg.py)
MOBILE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cai_mobile.json"), encoding="utf-8"))["flows"]


def dual_breaks(desk, mob):
    """same words, two sets of line breaks: <br> where both break, br.bd on desktop only, br.bm on phones only"""
    dw = [w for l in desk for w in l.split()]
    mw = [w for l in mob for w in l.split()]
    assert dw == mw, (dw, mw)

    def ends(ls):
        out, n = set(), 0
        for l in ls[:-1]:
            n += len(l.split()); out.add(n)
        return out
    de, me = ends(desk), ends(mob)
    out = html.escape(dw[0])
    for i, w in enumerate(dw[1:], 1):
        out += "<br>" if i in de and i in me else ' <br class="bd">' if i in de else ' <br class="bm">' if i in me else " "
        out += html.escape(w)
    return out


def flow(ph, cls, nodes, y0, h, links, summary):
    M = MOBILE[str(ph)]
    shifted = []
    for i, n in enumerate(nodes):
        # --y in the markup is absolute; shift to the flow's origin
        n = re.sub(r"--y:([\d.]+)", lambda m: f"--y:{float(m.group(1)) - y0:.1f}", n, count=1)
        nid = re.search(r'data-node="([^"]+)"', n).group(1)
        mb = M["nodes"][nid]
        x, y, w, hh = mb["box"]
        # --i: entrance order on desktop; --nx/--ny/--nw/--nh: the box on phones
        n = n.replace('style="--x', f'style="--i:{i};--nx:{x};--ny:{y};--nw:{w};--nh:{hh};--x', 1)
        n = n.replace('class="node ', 'class="reveal node ', 1).replace('class="loop"', 'class="reveal loop"', 1)
        if mb["kind"] in ("bubble", "card"):
            m = re.search(r'<span class="txt">(.*?)</span>', n)
            desk = [html.unescape(t) for t in m.group(1).split("<br>")]
            n = n.replace(m.group(0), f'<span class="txt">{dual_breaks(desk, mb["lines"])}</span>')
        elif mb["kind"] == "sym":
            for lb in re.findall(r'<span class="lbl"[^>]*>(.*?)</span>', n):
                ls = [html.unescape(t) for t in lb.split("<br>")]
                assert ls in mb["lines"].values(), (nid, ls, mb["lines"])
        shifted.append("      " + n)
    # phone arrows exactly as drawn in the mobile SVG; each path + head fades in as it scrolls into view
    shapes = M["arrows"]
    pairs = [shapes[k:k + 2] for k in range(0, len(shapes), 2)]
    assert all(a.startswith("<path") and b.startswith("<polygon") for a, b in pairs)
    arrows = "".join(f'<g class="reveal arw-m">{a}{b}</g>' for a, b in pairs)
    links_m = f'<svg class="links-m" aria-hidden="true" focusable="false" viewBox="0 0 560 {M["h"]}"><g transform="translate(0 {-M["top"]})">{arrows}</g></svg>'
    return (f'    <div class="flow {cls}" style="--fh:{h};--nfh:{M["h"]}" data-links="{links}">\n'
            f'      <p class="sr">{summary}</p>\n      {links_m}\n' + "\n".join(shifted) + "\n    </div>")


S1 = ("Phase 1, supervised learning. A harmful prompt goes to a helpful LLM, which gives a toxic response. "
      "The helpful LLM is then asked, using a random principle from a constitution of harmlessness principles, "
      "to critique and revise the response, producing a revised response. This repeats. The set of finetuned responses "
      "and the helpful LLM go through supervised learning, giving a finetuned LLM.")
S2 = ("Phase 2, reinforcement learning. A harmful prompt goes to the finetuned LLM, which gives two responses. "
      "The finetuned LLM is asked which response is better according to a random principle of the constitution, "
      "producing preference labels. This repeats. The AI-generated harmlessness dataset, a human-generated helpfulness "
      "dataset and the helpful LLM go through supervised learning, giving a preference model. The preference model and "
      "the finetuned LLM go through reinforcement learning, giving an RLAIF-aligned LLM.")

figure = f'''<figure class="cai" aria-labelledby="cai-title">
  <svg class="cai-defs" aria-hidden="true" focusable="false">{symbols}</svg>
  <div class="cai-title reveal"><h2 id="cai-title">Constitutional AI training process</h2></div>
  <section class="cai-phase">
    <div class="cai-band reveal"><h3>Phase 1: Supervised Learning</h3><p>The model learns to identify its own harmful responses.</p></div>
{flow(1, "flow-p1", p1, Y1, H1, links1, S1)}
  </section>
  <section class="cai-phase">
    <div class="cai-band reveal"><h3>Phase 2: Reinforcement Learning</h3><p>The model learns to prioritize helpful and harmless responses.</p></div>
{flow(2, "flow-p2", p2, Y2, H2, links2, S2)}
  </section>
</figure>'''
open(OUT, "w", encoding="utf-8", newline="\n").write(figure)
print("wrote", OUT, len(figure), "bytes")

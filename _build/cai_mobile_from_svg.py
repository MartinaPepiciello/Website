"""Turn the measured mobile-layout SVG (measure_svg.py output) into the data build_cai.py needs for the narrow layout:
node boxes relative to each flow, the line breaks of each text, the flow heights and the arrows as SVG markup.
usage: cai_mobile_from_svg.py measured.json out.json"""
import json, sys

M = json.load(open(sys.argv[1], encoding="utf-8"))
G = M["groups"]
PAD = 3
BUBBLES = {"prompt", "toxic", "revised", "critique", "r1", "r2", "q"}
SAME_H = {"r2": 60.5}   # stretched by accident in the edit; match response 1
BAND_GAP = 14                                     # band bottom -> flow top, as in the exported layout


def union(bbs):
    x0 = min(b[0] for b in bbs); y0 = min(b[1] for b in bbs)
    x1 = max(b[0] + b[2] for b in bbs); y1 = max(b[1] + b[3] for b in bbs)
    return [x0, y0, x1 - x0, y1 - y0]


def lines(texts, fs=None):
    """text pieces -> lines (top to bottom), pieces on the same baseline joined"""
    ts = [t for t in texts if fs is None or abs(t["fs"] - fs) < .5]
    rows = []
    for t in sorted(ts, key=lambda t: (round(t["bb"][1]), t["bb"][0])):
        if rows and abs(rows[-1][0] - t["bb"][1]) < 4: rows[-1][1].append(t)
        else: rows.append([t["bb"][1], [t]])
    return [" ".join(p["t"].strip() for p in sorted(r[1], key=lambda p: p["bb"][0])) for r in rows]


band1, band2 = G["phase1-band"]["bb"], G["phase2-band"]["bb"]
flows = {1: band1[1] + band1[3] + BAND_GAP, 2: band2[1] + band2[3] + BAND_GAP}
heights = {1: band2[1] - flows[1], 2: M["H"] - flows[2]}

out = {"flows": {}}
for ph in (1, 2):
    top = flows[ph]
    nodes = {}
    for gid, g in G.items():
        if not gid.startswith(f"phase{ph}-") or gid.endswith(("-band", "-arrows")): continue
        nid = gid.split("-", 1)[1]
        shapes = [s for s in g["shapes"]]
        if nid.startswith("loop"):
            frame = max(shapes, key=lambda s: s["bb"][2] * s["bb"][3])["bb"]   # stroked frame, stroke centred on it
            box = [frame[0] - 2.5, frame[1] - 2.5, frame[2] + 5, frame[3] + 5]
            nodes[nid] = {"box": box, "kind": "loop"}
            continue
        kind = "bubble" if nid in BUBBLES else None
        if kind == "bubble":
            rect = max(shapes, key=lambda s: s["bb"][2] * s["bb"][3])["bb"]
            if nid in SAME_H: rect = rect[:3] + [SAME_H[nid]]   # keep paired bubbles the same height
            n = {"kind": "bubble", "box": rect, "lines": lines(g["texts"])}
        elif nid.startswith(("docs", "ds", "labels")):
            card = union([s["bb"] for s in shapes])
            n = {"kind": "card", "box": card, "lines": lines(g["texts"])}
        else:                                                            # artwork node: box = artwork bbox + pad
            art = union([s["bb"] for s in shapes])
            n = {"kind": "sym", "box": [art[0] - PAD, art[1] - PAD, art[2] + 2 * PAD, art[3] + 2 * PAD],
                 "art": art, "lines": {fs: lines(g["texts"], fs) for fs in sorted({t["fs"] for t in g["texts"]})}}
        nodes[nid] = n
    for n in nodes.values():
        n["box"] = [round(n["box"][0], 1), round(n["box"][1] - top, 1), round(n["box"][2], 1), round(n["box"][3], 1)]
    # arrows, relative to the flow
    arrows = []
    for s in G[f"phase{ph}-arrows"]["shapes"]:
        assert s["m"] == [1, 0, 0, 1, 0, 0], s["m"]
        if s["tag"] == "path": arrows.append(f'<path d="{s["geo"]}"/>')
        elif s["tag"] == "polygon": arrows.append(f'<polygon points="{s["geo"]}"/>')
        elif s["tag"] == "line":
            x1, y1, x2, y2 = s["geo"].split(","); arrows.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
        else: raise ValueError(s["tag"])
    out["flows"][ph] = {"top": round(top, 1), "h": round(heights[ph], 1), "nodes": nodes, "arrows": arrows}
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for ph, f in out["flows"].items():
    print(f"phase {ph}: top {f['top']} h {f['h']}, {len(f['arrows'])} arrow shapes")
    for nid, n in f["nodes"].items(): print("  ", nid, n["kind"], n["box"], n.get("lines"))

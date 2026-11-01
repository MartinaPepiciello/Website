"""Measure an SVG of the CAI mobile layout in headless Chrome: per named group, the boxes of its shapes, its text lines
and (for the arrows groups) every arrow shape with its matrix and resolved style. usage: measure_svg.py in.svg out.json"""
import html, json, os, re, subprocess, sys, tempfile

SRC, OUT = sys.argv[1], sys.argv[2]
svg = re.sub(r"<\?xml[^>]*>", "", open(SRC, encoding="utf-8").read())
JS = r"""
(async () => {
  await document.fonts.ready; await new Promise(r => setTimeout(r, 300));
  const root = document.querySelector('svg'), R0 = root.getBoundingClientRect();
  const vb = root.viewBox.baseVal, k = vb.width / R0.width;
  const rnd = v => Math.round(v * 100) / 100;
  const bb = el => { const b = el.getBoundingClientRect(); return [rnd((b.left - R0.left) * k), rnd((b.top - R0.top) * k), rnd(b.width * k), rnd(b.height * k)]; };
  const out = {W: vb.width, H: vb.height, groups: {}};
  root.querySelectorAll('g[id]').forEach(g => {
    if (!/^(title|phase\d(-.+)?)$/.test(g.id) || /^phase\d$/.test(g.id)) return;
    const shapes = [], texts = [];
    g.querySelectorAll('rect,path,polygon,polyline,line,circle,ellipse').forEach(e => {
      if (e.closest('text')) return;
      const s = getComputedStyle(e);
      const m = e.getCTM(), rm = root.getCTM();
      const M = rm.inverse().multiply(m);
      shapes.push({tag: e.tagName, bb: bb(e), fill: s.fill, stroke: s.stroke, sw: parseFloat(s.strokeWidth),
                   fop: s.fillOpacity, inArt: !!e.closest('g[data-name="artwork"]'),
                   m: [M.a, M.b, M.c, M.d, M.e, M.f].map(v => rnd(v)),
                   geo: e.tagName === 'path' ? e.getAttribute('d') : e.tagName === 'polygon' || e.tagName === 'polyline' ? e.getAttribute('points')
                        : e.tagName === 'line' ? ['x1','y1','x2','y2'].map(a => e.getAttribute(a)).join(',')
                        : e.tagName === 'rect' ? ['x','y','width','height','rx'].map(a => e.getAttribute(a) || 0).join(',') : ''});
    });
    g.querySelectorAll('text').forEach(t => {
      const s = getComputedStyle(t);
      const spans = t.querySelectorAll('tspan');
      (spans.length ? [...spans] : [t]).forEach(sp => {
        const str = sp.textContent; if (!str.trim()) return;
        texts.push({t: str, bb: bb(sp), fs: parseFloat(getComputedStyle(sp).fontSize), fw: getComputedStyle(sp).fontWeight});
      });
    });
    out.groups[g.id] = {bb: bb(g), shapes, texts};
  });
  document.getElementById('out').textContent = JSON.stringify(out);
})();
"""
d = tempfile.mkdtemp(prefix="msvg-")
page = os.path.join(d, "m.html")
open(page, "w", encoding="utf-8").write(
    '<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;700&display=swap" rel="stylesheet">'
    '<style>body{margin:0}svg{display:block;width:560px;height:auto}</style>' + svg + '<pre id="out"></pre><script>' + JS + '</script>')
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={os.path.join(d, 'prof')}",
                      "--virtual-time-budget=10000", "--window-size=600,1000", "--dump-dom", "file:///" + page.replace("\\", "/")],
                     capture_output=True, text=True, encoding="utf-8", timeout=120).stdout
m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
data = json.loads(html.unescape(m.group(1)))
json.dump(data, open(OUT, "w", encoding="utf-8"), indent=1)
print(OUT, len(data["groups"]), "groups", data["W"], "x", data["H"])

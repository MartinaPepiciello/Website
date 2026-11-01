// Reads the Constitutional AI figure's narrow layout (figure 560px wide, so 1 design unit = 1px) out of the live page.
// Runs in a same-origin wrapper page; writes JSON into #out.
async function extract(win, doc) {
  await doc.fonts.ready;
  doc.querySelectorAll('.reveal,.wipe').forEach(e => { e.style.transition = 'none'; e.style.transform = 'none'; e.style.filter = 'none'; e.style.opacity = '1'; });
  await new Promise(r => setTimeout(r, 400));
  win.dispatchEvent(new Event('resize'));
  await new Promise(r => setTimeout(r, 400));
  const fig = doc.querySelector('figure.cai'), F = fig.getBoundingClientRect();
  const R = v => Math.round(v * 10) / 10;
  const box = el => { const b = el.getBoundingClientRect(); return { x: R(b.left - F.left), y: R(b.top - F.top), w: R(b.width), h: R(b.height) }; };
  const cs = (el, p) => win.getComputedStyle(el, p);
  const ctx = doc.createElement('canvas').getContext('2d');
  function lines(el) {
    const words = []; const tw = doc.createTreeWalker(el, 4); let n;
    while ((n = tw.nextNode())) {
      if (n.parentElement.closest('.sr')) continue;
      const re = /\S+/g; let m;
      while ((m = re.exec(n.textContent))) {
        const r = doc.createRange(); r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length);
        const b = r.getBoundingClientRect(); words.push({ t: m[0], l: b.left, r: b.right, top: b.top, b: b.bottom, p: n.parentElement });
      }
    }
    const L = [];
    words.forEach(w => { let ln = L.find(x => Math.abs(x.top - w.top) < 3); if (!ln) { ln = { top: w.top, b: w.b, ws: [], p: w.p }; L.push(ln); } ln.ws.push(w); });
    return L.map(ln => {
      ln.ws.sort((a, b) => a.l - b.l);
      const s = cs(ln.p); ctx.font = `${s.fontWeight} ${s.fontSize} ${s.fontFamily}`;
      const d = ctx.measureText('Hg').fontBoundingBoxDescent;
      const l = ln.ws[0].l, r = ln.ws[ln.ws.length - 1].r;
      return { t: ln.ws.map(w => w.t).join(' '), x: R((l + r) / 2 - F.left), y: R(ln.b - d - F.top), fs: parseFloat(s.fontSize), fw: +s.fontWeight, c: s.color };
    });
  }
  const groups = [], g = (id, items) => groups.push({ id, items });
  const t = fig.querySelector('.cai-title');
  g('title', [{ k: 'rect', ...box(t), fill: cs(t).backgroundColor }, { k: 'text', lines: lines(t) }]);
  fig.querySelectorAll('.cai-phase').forEach((ph, pi) => {
    const P = 'phase' + (pi + 1);
    const band = ph.querySelector('.cai-band');
    g(P + '-band', [{ k: 'rect', ...box(band), fill: cs(band).backgroundColor }, { k: 'text', lines: lines(band) }]);
    const flow = ph.querySelector('.flow');
    flow.querySelectorAll(':scope>.loop,:scope>.node').forEach(nd => {
      const id = P + '-' + nd.dataset.node, b = box(nd), s = cs(nd), items = [];
      if (nd.classList.contains('loop')) {
        items.push({ k: 'rect', x: b.x + 2.5, y: b.y + 2.5, w: b.w - 5, h: b.h - 5, rx: parseFloat(s.borderTopLeftRadius) - 2.5, fill: '#caf3ff', fop: 0.1, stroke: '#1856a0', sw: 5 });
        const rp = nd.querySelector('.repeat');
        items.push({ k: 'sym', s: 'cai-repeat', ...box(rp) }, { k: 'text', lines: lines(rp.querySelector('span')) });
      } else if (nd.classList.contains('bubble')) {
        items.push({ k: 'rect', ...b, rx: parseFloat(s.borderTopLeftRadius), fill: s.backgroundColor });
        const a = cs(nd, '::after'), tw = parseFloat(a.width), th = parseFloat(a.height), right = nd.classList.contains('tail-r');
        const x0 = right ? b.x + b.w - parseFloat(a.right) - tw : b.x + parseFloat(a.left), y0 = b.y + b.h;
        const pts = right ? [[x0, y0], [x0 + tw, y0], [x0 + tw, y0 + th]] : [[x0, y0], [x0 + tw, y0], [x0, y0 + th]];
        items.push({ k: 'poly', name: 'tail', pts: pts.map(p => p.map(R).join(',')).join(' '), fill: s.backgroundColor });
        items.push({ k: 'text', lines: lines(nd) });
      } else if (nd.classList.contains('docs') || nd.classList.contains('labels')) {
        const tx = nd.querySelector('.txt'), tb = box(tx);
        if (nd.classList.contains('docs')) { const bb = cs(nd, '::before'); items.push({ k: 'rect', name: 'back card', x: b.x, y: b.y, w: R(parseFloat(bb.width)), h: R(parseFloat(bb.height)), rx: 8, fill: bb.backgroundColor }); }
        items.push({ k: 'card', ...tb, fill: cs(tx).backgroundColor, corner: cs(tx, '::after').backgroundColor });
        items.push({ k: 'text', lines: lines(tx) });
      } else if (nd.classList.contains('sym')) {
        items.push({ k: 'sym', s: nd.querySelector('use').getAttribute('href').slice(1), ...b });
        nd.querySelectorAll('.lbl').forEach(l => items.push({ k: 'text', lines: lines(l) }));
      }
      g(id, items);
    });
    const links = flow.querySelector('svg.links'), lb = box(links);
    g(P + '-arrows', [...links.children].map(e => e.tagName === 'path'
      ? { k: 'path', d: e.getAttribute('d'), dx: lb.x, dy: lb.y, stroke: '#1856a0', sw: +e.getAttribute('stroke-width') }
      : { k: 'poly', pts: e.getAttribute('points'), dx: lb.x, dy: lb.y, fill: '#1856a0' }));
  });
  return { W: R(F.width), H: R(F.height), groups };
}

/* Arrows for HTML flow diagrams (used by the Constitutional AI infographic).
   Each .flow lists its links in data-links="a>b,b>c" (data-node ids). Arrows are drawn into an SVG overlay from the
   boxes' current positions, so they follow whatever layout CSS gives the nodes (desktop or the narrow grid).
   Routing: boxes side by side -> horizontal (with one bend if they're at different heights);
            boxes stacked     -> vertical.   Several arrows on one side of a box are fanned out.
   A link written "a>b:v" is always vertical (down from a, into the top of b).
   On narrow screens the flow shows its hand-drawn svg.links-m instead, so nothing is drawn here.
   Boxes are measured by layout (offsetLeft/Top), so the entrance animation's transforms don't move the arrows. */
(() => {
  const SVGNS = 'http://www.w3.org/2000/svg';
  // the original chevron arrowhead, tip at 0,0 pointing right (artboard units)
  const HEAD = [[-15.6, 8.4], [-7.2, 0], [-15.6, -8.5], [-8.4, -8.5], [0, 0], [-8.4, 8.4]];

  function unitOf(flow) {
    let p = flow.querySelector(':scope > .u-probe');
    if (!p) {
      p = document.createElement('i');
      p.className = 'u-probe';
      p.style.cssText = 'position:absolute;visibility:hidden;width:calc(1000 * var(--u));height:0';
      flow.appendChild(p);
    }
    return p.getBoundingClientRect().width / 1000;
  }

  function draw(flow) {
    const u = unitOf(flow);
    const fr = { width: flow.offsetWidth, height: flow.offsetHeight };
    const order = {};
    const box = id => {
      const el = flow.querySelector(`[data-node="${id}"]`);
      order[id] = getComputedStyle(el).getPropertyValue('--i').trim() || '0';
      const r = { width: el.offsetWidth, height: el.offsetHeight };
      const ox = el.offsetLeft, oy = el.offsetTop;
      let x = ox, y = oy, w = r.width, h = r.height;
      if (el.dataset.body) {            // the part arrows attach to (e.g. the model box under a robot)
        const [bx, by, bw, bh] = el.dataset.body.split(',').map(Number);
        x += bx * u; y += by * u; w = bw * u; h = bh * u;
      }
      // side arrows meet the body; arrows from above/below stop at the whole node (above the robot's head)
      return { l: x, t: y, r: x + w, b: y + h, cx: x + w / 2, cy: y + h / 2, w, h, ot: oy, ob: oy + r.height };
    };

    const hand = flow.querySelector(':scope > svg.links-m');
    if (hand && getComputedStyle(hand).display !== 'none') return;
    const links = flow.dataset.links.split(',').map(s => { const [ab, opt] = s.trim().split(':'); return [...ab.split('>'), opt]; });
    const ends = new Map();            // "node|side" -> [{link, which}]
    const add = (node, side, item) => { const k = node + '|' + side; (ends.get(k) || ends.set(k, []).get(k)).push(item); };
    const L = links.map(([a, b, opt]) => {
      const A = box(a), B = box(b);
      const xo = A.l < B.r - 2 && B.l < A.r - 2, yo = A.ot < B.ob - 2 && B.ot < A.ob - 2;
      const vertical = opt === 'v' || (xo && !yo);
      const sA = vertical ? (B.cy > A.cy ? 'b' : 't') : (B.cx > A.cx ? 'r' : 'l');
      const sB = { b: 't', t: 'b', r: 'l', l: 'r' }[sA];
      const link = { a, b, A, B, vertical, sA, sB, oA: 0, oB: 0 };
      add(a, sA, { link, end: 'A' });
      add(b, sB, { link, end: 'B' });
      return link;
    });

    // fan out arrows that share a side; a single arrow goes to the middle
    ends.forEach(items => {
      if (items.length < 2) return;
      const it0 = items[0], self = it0.end === 'A' ? it0.link.A : it0.link.B;
      const along = it0.link.vertical ? 'cx' : 'cy';
      const half = (it0.link.vertical ? self.w : self.h) / 2;
      const lim = Math.min(24 * u, half * 0.45), gap = 14 * u;
      items.forEach(i => { const other = i.end === 'A' ? i.link.B : i.link.A; i.nat = Math.max(-lim, Math.min(lim, other[along] - self[along])); });
      items.sort((p, q) => p.nat - q.nat);
      for (let k = 1; k < items.length; k++) items[k].nat = Math.max(items[k].nat, items[k - 1].nat + gap);
      const over = items[items.length - 1].nat - half * 0.8;
      if (over > 0) items.forEach(i => (i.nat -= over));
      items.forEach(i => (i.link['o' + i.end] = i.nat));
    });

    let svg = flow.querySelector(':scope > svg.links');
    if (!svg) { svg = document.createElementNS(SVGNS, 'svg'); svg.setAttribute('class', 'links'); svg.setAttribute('aria-hidden', 'true'); flow.prepend(svg); }
    svg.setAttribute('width', fr.width); svg.setAttribute('height', fr.height);
    svg.replaceChildren();

    const g = 12 * u, sw = 5 * u, back = 5.7 * u;
    L.forEach(k => {
      const { A, B } = k;
      let d, tip, dir;
      if (k.vertical) {
        const down = k.sA === 'b';
        let sx = A.cx + k.oA, tx = B.cx + k.oB;
        // straight drop when the target sits under the source (e.g. the loop box down to the datasets)
        if (!k.oA && B.cx > A.l + 10 && B.cx < A.r - 10) sx = tx;
        const sy = down ? A.ob + g : A.ot - g, ty = down ? B.ot - g : B.ob + g;
        const ey = ty - (down ? back : -back);
        // bend just below the source (keeps the horizontal run in the gap under it), or halfway if that's too close
        const near = sy + (down ? 1 : -1) * 22 * u;
        const my = Math.abs(near - sy) < Math.abs(ty - sy) - 14 * u ? near : (sy + ty) / 2;
        d = Math.abs(sx - tx) < 1 ? `M${sx},${sy}V${ey}` : `M${sx},${sy}V${my}H${tx}V${ey}`;
        tip = [tx, ty]; dir = down ? 90 : -90;
      } else {
        const right = k.sA === 'r';
        let sy = A.cy + k.oA, ty = B.cy + k.oB;
        if (!k.oA && !k.oB && Math.abs(sy - ty) < 3 * u) sy = ty;
        const sx = right ? A.r + g : A.l - g, tx = right ? B.l - g : B.r + g;
        const ex = tx - (right ? back : -back);
        const mx = (sx + tx) / 2;
        d = Math.abs(sy - ty) < 1 ? `M${sx},${sy}H${ex}` : `M${sx},${sy}H${mx}V${ty}H${ex}`;
        tip = [tx, ty]; dir = right ? 0 : 180;
      }
      const grp = document.createElementNS(SVGNS, 'g');
      grp.setAttribute('class', 'arw'); grp.style.setProperty('--i', order[k.b]);   // fades in with the box it points to
      svg.appendChild(grp);
      const p = document.createElementNS(SVGNS, 'path');
      p.setAttribute('d', d);
      p.setAttribute('fill', 'none'); p.setAttribute('stroke', 'var(--blue)'); p.setAttribute('stroke-width', sw);
      grp.appendChild(p);
      const a = dir * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
      const head = document.createElementNS(SVGNS, 'polygon');
      head.setAttribute('points', HEAD.map(([x, y]) => [tip[0] + (x * c - y * s) * u, tip[1] + (x * s + y * c) * u].map(v => v.toFixed(1)).join(',')).join(' '));
      head.setAttribute('fill', 'var(--blue)');
      grp.appendChild(head);
    });
  }

  const flows = [...document.querySelectorAll('.flow[data-links]')];
  if (!flows.length) return;
  const all = () => flows.forEach(draw);
  // arrows start fading in once the flow scrolls into view (same trigger point as the boxes' reveal)
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-on'); io.unobserve(e.target); } }),
                                      { threshold: 0, rootMargin: '0px 0px -8% 0px' });
  flows.forEach(f => io.observe(f));
  const ro = new ResizeObserver(all);
  flows.forEach(f => ro.observe(f));
  if (document.fonts) document.fonts.ready.then(all);
  addEventListener('load', all);
  all();
})();

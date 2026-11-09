/* Effective Altruism infographic, narrow screens: draws the connectors the stacked layout needs and sizes the timeline
   duration bars. Wide screens use the original artwork's own lines, so nothing is drawn there.
   - intro: lines leave the bulb's sides (the right one lower, where the heart ends) and run down to each card,
     meeting the white line in its header
   - values: each card's line leaves the card and runs on to its icon on the compass
   - take action (as in action.svg): four separate translucent paths start under the woman's feet, each bends off to
     its own option and ends behind the option's icon; after the icon, a separate arrow (one shape, so no overlaps)
   Every line belongs to a box and fades in just after that box slides in. Positions are measured as if the boxes had
   already arrived (their slide-in offset is taken out), so lines can be drawn at any time. */
(() => {
  const fig = document.querySelector('figure.ea');
  if (!fig) return;
  const NS = 'http://www.w3.org/2000/svg';
  const TEAL = '#0c869b';

  // vertical slide-in offset currently applied to an element (its own and its ancestors' transforms)
  const lift = el => { let t = 0; for (let e = el; e && e !== fig; e = e.parentElement) { const m = getComputedStyle(e).transform; if (m && m !== 'none') t += new DOMMatrix(m).f; } return t; };
  const rel = (box, x, y) => { const b = box.getBoundingClientRect(); return [x - b.left, y - b.top]; };
  // a point in an element's own SVG coordinates -> coordinates inside `box`, where the element will rest
  const at = (el, box, x, y) => { const p = new DOMPoint(x, y).matrixTransform(el.getScreenCTM()); const [a, b] = rel(box, p.x, p.y); return [a, b - lift(el)]; };
  const rect = (el, box) => {
    const r = el.getBoundingClientRect(), b = box.getBoundingClientRect(), d = lift(el);
    return { l: r.left - b.left, t: r.top - b.top - d, r: r.right - b.left, b: r.bottom - b.top - d, w: r.width, h: r.height };
  };
  const visible = sel => [...fig.querySelectorAll(sel)].find(e => e.getClientRects().length);
  const owner = el => el.closest('.reveal') || el;

  function layer(box, cls) {
    let s = box.querySelector(':scope > svg.ea-wires');
    if (!s) { s = document.createElementNS(NS, 'svg'); s.setAttribute('class', 'ea-wires ' + cls); s.setAttribute('aria-hidden', 'true'); box.appendChild(s); }
    s.setAttribute('width', box.offsetWidth); s.setAttribute('height', box.offsetHeight);
    s.replaceChildren();
    return s;
  }
  const wires = [];                                   // [path, the box it belongs to]
  const path = (s, d, attrs, of) => {
    const p = document.createElementNS(NS, 'path');
    p.setAttribute('d', d);
    for (const k in attrs) p.setAttribute(k, attrs[k]);
    s.appendChild(p);
    wires.push([p, owner(of)]);
    return p;
  };
  // polyline through points with rounded corners of radius r
  const rounded = (pts, r) => {
    let d = `M${pts[0][0]},${pts[0][1]}`;
    for (let i = 1; i < pts.length - 1; i++) {
      const [x0, y0] = pts[i - 1], [x1, y1] = pts[i], [x2, y2] = pts[i + 1];
      const l1 = Math.hypot(x1 - x0, y1 - y0), l2 = Math.hypot(x2 - x1, y2 - y1), rr = Math.min(r, l1 / 2, l2 / 2);
      if (!l1 || !l2) continue;
      const a = [x1 - (x1 - x0) / l1 * rr, y1 - (y1 - y0) / l1 * rr], b = [x1 + (x2 - x1) / l2 * rr, y1 + (y2 - y1) / l2 * rr];
      d += `L${a[0]},${a[1]}Q${x1},${y1} ${b[0]},${b[1]}`;
    }
    const e = pts[pts.length - 1];
    return d + `L${e[0]},${e[1]}`;
  };
  const px = el => el.getScreenCTM().a;               // px per unit of an SVG

  // rightmost point of the bulb outline at a given height (in the outline's own units)
  function outlineRight(outline, y) {
    let best = null;
    const n = outline.getTotalLength();
    for (let l = 0; l < n; l += 0.15) {
      const p = outline.getPointAtLength(l);
      if (Math.abs(p.y - y) < 0.35 && (!best || p.x > best.x)) best = p;
    }
    return best;
  }

  function intro() {
    const box = fig.querySelector('.ea-intro');
    const outline = box.querySelector('.bulb-outline');
    const L = visible('.i-l .ea-icard'), R = visible('.i-r .ea-icard');
    const s = layer(box, 'ea-wires-intro');
    const w = 3 * px(L), cl = rect(L, box), cr = rect(R, box);
    const gutL = cl.l / 2, gutR = (cr.r + box.offsetWidth) / 2;
    const [lx, ly] = at(outline, box, 19.23, 31.16);                      // the bulb's widest point, left
    const hr = outlineRight(outline, 55.4);                               // level with the bottom of the heart, right
    const [rx, ry] = at(outline, box, hr.x, hr.y);
    const [, yl] = at(L, box, 0, 259.7), [, yr] = at(R, box, 0, 362.7);   // the cards' white lines
    const o = { fill: 'none', stroke: TEAL, 'stroke-width': w };
    path(s, rounded([[lx, ly], [gutL, ly], [gutL, yl], [cl.l + 1, yl]], 10), o, L);
    path(s, rounded([[rx, ry], [gutR, ry], [gutR, yr], [cr.r - 1, yr]], 10), o, R);
  }

  function values() {
    const box = fig.querySelector('.ea-values');
    const comp = box.querySelector('.ea-compass');
    const s = layer(box, 'ea-wires-values');
    const icons = [...comp.children].filter(c => c.tagName === 'g').slice(1);       // the four icon groups
    const centre = g => { const b = g.getBBox(); return [b.x + b.width / 2, b.y + b.height / 2, b.width / 2]; };
    const pick = (top, left) => icons.find(g => { const [x, y] = centre(g); return (y < 4660) === top && (x < 640) === left; });
    const sc = px(comp);
    for (const [k, top, left] of [['tl', true, true], ['tr', true, false], ['bl', false, true], ['br', false, false]]) {
      const card = box.querySelector('.vm-' + k), vd = card.querySelector('.vd');
      const c = rect(card, box), d = rect(vd, box), y = d.t + d.h / 2;
      const edge = left ? c.l : c.r, gut = left ? c.l / 2 : (c.r + box.offsetWidth) / 2;
      const [ix, iy, ir] = centre(pick(top, left)), [qx, qy] = at(comp, box, ix, iy);
      const ex = left ? qx - ir * sc : qx + ir * sc;                             // the icon's outer edge
      path(s, rounded([[edge, y], [gut, y], [gut, qy], [ex, qy]], 10), { fill: 'none', stroke: TEAL, 'stroke-width': d.h }, card);
    }
  }

  // the arrow from Martina's sketch: shaft and head as one shape, tip at (275, 0), shaft 90 tall, head 210
  const ARROW = [[0, -45], [140, -45], [85, -105], [170, -105], [275, 0], [170, 105], [85, 105], [140, 45], [0, 45]];

  function action() {
    const box = fig.querySelector('.ea-action');
    const s = layer(box, 'ea-wires-action');
    const woman = box.querySelector('.ea-woman'), list = box.querySelector('.a-list');
    const unit = px(woman);                                                         // px per artboard unit (--u)
    const band = 38 * unit, r = 30 * unit, fill = 'rgb(4 178 190 / .3)';
    const [fx, fy] = at(woman, box, 139.4, 5424);                                   // under her feet
    const right = rect(list, box).r;
    const k = 62 * unit / 275;                                                      // arrow 62 units long
    list.querySelectorAll('li').forEach(li => {
      const ic = rect(li.querySelector('svg'), box), cx = (ic.l + ic.r) / 2, cy = (ic.t + ic.b) / 2;
      // the path ends at the icon's centre, hidden behind it
      path(s, rounded([[fx, fy], [fx, cy], [cx, cy]], r), { fill: 'none', stroke: fill, 'stroke-width': band }, li);
      const x0 = right - 275 * k;
      path(s, 'M' + ARROW.map(([x, y]) => `${x0 + x * k},${cy + y * k}`).join('L') + 'Z', { fill }, li);
    });
  }

  // timeline duration bars: from the item's year to the end of the timeline, fading out (as in the artwork)
  function bars() {
    fig.querySelectorAll('.ea-tl').forEach(ol => {
      const end = ol.getBoundingClientRect().bottom - lift(ol);
      ol.querySelectorAll('li.ongoing').forEach(li => li.style.setProperty('--bar', (end - li.getBoundingClientRect().top + lift(li)) + 'px'));
    });
  }

  const show = () => wires.forEach(([p, o]) => { if (o.classList.contains('is-visible') && !p.classList.contains('on')) p.classList.add('on'); });
  const narrow = () => getComputedStyle(fig.querySelector('.a-wide')).display === 'none';

  function draw() {
    bars();
    const n = narrow();
    fig.querySelectorAll('svg.ea-wires').forEach(w => { w.style.display = n ? '' : 'none'; });
    if (!n) return;
    wires.length = 0;
    intro(); values(); action();
    show();
  }
  let raf = 0;
  const later = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(draw); };
  // a box coming in brings its lines with it
  new MutationObserver(ms => { if (ms.some(m => m.target.classList.contains('reveal'))) show(); })
    .observe(fig, { subtree: true, attributes: true, attributeFilter: ['class'] });
  new ResizeObserver(later).observe(fig);
  if (document.fonts) document.fonts.ready.then(later);
  addEventListener('load', later);
  later();
})();

/* Shared behaviour: scroll-reveal, nav fade, mobile menu. No dependencies. */
document.documentElement.classList.add('js');
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

/* reveal on scroll: an element animates in as soon as its top edge is a little way into the window
   (threshold 0, so tall blocks such as long text columns don't wait until a share of their height is visible) */
const io = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
}), { threshold: 0, rootMargin: '0px 0px -8% 0px' });
document.querySelectorAll('.reveal,.wipe').forEach(el => io.observe(el));

/* nav: transparent over the page header (#hero), fades to navy as you scroll; solid on pages without one */
const nav = document.getElementById('nav');
const hero = document.getElementById('hero');
let ticking = false;
function frame() {
  ticking = false;
  const end = hero ? Math.max(1, hero.offsetHeight - nav.offsetHeight * 2) : 1;
  nav.style.setProperty('--nav-a', hero ? clamp(scrollY / end, 0, 1).toFixed(3) : 1);
}
addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }, { passive: true });
addEventListener('resize', frame); frame();

/* mobile menu */
const t = document.querySelector('.menu-toggle'), m = document.getElementById('menu');
if (t && m) t.addEventListener('click', () => {
  const o = m.classList.toggle('open');
  t.setAttribute('aria-expanded', o);
  nav.classList.toggle('menu-open', o);
});

/* topic filters (Diagrams, Comics): show matching tiles and re-deal them into the two columns in their original order */
const bar = document.querySelector('.filters');
const mosaic = document.querySelector('.gallery .mosaic');
if (bar && mosaic) {
  const cols = [...mosaic.querySelectorAll(':scope > .col')];
  const tiles = [];   // original reading order: alternate between the columns
  const lists = cols.map(c => [...c.children]);
  for (let i = 0; i < Math.max(...lists.map(l => l.length)); i++) lists.forEach(l => l[i] && tiles.push(l[i]));
  bar.addEventListener('click', e => {
    const btn = e.target.closest('button[data-filter]');
    if (!btn) return;
    const f = btn.dataset.filter;
    bar.querySelectorAll('button').forEach(b => {
      const on = b === btn;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on);
    });
    let n = 0;
    tiles.forEach(t => {
      const show = f === 'all' || (t.dataset.tags || '').split(' ').includes(f);
      t.hidden = !show;
      if (show) { cols[n % cols.length].appendChild(t); t.style.setProperty('--i', n % 3); n++; }
      else cols[cols.length - 1].appendChild(t);
      if (show) { t.classList.remove('is-visible'); requestAnimationFrame(() => t.classList.add('is-visible')); }
    });
  });
}

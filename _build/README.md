# Build scripts

The scripts that generated the project pages and the two HTML infographics. The site itself is plain static files and
doesn't need them to run; keep them to regenerate pages after content changes.

Run from the site folder (needs Python 3 with Pillow; the infographic scripts read the original artwork files):

- `python _build/build.py .` rewrites the `<main>` of every project page, the Diagrams/Comics grids, `content.json`,
  then stamps CSS/JS links (`tools/bust-cache.py`). Content: `projects.py` (texts, images), `alts.py` (alt text),
  `layouts.py` (page layouts, subtitles, topic tags).
- `python _build/build_cai.py <path to cai.svg>` regenerates the Constitutional AI figure (`cai_figure.html`, which
  `build.py` inserts into its page). Its phone layout comes from `cai_mobile.json`, made from the edited mobile
  design `cai-mobile-edited.svg`:
  `python _build/measure_svg.py _build/cai-mobile-edited.svg m.json`, then `python _build/cai_mobile_from_svg.py m.json _build/cai_mobile.json`.
  `export_cai_svg.py` exports the current phone layout back to an editable SVG.
- `python _build/build_ea.py <path to intro-to-ea.svg>` regenerates the Effective Altruism figure (`ea_figure.html`).
  It also reads the bulb from `assets/lightbulbArtboard 3 copy.svg` next to that file.
- `render.py`, `measure_svg.py` and `export_cai_svg.py` use headless Google Chrome (path set at the top of each).

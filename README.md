# martinapepiciello.com: static site

Plain HTML, CSS and a little vanilla JS. No framework, no npm, no build step. Open the folder in Cursor and edit files directly.

## Run it locally

Links start with `/` (so clean URLs like `/diagrams/` work), so serve the folder instead of double-clicking a file:

```
cd site
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy (Cloudflare Pages)

Create a Pages project from this folder (or connect a Git repo). **Build command: none. Output directory: `/`** (the folder that contains `index.html`).

## How it's organized

```
/site
  index.html                       Home
  diagrams/index.html              Diagrams index (all diagram projects)
  comics/index.html                Comics index
  about/index.html                 About
  contact/index.html               Contact (email and coffee mug illustration)
  <project-slug>/index.html        One folder per project, same URL as the old site
  css/style.css                    The only stylesheet. Design tokens are the :root block at the top
  js/main.js                       Scroll reveal, nav fade (transparent over page headers), mobile menu
  images/
    diagrams/<project-slug>/       <name>.webp (max 1800px) and <name>-800.webp (thumbnail)
    comics/<project-slug>/
    about/                         propic-round.webp
    icons/                         nav wordmark (pers-logo-white.webp), favicon.png + apple-touch-icon.png (MP monogram in a white circle, from src/mp-monogram-circle.png; /favicon.ico too), social icons
    hero/                          page header images (home-, diagrams-, comics-header.webp, 2000px wide)
  content.json                     All text + the image list per project (the reference copy)
  _templates/project.html          Copy this to start a new project page
  tools/fill-image-sizes.py        Optional helper (see "Images")
  sitemap.xml, robots.txt
```

Every page repeats the same header and footer markup. To change the nav or footer, edit it in each `index.html` (search for `<header class="nav"` / `<footer>`).

## Change the design

Everything visual lives in `css/style.css`. The `:root { ... }` block at the top holds the colours (`--navy`, `--emerald`), the fonts (`--font-head` = Cookie, `--font-body` = Montserrat), nav height, and motion easing. To swap fonts, change the two `--font-*` variables **and** the Google Fonts `<link>` in each page's `<head>`. Heading sizes for Cookie are in the "HEADING SIZES" block near the bottom of the CSS (Cookie is small, so they're large).

## Images

1. Put the converted files in the matching folder, for example `images/comics/spacetime/spacetime1.webp` and `spacetime1-800.webp`. The file names are the Drive names with a `.webp` extension. `content.json` lists exactly which files each project expects.
2. Run `python3 tools/fill-image-sizes.py`. It reads each file's real size and writes `width`/`height` into the pages (prevents layout jumps while images load). Re-run it after adding images. It's optional; the site works without it.
3. Index pages and the Home page show the `-800` thumbnail of a project's **first** image. Project pages show the full-size files.
4. Alt text: every image has its own description in its `alt` attribute. When you add an image, write one that says what the picture shows (quote any text in it), and copy it to the `alt` field in `content.json`.
5. Header images go in `images/hero/` and are set per page with `--hero-img:url(...)` on the `<section class="hero">` (Home, Diagrams, Comics). A dark overlay (`.hero::before` in the CSS) keeps the white text readable; without the file the page shows the dark gradient.

## Add a new project

1. Create the folder `images/<diagrams|comics>/<slug>/` and add the `.webp` + `-800.webp` files.
2. Copy `_templates/project.html` to `<slug>/index.html` and replace every `{{...}}` (title, slug, text, images, previous/next links).
3. Add the project's tile to `diagrams/index.html` or `comics/index.html` (copy an existing `<a class="tile wipe" ...>` block; tiles alternate between the two columns). The template's comment explains the layout blocks for the project page itself (lead image rows, text, text beside an image, rows, masonry).
4. Add an entry to `content.json` (copy an existing project), add the URL to `sitemap.xml`, and link neighbours' previous/next if you want it in order.
5. Run `python3 tools/fill-image-sizes.py`.

## Still to fill in

All page text is in (copied from the live Google Sites pages on 23 Oct 2026). What's left:

### Image files the pages expect but that aren't in `images/` yet

None. When you add images to a page: full size max 1800px wide, plus an 800px-wide `-800` copy for the one image used on the index pages, both WebP (quality ~85). Then run `python tools/fill-image-sizes.py` again.

### Images in `images/` that the live site doesn't use (not on any page)

`comics/immunology1bg.webp`, `comics/immunology2bg.webp`; `diagrams/aml-research-program/aml.webp` (the AML tile isn't a link, so only `aml-800.webp` shows); Bad Bug Busters `bbb0`, `bbb13`, `bbb14`, `bbb15`; Faults, errors, failures `safety3`, `safety4`, `safety7`; Radiomon `nickel`. Add them to a page if you want them shown.

### Other

- Cache-busting: every link to a stylesheet or script carries `?v=` and a short fingerprint of the file, so browsers fetch changes straight away. After editing anything in `css/` or `js/`, run `python tools/bust-cache.py` to update the fingerprints.
- Alt text: every artwork image has a description written from the full image (speech bubbles and labels quoted). The nav logo and footer icons use empty alt on purpose, because their links already have labels. When you add an image, write its alt text in the page's `index.html` and in `content.json`.
- Footer: links to LinkedIn, Redbubble and Behance. `icon-linkedin.webp` and `icon-behance.webp` were drawn to match your other icons; swap in your own if you have them. `icon-x.webp` and `icon-instagram.webp` are in `images/icons/` but intentionally not used.
- All full-size images are now at most 1800px wide (originals wider than that were scaled down on 23 Oct 2026).
- Animations: every entrance animation (header text, text blocks, pills, images) uses the same fade-rise-unblur, set by `--rise`, `--rise-blur` and `--rise-time` at the top of `css/style.css`. Make them stronger or subtler there.
- Header images: Home `home-header.webp` (2000px), Diagrams `diagrams-header.webp` (2000px, very wide so it gets enlarged to fill the screen height), Comics `comics-header.webp` (spacetime4, 1920px). For sharp results on retina and large screens, ~2880px wide is ideal; the Diagrams one benefits most.
- Topic filters (Diagrams, Comics): each tile has `data-tags="biology health …"`; the pills above the grid are buttons with `data-filter="biology"`. To retag a project, edit its tile's `data-tags` (and the pill list if you add a new topic). Topics in use: Biology, Health & medicine, Physics, Chemistry, Space, Earth science, Engineering, AI, Effective altruism, Children's books.
- One-line project descriptions: the small uppercase line under each project title (`<p class="lede">` in the page head).
- Background glows beside project text: `.glows` inside each `.intro-text` (one shape for shorter text, two for longer). They're heavily blurred navy/emerald shapes (`.glow-n`, `.glow-e` in the CSS: change the opacity there to make them stronger or fainter) that sit behind the images; hidden below 1100px wide.
- Logos (home page, "Organizations I've worked with"): `images/logos/*.webp`, one row scrolling slowly to the left (pauses on hover), greyscale and in colour on hover. The list appears twice in `index.html` so the loop is seamless: to add a logo, drop a trimmed file (white or transparent background) in that folder and add an `<li>` to both copies (the second copy with `aria-hidden="true"` and empty `alt`).
- Constitutional AI infographic: built as HTML, not an image (`constitutional-ai-training-diagram/index.html`, inside `<figure class="cai">`). Labels are real text you can edit there. The robots, book, learning cycles and REPEAT tag are SVG symbols taken from the original artwork (in the `<svg class="cai-defs">` at the top of the figure); bubbles and dataset cards are CSS. Styles: `css/cai.css` (font: Nunito Sans, loaded on that page only). Arrows are drawn by `js/flow.js` from each `.flow`'s `data-links` list ("from>to", ids from `data-node`), on wide screens. Below 720px the figure uses the phone layout from your edited `cai-mobile-layout.svg`: every box keeps the position, size and line breaks from that file (`--nx/--ny/--nw/--nh` on each node, `br.bm` = phone-only line break, `br.bd` = desktop-only) and the arrows are the ones you drew (`svg.links-m`); the whole thing scales with the screen. Entrance: on wide screens the boxes rise in one after another in reading order, each arrow fading in with the box it points to; on phones each box and arrow appears as it scrolls into view.
- Effective Altruism infographic: also HTML (`introduction-to-effective-altruism-infographic/index.html`, inside `<figure class="ea">`), in Merriweather and Raleway, loaded on that page only. Styles: `css/ea.css`. Headings, card text, timelines, chart labels and the take-action list are real text. The illustrations (bulb, icons, compass, woman, paths, charts) are small inline SVGs cut from the original artwork, with their text kept as live SVG text. Pictograms are counted icons: the counts are in the markup, with a sentence for screen readers under each one. On wide screens the intro, values and take-action sections keep the original artboard positions (`--x`/`--y` in units of 1/1280 of the figure width). Below 1000px everything stacks into one column at one consistent scale (text and illustrations at their artboard size times about 0.8 on a phone; headings on tighter steps: title 32px, section headings 25.6px, card titles 20.8px). Phone-only pieces: the intro (small bulb, lines from its sides to each card's icon), values ordered around the compass with each underline wired to its icon, take action as four separate paths branching from under the woman's feet (all drawn by `js/ea.js`), the AI chart with the brain/bee markers as a legend above it, a phone version of the decision-making chart (circle as wide as the card, dot at 1:10,000 of its area, roomier timeline), and the people pictograms re-wrapped across the card (180 = 20 × 9, 133 = 19 × 7). Timeline duration bars run from their year to the end of the timeline and fade out (`js/ea.js` measures them). Fixes to the source: the sentence "finding unusually good ways to do good" was missing its last word, and the bulb outline had an SVG export glitch (a sliver at the top of the screw) that is corrected in the build.


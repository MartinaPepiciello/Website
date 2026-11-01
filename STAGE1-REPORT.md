# Report: site build

## What's in the zip
24 pages (Home, Diagrams, Comics, About, Contact + 19 project pages), one stylesheet, one script, `content.json`, `README.md`, a project-page template, `sitemap.xml`, `robots.txt`, and an optional `tools/fill-image-sizes.py`. Design = the Cookie-headings version of combined v2.

## Text
- **Verbatim (copied from the live Home page):** hero, both section intros and subtitles, 3 testimonials, About text, pricing (3 plans), contact text, newsletter text, nav and footer. Copyright is updated to 2026.
- **Verbatim from Diagrams page:** hero subtitle and all project titles/slugs. **Comics:** all 12 titles/slugs.
- **NOT obtained verbatim:** body text of all 19 project pages, the full About page (live page has "My work" and "What working with me looks like" sections), the Contact page text, and the Comics hero subtitle. My fetch tool returns summaries for these pages and the shell can't reach the site (blocked), so I did not use any paraphrase. These spots are marked `TODO` in the HTML and empty `body` fields in `content.json`.
- The Contact page uses the Home page's "Sounds good? Let's chat!" text plus a Formspree form (`YOUR_FORM_ID` to replace). The live site has no form.

## Images (referenced, not processed; you're converting them)
- 106 Drive files are assigned to projects → 212 files expected (full + `-800`), plus `propic-round.webp`, `pers-logo-bg.webp`, `icon-linkedin.webp`, `icon-rb.webp`, `icon-behance.webp`.
- **No file found in Drive:** Constitutional AI training diagram, Effective Altruism infographic (both appear on the Home page), Faults errors failures, Seismic monitoring. These show empty hatched panels.
- **Ambiguous (matched by filename, please check):** Noisy genes, The honest microbes (teeth*), A Shore Thing (sea-life files), Neuron synapses, Radiomon (element files), Molecular neuroscience (figure_*), Gil and Rosie (aorf*; aorf2 and aorf9 absent). Order within every project is by filename and unverified against the live site.
- **Not assigned to any project:** cfo.png, fig1.png, fig2.png, k-utec-*.jpg (3), cardioid.jpg, my-cow-classical* (4), immunology1bg/2bg.jpg, cargo1.jpg. Also unused: banners/, collabs/, carousels/ folders, icon-ig/x/bgr, site-icon-comic, testimonial-icon.
- Home hero image is a guess (`io-earth-venus-600dpi-black`). Diagrams/Comics hero (wave image) not found. "Acute myeloid leukemia research program" has no page on the live site, so it is a non-linked tile.
- Logo and portrait sizes aren't known; the portrait is displayed square (cropped to fit). The Drive `propic-round` may need a square (not circular) version.
- Alt text is generic ("Title, image n of N"); add real alt text.

## Not done / decisions for you
- Newsletter is a placeholder "Subscribe" button (`#newsletter`). The Substack iframe can't be styled.
- Fonts load from Google Fonts (Cookie, Montserrat).
- Not tested here: Cookie rendering (sandbox has no access to Google Fonts) and real artwork.

# Ibrahim Alobaid — Personal Site

Live at **https://ibrahim-dev.me** (English) and **https://ibrahim-dev.me/ar/** (Arabic).

Static, bilingual personal site built on identity **2a · Classic Luxury**:
Onyx `#0E0D0B` / Umber `#1B1814` / Ivory `#F3EEE3` / Gilt `#C6A15B` / Champagne `#E3CB94` / Antique `#8C6D2E`,
Cormorant Garamond + Jost (Amiri + IBM Plex Sans Arabic for Arabic), the IA monogram and the Aleppine eight-point star.

## Structure

```
src/index.html        ← the page (English source of truth) — EDIT THIS
src/ar.json           ← Arabic strings, keyed by data-i18n attributes
tools/build.py        ← generates index.html, ar/index.html, sitemap.xml
index.html, ar/       ← generated — do not edit by hand
assets/               ← css, js, images (portrait, OG image, icons)
robots.txt, sitemap.xml, site.webmanifest, llms.txt, 404.html, favicon.ico
```

## Edit → build → publish

```bash
python tools/build.py
git add -A && git commit -m "Update site" && git push
```

- **English text:** edit `src/index.html`.
- **Arabic text:** edit the matching key in `src/ar.json`. The build stops and lists any key that's missing.
- **New Q&A item:** copy a `<details class="faq__item">` block in `src/index.html`, give it new `faq.qN` / `faq.aN` keys, and add both to `src/ar.json`. The FAQPage structured data is generated from the visible Q&A automatically.

## SEO in place

- Separate, crawlable English and Arabic URLs with `hreflang` and canonical tags
- JSON-LD: `WebSite`, `ProfilePage`, `Person` (with Arabic and alternate spellings of the name), `Organization` (Syrian AI Community), `FAQPage`
- Open Graph / Twitter card with a 1200×630 share image
- `sitemap.xml` (with hreflang alternates and image), `robots.txt`, favicons, web manifest, `llms.txt` for AI search engines
- IndexNow key file at the root for instant Bing/Yandex submission

## Run locally

```bash
python -m http.server 5173
```

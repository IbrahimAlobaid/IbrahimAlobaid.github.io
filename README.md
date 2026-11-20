# Ibrahim Alobaid — Personal Site

Static personal website built on identity **2a · Classic Luxury**:
Onyx `#0E0D0B` / Umber `#1B1814` / Ivory `#F3EEE3` / Gilt `#C6A15B` / Champagne `#E3CB94` / Antique `#8C6D2E`,
Cormorant Garamond + Jost (Amiri + IBM Plex Sans Arabic for Arabic), the IA monogram, and the Aleppine eight-point star pattern.

No build step, no dependencies.

```
index.html            ← all content (English, source of truth)
assets/js/i18n.js     ← Arabic translations (keys match data-i18n attributes)
assets/js/main.js     ← language toggle, mobile menu, scroll reveal
assets/css/styles.css ← design tokens and layout
assets/img/           ← portrait.jpg, favicon.svg
```

## Run locally

```bash
python -m http.server 5173
```

Then open http://localhost:5173 (add `?lang=ar` to open in Arabic).

## Edit content

- **English text:** edit `index.html` directly.
- **Arabic text:** edit the matching key in `assets/js/i18n.js`.
- **New text element:** add `data-i18n="section.key"` in the HTML and the same key in `i18n.js`.
- **Photo:** replace `assets/img/portrait.jpg` (square, ≥ 800×800). It is shown in monochrome; colour returns on hover.

## Deploy

Any static host works. Two quick options:

- **Vercel:** `npx vercel` from this folder (framework preset: *Other*).
- **GitHub Pages:** push to a repo → Settings → Pages → deploy from the `main` branch root.

# WealthGuard Investment Recovery — Website

The live, deployable version of the **WealthGuard Investment Recovery** site created in
Claude Design. The design's self-contained export has been unpacked into a normal static
repo (real asset files, editable markup) that hosts cleanly on GitHub Pages or any static
host (Netlify, Cloudflare Pages, S3, …). No build step is required to deploy.

## How it works (important)

The page is a single-page app with tabbed navigation (Home, Services, Why Us, Our Expert,
Fees, FAQs, Contact). It is rendered by the Claude-Design runtime (`assets/js/dc-runtime.js`),
which is React-based. The design's template lives inside `index.html` as an `<x-dc>` block
with `{{ … }}` bindings, `<sc-for>` loops and `<sc-if>` conditionals; the text content lives
in a small data component in a `<script type="text/x-dc">` tag at the bottom of `index.html`.

**React is self-hosted** (`assets/vendor/react*.js`) and loaded before the runtime, so the
site has **no external CDN dependency** and works even if a CDN is down. The 18 web-font files
(Spectral for headings, Archivo for body) are embedded locally too.

---

## Repository structure

```
wealthguard-website/
├── index.html                  # The site (design template + runtime bootstrap)
├── 404.html                    # Branded not-found page
├── favicon.ico                 # Generated from the logo
├── .nojekyll                   # Skip Jekyll processing on GitHub Pages
├── robots.txt / sitemap.xml    # SEO (update the URL to your live domain)
├── README.md / LICENSE / .gitignore
│
├── assets/
│   ├── img/
│   │   ├── logo.png            # Brand logo (transparent, icon only)
│   │   ├── apple-touch-icon.png
│   │   └── expert-placeholder.jpg  # ← replace with the real consultant photo
│   ├── fonts/
│   │   └── font-01…18.woff2    # Embedded Spectral + Archivo web fonts
│   ├── js/
│   │   └── dc-runtime.js       # Claude-Design React runtime (renders the page)
│   └── vendor/
│       ├── react.production.min.js       # Self-hosted React 18.3.1
│       └── react-dom.production.min.js    # Self-hosted ReactDOM 18.3.1
│
├── tools/                      # Dev helpers (NOT needed to serve the site)
│   ├── unpack_design.py        # Rebuild the site from a Claude-Design export
│   ├── generate_assets.py      # Rebuild favicon + apple icon + placeholder
│   └── process_logo.py         # Clean a raw logo (transparent bg, remove text)
│
└── .github/workflows/deploy.yml  # Optional: deploy via GitHub Actions
```

Everything at the repo root **is** the website. The `tools/` folder is developer tooling only.

---

## Quick start (local preview)

A tiny local server avoids `file://` path issues:

```bash
python -m http.server 8000     # then open http://localhost:8000
# or:  npx serve .
```

---

## Deploying to GitHub Pages

### Option A — Deploy from a branch (simplest)

1. Create a public repo named **`wealthguard-website`**.
2. Push:
   ```bash
   cd wealthguard-website
   git init && git add . && git commit -m "Initial WealthGuard site"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/wealthguard-website.git
   git push -u origin main
   ```
3. On GitHub: **Settings ▸ Pages ▸ Source → Deploy from a branch**, set **`main` / `(root)`**, Save.
4. Live in ~1 min at `https://YOUR-USERNAME.github.io/wealthguard-website/`.
   *(You can delete `.github/workflows/deploy.yml` if you use this option.)*

### Option B — Deploy with GitHub Actions

Push the repo, then **Settings ▸ Pages ▸ Source → GitHub Actions**. Every push to `main`
publishes automatically via the included workflow (see the **Actions** tab for logs).

> All asset paths are **relative**, so the site works from the `/wealthguard-website/` subpath
> with no changes. The only absolute path is the "Back to home" link in `404.html` — update it
> if you rename the repo or add a custom domain.

---

## Custom domain (optional)

1. Add a `CNAME` file at the repo root containing just your domain (e.g. `www.wealthguard.com.sg`).
2. Point your DNS at GitHub Pages (CNAME → `YOUR-USERNAME.github.io`, or GitHub's A records).
3. **Settings ▸ Pages** → add the domain, enable **Enforce HTTPS**.
4. Update the absolute URLs in `robots.txt`, `sitemap.xml`, `index.html` (`og:url` if added) and `404.html`.

---

## Customizing the site

### 1. The consultant photo (“Our Expert” tab)
Replace **`assets/img/expert-placeholder.jpg`** with the real portrait (keep the filename, or
update the `src` in the `#expert`/“Our Expert” `<img>` in `index.html`). A **square** image
works best — it's shown with `object-fit: cover`.

### 2. The logo
Replace **`assets/img/logo.png`** (transparent PNG, icon only). Then optionally refresh the
favicon/app icon: `python tools/generate_assets.py`.

### 3. Text content
All copy is inside `index.html`:
- **Section structure and static text** live in the `<x-dc>` template.
- **Repeated/list content** — the services, "why us" reasons, expert bio points, fees and FAQs —
  lives in the data arrays inside the `<script type="text/x-dc">` component near the bottom
  (`services`, `reasons`, `expertPoints`, `fees`, `FAQS`). Edit the strings there.
- **Contact details** (email / WhatsApp) appear in the footer and Contact tab of the template.

### 4. Accent colour
The gold accent is set via the runtime prop `accentColor` (default `#c9a15a`), referenced as
`{{ accent }}` throughout. Change the default in the component's `renderVals()` (`const accent = …`).

### 5. Re-importing an updated design
If you edit the design again in Claude Design and export a new bundle, regenerate everything:
```bash
python tools/unpack_design.py path/to/NewExport.html
```
This re-extracts all assets and rewrites `index.html` (keeping React self-hosted and the
expert `<img>` swap). Requires Python with `Pillow`, `numpy`, `scipy` only for the other two
tools; `unpack_design.py` itself uses just the standard library.

---

## Third-party code
`assets/vendor/` contains React and ReactDOM (MIT, © Meta). `assets/js/dc-runtime.js` is the
Claude-Design runtime. The logo and brand assets are proprietary to WealthGuard.

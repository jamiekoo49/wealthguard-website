#!/usr/bin/env python3
"""
Unpack a Claude-Design "bundled" HTML export into this deployable static repo.

The design tool exports a single self-contained HTML file in which the real page
is stored as a JSON template plus a manifest of base64 (optionally gzipped)
assets, rendered at runtime into blob URLs by an embedded React-based runtime.

This script does the same substitution the bundle does, but writes the assets as
real files and rewrites the template to reference them by relative path — giving
an editable, deployable repo instead of one opaque blob. It also:
  * self-hosts React (assets/vendor/*) so the site has no runtime CDN dependency,
  * injects <title>/description/Open Graph/favicon into <head>,
  * swaps the "Our Expert" CSS placeholder for a swappable <img>.

Usage (from the repo root):
    python tools/unpack_design.py path/to/WealthGuard_Investment_Recovery.html

Requires the React UMD builds to already exist at:
    assets/vendor/react.production.min.js
    assets/vendor/react-dom.production.min.js
(They ship with this repo. To refresh them: `npm pack react@18.3.1 react-dom@18.3.1`
 and copy the files from each tarball's package/umd/ folder.)
"""
import sys, os, re, json, base64, gzip

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
JS = os.path.join(ROOT, "assets", "js")
FONTS = os.path.join(ROOT, "assets", "fonts")


def extract_script(html, script_type):
    m = re.search(
        r'<script type="__bundler/%s">(.*?)</script>' % re.escape(script_type),
        html, re.S)
    if not m:
        raise SystemExit(f"Could not find <script type=__bundler/{script_type}>")
    return m.group(1).strip()


def main(bundle_path):
    html = open(bundle_path, encoding="utf-8").read()
    manifest = json.loads(extract_script(html, "manifest"))
    template = json.loads(extract_script(html, "template"))

    for d in (IMG, JS, FONTS):
        os.makedirs(d, exist_ok=True)

    # 1) Decode + save each asset, mapping its UUID to a relative repo path.
    path_for = {}
    font_i = 0
    for uuid, entry in manifest.items():
        data = base64.b64decode(entry["data"])
        if entry.get("compressed"):
            data = gzip.decompress(data)
        mime = entry["mime"]
        if mime == "image/png":
            rel, out = "assets/img/logo.png", os.path.join(IMG, "logo.png")
        elif mime == "text/javascript":
            rel, out = "assets/js/dc-runtime.js", os.path.join(JS, "dc-runtime.js")
        elif mime == "font/woff2":
            font_i += 1
            name = f"font-{font_i:02d}.woff2"
            rel, out = f"assets/fonts/{name}", os.path.join(FONTS, name)
        else:
            raise SystemExit(f"Unhandled asset mime: {mime}")
        open(out, "wb").write(data)
        path_for[uuid] = rel
    print(f"Extracted {len(manifest)} assets ({font_i} fonts).")

    # 2) Replace every UUID in the template with its relative path.
    for uuid, rel in path_for.items():
        template = template.replace(uuid, rel)

    # 3) Head: lang, title, meta, favicon, and self-hosted React before runtime.
    template = template.replace(
        '<html><head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<html lang="en"><head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>WealthGuard Investment Recovery Pte Ltd</title>\n'
        '<meta name="description" content="WealthGuard Investment Recovery is a specialist '
        'consultancy helping clients in Singapore and Hong Kong pursue complaints for '
        'mis-sold investment products \u2014 without going straight to litigation.">\n'
        '<meta property="og:title" content="WealthGuard Investment Recovery Pte Ltd">\n'
        '<meta property="og:description" content="Investment mis-selling &amp; recovery '
        'specialists for non-retail clients in Singapore and Hong Kong.">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:image" content="assets/img/apple-touch-icon.png">\n'
        '<link rel="icon" href="favicon.ico" sizes="any">\n'
        '<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">',
        1)

    runtime_tag = '<script src="assets/js/dc-runtime.js"></script>'
    template = template.replace(
        runtime_tag,
        '<!-- React is self-hosted; the runtime skips its CDN fetch when '
        'window.React already exists. -->\n'
        '<script src="assets/vendor/react.production.min.js"></script>\n'
        '<script src="assets/vendor/react-dom.production.min.js"></script>\n'
        + runtime_tag,
        1)

    # 4) Expert CSS placeholder -> swappable <img>.
    template = re.sub(
        r'<div style="width:100%;aspect-ratio:1;border-radius:12px;'
        r'background:repeating-linear-gradient\(135deg,#eee8db,#eee8db 11px,'
        r'#e7e0d1 11px,#e7e0d1 22px\);[^"]*">\s*'
        r'<span[^>]*>\[ principal consultant photo \]</span>\s*</div>',
        '<!-- Swap expert-placeholder.jpg for the real portrait (square works best). -->\n'
        '            <img src="assets/img/expert-placeholder.jpg" alt="Principal consultant" '
        'style="width:100%;aspect-ratio:1;border-radius:12px;object-fit:cover;display:block;'
        'margin-bottom:18px;">',
        template, count=1)

    leftover = re.findall(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', template)
    if leftover:
        print("WARNING: unresolved UUIDs remain:", set(leftover))

    out = os.path.join(ROOT, "index.html")
    open(out, "w", encoding="utf-8").write(template)
    print(f"Wrote {out} ({len(template)} bytes).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python tools/unpack_design.py <bundle.html>")
    main(sys.argv[1])

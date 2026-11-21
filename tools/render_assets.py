"""
Pre-render Mermaid diagrams (to SVG) and display math (to MathML) at build time,
so article pages ship no diagram/math JavaScript and are fully crawlable.

Results are cached in tools/cache/render-cache.json keyed by a hash of the source,
so rebuilding only needs a browser when a diagram or formula changes.
Requires: playwright (python) + an installed Chrome. Network access to cdn.jsdelivr.net
is needed only for cache misses.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_FILE = ROOT / "tools" / "cache" / "render-cache.json"

MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"
KATEX_URL = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"
FONTS = (
    "https://fonts.googleapis.com/css2?family=Jost:wght@400;500"
    "&family=IBM+Plex+Sans+Arabic:wght@400;500&display=block"
)

MERMAID_CONFIG = {
    "startOnLoad": False,
    "securityLevel": "strict",
    "theme": "base",
    "fontFamily": "Jost, 'IBM Plex Sans Arabic', system-ui, sans-serif",
    "flowchart": {"curve": "basis", "padding": 14, "nodeSpacing": 40, "rankSpacing": 46, "htmlLabels": True, "useMaxWidth": True},
    "sequence": {"useMaxWidth": True, "mirrorActors": False, "actorMargin": 60},
    "themeVariables": {
        "darkMode": True,
        "background": "transparent",
        "fontFamily": "Jost, 'IBM Plex Sans Arabic', system-ui, sans-serif",
        "fontSize": "16px",
        "primaryColor": "#1B1814",
        "primaryTextColor": "#F3EEE3",
        "primaryBorderColor": "#C6A15B",
        "secondaryColor": "#24201A",
        "secondaryTextColor": "#F3EEE3",
        "secondaryBorderColor": "#8C6D2E",
        "tertiaryColor": "#141210",
        "tertiaryTextColor": "#F3EEE3",
        "tertiaryBorderColor": "#3A3226",
        "lineColor": "#B8975A",
        "textColor": "#F3EEE3",
        "mainBkg": "#1B1814",
        "nodeBorder": "#C6A15B",
        "clusterBkg": "#13110E",
        "clusterBorder": "#3A3226",
        "titleColor": "#E3CB94",
        "edgeLabelBackground": "#0E0D0B",
        "actorBkg": "#1B1814",
        "actorBorder": "#C6A15B",
        "actorTextColor": "#F3EEE3",
        "actorLineColor": "#5A4C36",
        "signalColor": "#C6A15B",
        "signalTextColor": "#F3EEE3",
        "labelBoxBkgColor": "#1B1814",
        "labelBoxBorderColor": "#8C6D2E",
        "labelTextColor": "#F3EEE3",
        "loopTextColor": "#E3CB94",
        "noteBkgColor": "#24201A",
        "noteTextColor": "#F3EEE3",
        "noteBorderColor": "#8C6D2E",
        "activationBkgColor": "#24201A",
        "activationBorderColor": "#C6A15B",
        "sequenceNumberColor": "#0E0D0B",
        "stateBkg": "#1B1814",
        "stateLabelColor": "#F3EEE3",
        "compositeBackground": "#13110E",
        "altBackground": "#13110E",
        "transitionColor": "#B8975A",
        "transitionLabelColor": "#E3CB94",
    },
}


def key_for(kind: str, source: str) -> str:
    salt = json.dumps(MERMAID_CONFIG, sort_keys=True) if kind == "mermaid" else ""
    return kind + ":" + hashlib.sha256((source.strip() + salt).encode("utf-8")).hexdigest()[:16]


def svg_ratio(svg: str) -> tuple[float, float]:
    import re

    m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', svg)
    return (float(m.group(1)), float(m.group(2))) if m else (0.0, 1.0)


def verticalize(source: str) -> str:
    """Re-orient a left-to-right flowchart top-to-bottom so long pipelines stay legible in a text column."""
    import re

    lines = source.strip().split("\n")
    lines[0] = re.sub(r"^(\s*(?:flowchart|graph))\s+(LR|RL)\b", r"\1 TB", lines[0])
    return "\n".join(re.sub(r"^(\s*direction)\s+(LR|RL)\b", r"\1 TB", l) for l in lines)


def is_too_wide(svg: str, source: str) -> bool:
    w, h = svg_ratio(svg)
    return source.lstrip().startswith(("flowchart", "graph")) and w > 1000 and w / max(h, 1) > 3


def load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")


PAGE = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{FONTS}">
<script src="{MERMAID_URL}"></script><script src="{KATEX_URL}"></script>
<style>body{{background:#0E0D0B;color:#F3EEE3;margin:0;width:1100px}}</style>
</head><body><div id="host"></div></body></html>"""


async def _render(jobs: list[tuple[str, str, str]]) -> dict:
    from playwright.async_api import async_playwright

    out: dict[str, str] = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome")
        page = await browser.new_page(viewport={"width": 1100, "height": 900})
        await page.set_content(PAGE, wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        await page.evaluate(f"mermaid.initialize({json.dumps(MERMAID_CONFIG)})")
        for key, kind, source in jobs:
            try:
                if kind == "mermaid":
                    dom_id = "mmd-" + key.split(":")[1][:10]
                    svg = await page.evaluate(
                        "async ([id, code]) => (await mermaid.render(id, code)).svg",
                        [dom_id, sanitize_mermaid(source)],
                    )
                    out[key] = svg
                else:
                    out[key] = await page.evaluate(
                        "(tex) => katex.renderToString(tex, {displayMode: true, output: 'mathml', throwOnError: true})",
                        source,
                    )
            except Exception as exc:  # report, don't abort the whole build
                first = str(exc).splitlines()[0][:160]
                print(f"  ! could not render {kind} ({key}): {first}\n    source starts: {source[:80]!r}")
        await browser.close()
    return out


def sanitize_mermaid(source: str) -> str:
    """Mermaid treats ';' as a statement separator, even inside sequence-diagram notes and messages."""
    lines = []
    for line in source.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith(("Note ", "note ")) or ("->>" in line or "-->>" in line or "-)" in line):
            head, sep, text = line.partition(":")
            if sep:
                line = head + sep + text.replace(";", "#59;")
        lines.append(line)
    return "\n".join(lines)


def render_all(items: list[tuple[str, str]]) -> dict[str, str]:
    """items: (kind, source) where kind is 'mermaid' or 'math'. Returns {key: html}."""
    cache = load_cache()
    jobs = []
    seen = set()
    for kind, source in items:
        k = key_for(kind, source)
        if k not in cache and k not in seen:
            jobs.append((k, kind, source.strip()))
            seen.add(k)
    if jobs:
        print(f"Rendering {len(jobs)} new diagram(s)/formula(s) with headless Chrome…")
        cache.update(asyncio.run(_render(jobs)))
        save_cache(cache)
    # Second pass: vertical variants for pipelines too wide to read in a text column.
    extra = []
    for kind, source in items:
        k = key_for(kind, source)
        if kind == "mermaid" and k in cache and is_too_wide(cache[k], source):
            v = verticalize(source)
            vk = key_for("mermaid", v)
            if vk not in cache and vk not in seen:
                extra.append((vk, "mermaid", v))
                seen.add(vk)
    if extra:
        print(f"Re-orienting {len(extra)} wide diagram(s) top-to-bottom…")
        cache.update(asyncio.run(_render(extra)))
        save_cache(cache)
    return cache


def best_svg(cache: dict, source: str) -> str:
    svg = cache[key_for("mermaid", source)]
    if is_too_wide(svg, source):
        return cache.get(key_for("mermaid", verticalize(source)), svg)
    return svg

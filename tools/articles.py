"""
Article pipeline: Obsidian Markdown series → bilingual, SEO-complete static pages.

Called from tools/build.py. Produces:
  /articles/index.html, /ar/articles/index.html                (series hub + roadmap)
  /articles/<slug>/index.html, /ar/articles/<slug>/index.html  (articles)
  /articles/feed.xml, /ar/articles/feed.xml                    (RSS)
  /articles/assets/<series>/*.webp|jpg                         (optimized images)
  /articles/code/<series>/*                                    (lab files)

Handles Obsidian features: YAML front matter, [[wikilinks]], ![[image embeds]],
> [!callouts], ```mermaid (pre-rendered SVG), $$ math $$ (MathML), [^footnotes].
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin
from PIL import Image
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name

from render_assets import best_svg, key_for, render_all

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ibrahim-dev.me"
TODAY = dt.date.today().isoformat()
FONTS = (
    "https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400"
    "&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400"
    "&family=IBM+Plex+Sans+Arabic:wght@300;400;500;600&family=Jost:wght@300;400;500&display=swap"
)

UI = {
    "en": {
        "home": "Home", "articles": "Articles", "about": "About", "work": "Work", "talks": "Talks",
        "faqNav": "Q&A", "contact": "Contact", "langLabel": "العربية", "langShort": "ع",
        "skip": "Skip to content", "onThisPage": "On this page", "minRead": "min read",
        "level": "Level", "published": "Published", "updated": "Updated",
        "readOther": "اقرأ بالعربية", "articleOf": "Article {n} of {total}",
        "faqTitle": "Frequently asked questions", "faqLede": "Short answers to the questions people search for most about this topic.",
        "labTitle": "Run the lab", "labText": "Every example runs locally. Download the files and follow the commands in the article.",
        "download": "Download", "prev": "Previous article", "next": "Next article",
        "soon": "Coming soon", "roadmap": "Series roadmap", "writtenBy": "Written by",
        "authorRole": "Lead AI Engineer, Healthcare AI · Founder, Syrian AI Community",
        "authorBio": "I build production voice agents and LLM systems, and teach applied AI to the next generation of Syrian engineers.",
        "copy": "Copy", "copied": "Copied", "start": "Start with Article 01",
        "publishedCount": "{n} of {total} articles published",
        "indexEyebrow": "Writing", "indexTitle": "Articles, <em>engineered.</em>",
        "indexLede": "Long-form, practical writing on building AI systems that work outside the demo — with diagrams, runnable code and references.",
        "series": "Series", "audience": "Who it's for", "allArticles": "All articles",
        "readArticle": "Read article", "references": "References", "share": "Share",
        "seriesHub": "Series hub", "breadcrumb": "Breadcrumb", "backHome": "Ibrahim Alobaid — home",
        "level_map": {}, "lang_name": "English",
    },
    "ar": {
        "home": "الرئيسية", "articles": "المقالات", "about": "نبذة", "work": "الأعمال", "talks": "المحاضرات",
        "faqNav": "أسئلة", "contact": "تواصل", "langLabel": "English", "langShort": "EN",
        "skip": "تخطَّ إلى المحتوى", "onThisPage": "في هذه المقالة", "minRead": "دقيقة قراءة",
        "level": "المستوى", "published": "نُشرت", "updated": "حُدّثت",
        "readOther": "Read in English", "articleOf": "المقالة {n} من {total}",
        "faqTitle": "أسئلة شائعة", "faqLede": "إجابات مختصرة لأكثر ما يبحث عنه الناس حول هذا الموضوع.",
        "labTitle": "جرّب بنفسك", "labText": "كل الأمثلة تعمل محلياً. حمّل الملفات واتبع الأوامر الموجودة في المقالة.",
        "download": "تحميل", "prev": "المقالة السابقة", "next": "المقالة التالية",
        "soon": "قريباً", "roadmap": "خارطة السلسلة", "writtenBy": "بقلم",
        "authorRole": "مهندس ذكاء اصطناعي رئيسي في الذكاء الاصطناعي الطبي · مؤسس مجتمع الذكاء الاصطناعي السوري",
        "authorBio": "أبني وكلاء صوتيين وأنظمة نماذج لغوية تعمل في الإنتاج، وأعلّم الذكاء الاصطناعي التطبيقي للجيل القادم من المهندسين السوريين.",
        "copy": "نسخ", "copied": "تم النسخ", "start": "ابدأ من المقالة الأولى",
        "publishedCount": "{n} من {total} مقالة منشورة",
        "indexEyebrow": "الكتابة", "indexTitle": "مقالات <em>هندسية.</em>",
        "indexLede": "كتابة عملية معمّقة عن بناء أنظمة ذكاء اصطناعي تعمل خارج العروض التجريبية — مع مخططات وأكواد قابلة للتشغيل ومراجع.",
        "series": "السلسلة", "audience": "لمن هذه السلسلة", "allArticles": "كل المقالات",
        "readArticle": "اقرأ المقالة", "references": "المراجع", "share": "مشاركة",
        "seriesHub": "صفحة السلسلة", "breadcrumb": "مسار التنقل", "backHome": "إبراهيم العبيد — الرئيسية",
        "level_map": {
            "Beginner": "مبتدئ", "Beginner to Intermediate": "مبتدئ إلى متوسط",
            "Intermediate": "متوسط", "Advanced": "متقدم",
        },
        "lang_name": "العربية",
    },
}

MONTHS_AR = ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول",
             "تشرين الأول", "تشرين الثاني", "كانون الأول"]

CALLOUT_DEFAULTS = {
    "abstract": ("Summary", "الخلاصة"), "question": ("Question", "سؤال"), "important": ("Important", "مهم"),
    "tip": ("Tip", "نصيحة"), "warning": ("Warning", "تنبيه"), "success": ("Takeaway", "الخلاصة"),
    "info": ("Note", "ملاحظة"), "example": ("Example", "مثال"), "todo": ("Exercise", "تمرين"),
}


# --------------------------------------------------------------------------- helpers
def esc(s: str) -> str:
    return html.escape(s, quote=True)


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower(), flags=re.U)
    return re.sub(r"[\s_]+", "-", text).strip("-") or "section"


def strip_md(s: str) -> str:
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"\[\^[^\]]+\]", "", s)
    s = re.sub(r"[*_`]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def text_of(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def clip(s: str, n: int = 158) -> str:
    if len(s) <= n:
        return s
    cut = s[:n]
    for stop in (". ", "، ", ", ", " "):
        i = cut.rfind(stop)
        if i > n * 0.6:
            return cut[: i + (1 if stop.startswith(".") else 0)].rstrip(" ,،") + ("" if stop.startswith(".") else "…")
    return cut.rstrip() + "…"


def fmt_date(iso: str, lang: str) -> str:
    d = dt.date.fromisoformat(iso)
    if lang == "ar":
        return f"{d.day} {MONTHS_AR[d.month - 1]} {d.year}"
    return f"{d.strftime('%B')} {d.day}, {d.year}"


# --------------------------------------------------------------------------- markdown
class CodeFormatter(HtmlFormatter):
    def wrap(self, source):
        return source


def make_md() -> MarkdownIt:
    def hl(code: str, lang: str, _attrs) -> str:
        lang = (lang or "text").strip().lower()
        try:
            lexer = get_lexer_by_name(lang)
        except Exception:
            lexer = TextLexer()
        body = highlight(code, lexer, CodeFormatter(nowrap=True))
        label = {"bash": "Terminal", "text": "Text", "json": "JSON", "python": "Python"}.get(lang, lang.upper())
        return f'<pre class="code" data-lang="{esc(label)}" dir="ltr"><code class="language-{esc(lang)}">{body}</code></pre>'

    md = (
        MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False, "highlight": hl})
        .enable("table")
        .enable("strikethrough")
        .use(footnote_plugin)
        .use(anchors_plugin, min_level=2, max_level=3, slug_func=slugify, permalink=False)
    )
    return md


MD = make_md()


@dataclass
class Article:
    meta: dict
    lang: str
    slug: str
    n: int
    title: str
    description: str
    level: str
    date: str
    cover: str
    body_html: str = ""
    toc: list = field(default_factory=list)
    words: int = 0
    minutes: int = 0
    tags: list = field(default_factory=list)

    @property
    def path(self) -> str:
        return ("/ar" if self.lang == "ar" else "") + f"/articles/{self.slug}/"

    @property
    def url(self) -> str:
        return SITE + self.path


# --------------------------------------------------------------------------- images
def image_out_dir(series: dict) -> Path:
    return ROOT / "articles" / "assets" / series["slug"]


def process_images(series: dict) -> dict:
    """Convert source PNGs to responsive WebP (+ OG JPG for covers). Returns {name: (w, h)}."""
    src_dir = ROOT / series["source_dir"] / "assets"
    out = image_out_dir(series)
    out.mkdir(parents=True, exist_ok=True)
    covers = {series["cover"]}
    sizes = {}
    for png in sorted(src_dir.glob("*.png")):
        stem = png.stem
        im = Image.open(png)
        w, h = im.size
        sizes[png.name] = (w, h)
        for width in (800, 1600):
            dst = out / f"{stem}-{width}.webp"
            if not dst.exists() or dst.stat().st_mtime < png.stat().st_mtime:
                im2 = im.convert("RGB") if im.mode not in ("RGB", "RGBA") else im
                if w > width:
                    im2 = im2.resize((width, round(h * width / w)), Image.LANCZOS)
                im2.save(dst, "WEBP", quality=82, method=6)
        if png.name in covers or "cover" in stem:
            og = out / f"{stem}-og.jpg"
            if not og.exists() or og.stat().st_mtime < png.stat().st_mtime:
                rgb = im.convert("RGB")
                target = 1200 / 630
                if w / h > target:
                    nw = round(h * target)
                    rgb = rgb.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
                else:
                    nh = round(w / target)
                    rgb = rgb.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
                rgb.resize((1200, 630), Image.LANCZOS).save(og, "JPEG", quality=86, optimize=True, progressive=True)
    return sizes


def img_tag(series: dict, name: str, alt: str, sizes: dict, *, eager: bool = False, sizes_attr: str = "(max-width: 860px) 100vw, 760px") -> str:
    stem = Path(name).stem
    base = f"/articles/assets/{series['slug']}/{stem}"
    w, h = sizes.get(Path(name).name, (1600, 900))
    disp_w = min(w, 1600)
    disp_h = round(h * disp_w / w)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (
        f'<img src="{base}-1600.webp" srcset="{base}-800.webp 800w, {base}-1600.webp 1600w" '
        f'sizes="{sizes_attr}" width="{disp_w}" height="{disp_h}" alt="{esc(alt)}" {load} decoding="async" />'
    )


# --------------------------------------------------------------------------- conversion
def link_for(stem: str, lang: str, series: dict) -> str:
    if stem.startswith("00-"):
        return ("/ar" if lang == "ar" else "") + "/articles/#roadmap"
    for a in series["articles"]:
        for lg, f in a["files"].items():
            if Path(f).stem == stem:
                return ("/ar" if lg == "ar" else "") + f"/articles/{a['slug']}/"
    return ("/ar" if lang == "ar" else "") + "/articles/"


def preprocess(md: str, lang: str, series: dict, sizes: dict, blocks: list) -> str:
    lines = md.split("\n")
    # Drop H1 + the metadata/cover lines directly under it (rendered by the page template).
    h1 = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
    if h1 is not None:
        j = h1 + 1
        while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith("**") or lines[j].strip().startswith("![[")):
            j += 1
        del lines[h1:j]

    out: list[str] = []
    i = 0

    def take_caption(k: int) -> tuple[str, int]:
        m = k
        while m < len(lines) and not lines[m].strip():
            m += 1
        if m < len(lines):
            s = lines[m].strip()
            if s.startswith("*") and s.endswith("*") and not s.startswith("**") and not s.startswith("* "):
                return s[1:-1].strip(), m + 1
        return "", k

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```mermaid") or s == "$$":
            kind = "mermaid" if s.startswith("```") else "math"
            end_marker = "```" if kind == "mermaid" else "$$"
            j = i + 1
            while j < len(lines) and lines[j].strip() != end_marker:
                j += 1
            source = "\n".join(lines[i + 1 : j])
            caption, nxt = take_caption(j + 1) if kind == "mermaid" else ("", j + 1)
            blocks.append({"kind": kind, "source": source, "caption": caption})
            out += ["", f"@@BLOCK{len(blocks) - 1}@@", ""]
            i = nxt
            continue
        m = re.fullmatch(r"!\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", s)
        if m:
            caption, nxt = take_caption(i + 1)
            blocks.append({"kind": "image", "source": m.group(1), "caption": caption})
            out += ["", f"@@BLOCK{len(blocks) - 1}@@", ""]
            i = nxt
            continue
        out.append(line)
        i += 1

    text = "\n".join(out)
    text = re.sub(
        r"(?<!!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]",
        lambda m: f"[{m.group(2) or m.group(1)}]({link_for(m.group(1).strip(), lang, series)})",
        text,
    )
    return text


def convert_callouts(h: str, lang: str) -> str:
    pat = re.compile(r"<blockquote>\s*<p>\[!(\w+)\][ \t]*([^\n]*?)(\n|</p>)")
    while (m := pat.search(h)):
        kind = m.group(1).lower()
        title = m.group(2).strip() or CALLOUT_DEFAULTS.get(kind, ("Note", "ملاحظة"))[0 if lang == "en" else 1]
        depth, pos = 1, m.end()
        tag = re.compile(r"<(/?)blockquote>")
        for t in tag.finditer(h, pos):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                close = t
                break
        rest = h[m.end() : close.start()]
        if m.group(3) == "\n":
            rest = "<p>" + rest
        rest = rest.strip()
        if rest in ("<p></p>", "<p>"):
            rest = ""
        block = (
            f'<aside class="callout callout--{esc(kind)}" role="note">'
            f'<p class="callout__title"><span class="callout__icon" aria-hidden="true"></span>{title}</p>{rest}</aside>'
        )
        h = h[: m.start()] + block + h[close.end() :]
    return h


def finish_html(h: str, art: Article, series: dict, sizes: dict, blocks: list, rendered: dict) -> str:
    def block_html(idx: int) -> str:
        b = blocks[idx]
        cap = MD.renderInline(b["caption"]) if b["caption"] else ""
        figcap = f"<figcaption>{cap}</figcaption>" if cap else ""
        if b["kind"] == "mermaid":
            svg = best_svg(rendered, b["source"])
            label = esc(text_of(cap)) if cap else ("Diagram" if art.lang == "en" else "مخطط")
            return f'<figure class="fig fig--diagram"><div class="diagram" dir="ltr" role="img" aria-label="{label}">{svg}</div>{figcap}</figure>'
        if b["kind"] == "math":
            return f'<div class="math" dir="ltr">{rendered[key_for("math", b["source"])]}</div>'
        alt = text_of(cap) if cap else Path(b["source"]).stem.replace("-", " ")
        alt = re.sub(r"^(Figure|الشكل)\s*\d+\s*[—–-]\s*", "", alt)
        return f'<figure class="fig fig--image">{img_tag(series, b["source"], alt, sizes)}{figcap}</figure>'

    h = re.sub(r"<p>@@BLOCK(\d+)@@</p>", lambda m: block_html(int(m.group(1))), h)
    h = convert_callouts(h, art.lang)
    # Tables scroll on narrow screens
    h = re.sub(r"<table>", '<div class="table-wrap" tabindex="0"><table>', h)
    h = h.replace("</table>", "</table></div>")
    # External links
    h = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', h)
    # Footnotes: readable back-links and placement under the References heading
    h = h.replace("↩︎", '<span aria-hidden="true">↑</span>').replace(
        'class="footnote-backref"', 'class="footnote-backref" aria-label="' + ("Back to text" if art.lang == "en" else "العودة إلى النص") + '"'
    )
    fn = re.search(r'<hr class="footnotes-sep"\s*/?>\s*(<section class="footnotes">.*?</section>)', h, re.S)
    if fn:
        section = fn.group(1)
        h = h[: fn.start()] + h[fn.end() :]
        heads = list(re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', h))
        ref_head = next(
            (x for x in reversed(heads) if re.search(r"referen|sources|further reading|المراجع|مصادر|المصادر", text_of(x.group(2)), re.I)),
            None,
        )
        if ref_head:
            h = h[: ref_head.end()] + section + h[ref_head.end() :]
        else:
            title = UI[art.lang]["references"]
            h += f'<h2 id="references">{title}</h2>{section}'
    # Heading anchors (hover permalink)
    h = re.sub(
        r'<(h[23]) id="([^"]+)">(.*?)</\1>',
        lambda m: f'<{m.group(1)} id="{m.group(2)}">{m.group(3)}<a class="anchor" href="#{m.group(2)}" aria-hidden="true" tabindex="-1">#</a></{m.group(1)}>',
        h,
    )
    return h


def load_article(a: dict, lang: str, series: dict, sizes: dict) -> tuple[Article, list]:
    src = (ROOT / series["source_dir"] / a["files"][lang]).read_text(encoding="utf-8")
    _, fm_raw, body = src.split("---", 2)
    fm = yaml.safe_load(fm_raw)
    abstract = re.search(r"^> \[!abstract\][^\n]*\n((?:>.*\n?)+)", body, re.M)
    desc = strip_md(re.sub(r"^>\s?", "", abstract.group(1), flags=re.M)) if abstract else series["description"][lang]
    level = UI[lang]["level_map"].get(str(fm.get("level", "")), str(fm.get("level", "")))
    art = Article(
        meta=fm, lang=lang, slug=a["slug"], n=a["n"], title=str(fm["title"]).strip(),
        description=desc, level=level, date=str(fm.get("date", TODAY)),
        cover=Path(fm.get("cover", series["cover"])).name, tags=list(fm.get("tags", [])),
    )
    if abstract:  # shown as the hero introduction — don't repeat it as the first callout
        body = body[: abstract.start()] + body[abstract.end() :]
    blocks: list = []
    pre = preprocess(body, lang, series, sizes, blocks)
    return art, [pre, blocks]


# --------------------------------------------------------------------------- page chrome
def head(*, lang: str, title: str, description: str, path: str, alt_path: str, image: str, image_alt: str,
         og_type: str, jsonld: list, extra_meta: str = "", css_extra: bool = True, feed: str = "") -> str:
    url = SITE + path
    other = "ar" if lang == "en" else "en"
    en_path, ar_path = (path, alt_path) if lang == "en" else (alt_path, path)
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in jsonld)
    return f"""<!doctype html>
<!-- Generated by tools/build.py — edit the Markdown source, not this file. -->
<html lang="{lang}" dir="{'rtl' if lang == 'ar' else 'ltr'}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <meta name="author" content="Ibrahim Alobaid" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="theme-color" content="#0E0D0B" />
  <meta name="color-scheme" content="dark" />
  <link rel="canonical" href="{url}" />
  <link rel="alternate" hreflang="en" href="{SITE + en_path}" />
  <link rel="alternate" hreflang="ar" href="{SITE + ar_path}" />
  <link rel="alternate" hreflang="x-default" href="{SITE + en_path}" />
  {f'<link rel="alternate" type="application/rss+xml" title="Ibrahim Alobaid — Articles" href="{feed}" />' if feed else ''}
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="Ibrahim Alobaid" />
  <meta property="og:url" content="{url}" />
  <meta property="og:locale" content="{'ar_AR' if lang == 'ar' else 'en_US'}" />
  <meta property="og:locale:alternate" content="{'en_US' if lang == 'ar' else 'ar_AR'}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:image" content="{SITE + image}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{esc(image_alt)}" />
  {extra_meta}
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />
  <meta name="twitter:image" content="{SITE + image}" />
  <link rel="icon" href="/favicon.ico" sizes="48x48" />
  <link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{FONTS}" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/css/styles.css" />
  {'<link rel="stylesheet" href="/assets/css/articles.css" />' if css_extra else ''}
  <script>document.documentElement.classList.add('js');</script>
  {ld}
</head>"""


def nav(lang: str, alt_path: str) -> str:
    t = UI[lang]
    p = "/ar" if lang == "ar" else ""
    other_lang = "en" if lang == "ar" else "ar"
    return f"""
<body class="page-articles">
  <a class="skip-link" href="#main">{t['skip']}</a>
  <div class="read-progress" aria-hidden="true"><span></span></div>
  <header class="nav is-scrolled" id="nav">
    <div class="wrap nav__inner">
      <a class="nav__brand" href="{p}/" aria-label="{esc(t['backHome'])}">
        <span class="monogram" aria-hidden="true">IA</span>
        <span class="nav__name">{'إبراهيم العبيد' if lang == 'ar' else 'Ibrahim Alobaid'}</span>
      </a>
      <nav aria-label="Primary">
        <ul class="nav__links" id="nav-links">
          <li><a href="{p}/#about">{t['about']}</a></li>
          <li><a href="{p}/#work">{t['work']}</a></li>
          <li><a href="{p}/#talks">{t['talks']}</a></li>
          <li><a href="{p}/articles/" class="is-active" aria-current="page">{t['articles']}</a></li>
          <li><a href="{p}/#faq">{t['faqNav']}</a></li>
          <li><a href="{p}/#contact">{t['contact']}</a></li>
        </ul>
      </nav>
      <div class="nav__actions">
        <a class="lang-toggle" href="{alt_path}" hreflang="{other_lang}" lang="{other_lang}" aria-label="{esc(t['langLabel'])}">{t['langShort']}</a>
        <button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="Menu"><span></span><span></span></button>
      </div>
    </div>
  </header>"""


def footer(lang: str) -> str:
    p = "/ar" if lang == "ar" else ""
    top = "العودة للأعلى ↑" if lang == "ar" else "Back to top ↑"
    return f"""
  <footer class="footer">
    <div class="wrap footer__inner">
      <a class="footer__brand" href="{p}/"><span class="monogram" aria-hidden="true">IA</span><span>© {TODAY[:4]} Ibrahim Alobaid</span></a>
      <span class="footer__ar" lang="ar">نبني الذكاء، ونبني من يبنيه</span>
      <a class="link-u" href="#top">{top}</a>
    </div>
  </footer>
  <script src="/assets/js/main.js" defer></script>
  <script src="/assets/js/articles.js" defer></script>
</body>
</html>
"""


PERSON = {"@type": "Person", "@id": f"{SITE}/#person", "name": "Ibrahim Alobaid", "alternateName": "إبراهيم العبيد", "url": f"{SITE}/"}


def series_ld(series: dict, lang: str) -> dict:
    return {
        "@type": "CreativeWorkSeries",
        "@id": f"{SITE}/articles/#{series['slug']}",
        "name": series["name"][lang],
        "description": series["description"][lang],
        "author": {"@id": f"{SITE}/#person"},
        "inLanguage": lang,
    }


def breadcrumb_ld(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + path} for i, (name, path) in enumerate(items)
        ],
    }


# --------------------------------------------------------------------------- article page
def article_page(art: Article, other: Article, series: dict, published: list[Article], faqs: list, sizes: dict) -> str:
    t = UI[art.lang]
    lang = art.lang
    p = "/ar" if lang == "ar" else ""
    total = len(series["roadmap"])
    cover_alt = art.title
    og_image = f"/articles/assets/{series['slug']}/{Path(art.cover).stem}-og.jpg"
    seo_title = f"{art.title} | {series['short'][lang]} {art.n:02d}"
    desc = clip(art.description)

    faq_items = "".join(
        f'<details class="faq__item"{" open" if i == 0 else ""}><summary><span class="faq__q">{esc(f["q"])}</span>'
        f'<span class="faq__icon" aria-hidden="true"></span></summary><div class="faq__a"><p>{esc(f["a"])}</p></div></details>'
        for i, f in enumerate(faqs)
    )
    code_files = next(a for a in series["articles"] if a["slug"] == art.slug)["code"]
    lab = ""
    if code_files:
        rows = "".join(
            f'<li><a href="/articles/code/{series["slug"]}/{f}" download><span class="lab__file" dir="ltr">{f}</span>'
            f'<span class="lab__dl">{t["download"]} ↓</span></a></li>'
            for f in code_files
        )
        lab = f'<section class="post-lab" aria-labelledby="lab-title"><h2 id="lab-title">{t["labTitle"]}</h2><p>{t["labText"]}</p><ul class="lab__files">{rows}</ul></section>'

    idx = [a.slug for a in published].index(art.slug)
    prev_a = published[idx - 1] if idx > 0 else None
    next_a = published[idx + 1] if idx + 1 < len(published) else None

    def pn(a: Article | None, label: str, cls: str) -> str:
        if not a:
            return f'<span class="pn pn--empty {cls}"></span>'
        return (
            f'<a class="pn {cls}" href="{a.path}"><span class="pn__label caps">{label}</span>'
            f'<span class="pn__n">{a.n:02d}</span><span class="pn__title">{esc(a.title)}</span></a>'
        )

    roadmap_html = roadmap_list(series, lang, {a.n: a for a in published}, current=art.n)

    toc = "".join(f'<li><a href="#{hid}">{esc(text)}</a></li>' for hid, text in art.toc)
    level = f'<span class="meta-chip">{t["level"]}: {esc(art.level)}</span>' if art.level else ""

    article_ld = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "@id": art.url + "#article",
        "headline": art.title[:110],
        "description": desc,
        "image": [SITE + og_image, f"{SITE}/articles/assets/{series['slug']}/{Path(art.cover).stem}-1600.webp"],
        "datePublished": art.date,
        "dateModified": TODAY,
        "author": PERSON,
        "publisher": PERSON,
        "inLanguage": lang,
        "mainEntityOfPage": art.url,
        "url": art.url,
        "wordCount": art.words,
        "timeRequired": f"PT{art.minutes}M",
        "proficiencyLevel": str(art.meta.get("level", "")),
        "keywords": ", ".join(dict.fromkeys(next(a for a in series["articles"] if a["slug"] == art.slug)["keywords"] + art.tags)),
        "isPartOf": series_ld(series, lang),
        "position": art.n,
        "translationOfWork" if lang == "ar" else "workTranslation": {"@id": other.url + "#article"},
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": lang,
        "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs],
    }
    crumbs = [(t["home"], f"{p}/"), (t["articles"], f"{p}/articles/"), (art.title, art.path)]
    extra = (
        f'<meta property="article:published_time" content="{art.date}" />\n'
        f'  <meta property="article:modified_time" content="{TODAY}" />\n'
        f'  <meta property="article:author" content="{SITE}/" />\n'
        f'  <meta property="article:section" content="{esc(series["short"][lang])}" />\n'
        + "".join(f'  <meta property="article:tag" content="{esc(tag)}" />\n' for tag in art.tags[:6])
    )
    page = head(
        lang=lang, title=seo_title, description=desc, path=art.path, alt_path=other.path, image=og_image,
        image_alt=art.title, og_type="article", jsonld=[article_ld, breadcrumb_ld(crumbs), faq_ld], extra_meta=extra,
        feed=f"{p}/articles/feed.xml",
    )
    page += nav(lang, other.path)
    page += f"""
  <main id="main">
    <article class="post" id="top">
      <header class="post-hero">
        <div class="post-hero__pattern pattern" aria-hidden="true"></div>
        <div class="wrap post-hero__inner">
          <nav class="crumbs" aria-label="{t['breadcrumb']}">
            <ol><li><a href="{p}/">{t['home']}</a></li><li><a href="{p}/articles/">{t['articles']}</a></li><li><a href="{p}/articles/#roadmap">{esc(series['short'][lang])}</a></li></ol>
          </nav>
          <p class="post-hero__series caps"><span>{esc(series['short'][lang])}</span><span class="dot" aria-hidden="true"></span><span>{t['articleOf'].format(n=f'{art.n:02d}', total=total)}</span></p>
          <h1 class="post-hero__title">{esc(art.title)}</h1>
          <p class="post-hero__dek">{esc(art.description)}</p>
          <div class="post-meta">
            <a class="post-meta__author" href="{p}/#about"><img src="/assets/img/ibrahim-alobaid.jpg" width="44" height="44" alt="" loading="lazy" /><span><strong>{'إبراهيم العبيد' if lang == 'ar' else 'Ibrahim Alobaid'}</strong><span>{t['authorRole'].split(' · ')[0]}</span></span></a>
            <span class="post-meta__facts">
              <span><time datetime="{art.date}">{fmt_date(art.date, lang)}</time></span>
              <span>{art.minutes} {t['minRead']}</span>
              {level}
            </span>
            <a class="post-meta__lang" href="{other.path}" hreflang="{other.lang}" lang="{other.lang}">{t['readOther']} →</a>
          </div>
        </div>
      </header>

      <figure class="post-cover wrap">
        {img_tag(series, art.cover, cover_alt, sizes, eager=True, sizes_attr="(max-width: 1240px) 100vw, 1240px")}
      </figure>

      <div class="post-layout wrap">
        <aside class="toc" aria-label="{t['onThisPage']}">
          <details class="toc__box" open>
            <summary class="caps">{t['onThisPage']}</summary>
            <ol>{toc}</ol>
          </details>
        </aside>

        <div class="prose" data-copy="{t['copy']}" data-copied="{t['copied']}">
{art.body_html}
          {lab}
          <section class="post-faq" id="faq" aria-labelledby="faq-title">
            <p class="caps gold">Q&amp;A</p>
            <h2 id="faq-title">{t['faqTitle']}</h2>
            <p class="post-faq__lede">{t['faqLede']}</p>
            <div class="faq">{faq_items}</div>
          </section>

          <aside class="author-box" aria-label="{t['writtenBy']}">
            <img src="/assets/img/ibrahim-alobaid.jpg" width="96" height="96" alt="{'إبراهيم العبيد' if lang == 'ar' else 'Ibrahim Alobaid'}" loading="lazy" />
            <div>
              <p class="caps gold">{t['writtenBy']}</p>
              <p class="author-box__name">{'إبراهيم العبيد' if lang == 'ar' else 'Ibrahim Alobaid'}</p>
              <p class="author-box__role">{t['authorRole']}</p>
              <p class="author-box__bio">{t['authorBio']}</p>
              <p class="author-box__links"><a href="{p}/" class="link-u">ibrahim-dev.me</a><a href="https://www.linkedin.com/in/ibrahimalobaid44/" target="_blank" rel="noopener" class="link-u">LinkedIn</a><a href="https://github.com/IbrahimAlobid2" target="_blank" rel="noopener" class="link-u">GitHub</a></p>
            </div>
          </aside>
        </div>
      </div>

      <div class="wrap">
        <nav class="pn-wrap" aria-label="{t['prev']} / {t['next']}">
          {pn(prev_a, t['prev'], 'pn--prev')}
          {pn(next_a, t['next'], 'pn--next')}
        </nav>
      </div>

      <section class="series-box wrap" aria-labelledby="roadmap-title">
        <p class="caps gold">{t['roadmap']}</p>
        <h2 id="roadmap-title" class="series-box__title">{esc(series['name'][lang])}</h2>
        {roadmap_html}
      </section>
    </article>
  </main>"""
    page += footer(lang)
    return page


def roadmap_list(series: dict, lang: str, published: dict, current: int | None = None) -> str:
    t = UI[lang]
    groups = []
    for lvl, names in series["levels"].items():
        items = []
        for r in series["roadmap"]:
            if str(r["level"]) != lvl:
                continue
            a = published.get(r["n"])
            num = f'<span class="rm__n">{r["n"]:02d}</span>'
            if a:
                cur = ' aria-current="page"' if current == r["n"] else ""
                items.append(f'<li class="rm__item is-live{" is-current" if current == r["n"] else ""}"><a href="{a.path}"{cur}>{num}<span class="rm__t">{esc(r[lang])}</span></a></li>')
            else:
                items.append(f'<li class="rm__item"><span>{num}<span class="rm__t">{esc(r[lang])}</span><span class="rm__soon">{t["soon"]}</span></span></li>')
        groups.append(f'<div class="rm__group"><p class="rm__level caps">{esc(names[lang])}</p><ol class="rm__list">{"".join(items)}</ol></div>')
    return f'<div class="rm">{"".join(groups)}</div>'


# --------------------------------------------------------------------------- index page
def index_page(series: dict, lang: str, published: list[Article], sizes: dict) -> str:
    t = UI[lang]
    p = "/ar" if lang == "ar" else ""
    alt = "/articles/" if lang == "ar" else "/ar/articles/"
    path = f"{p}/articles/"
    total = len(series["roadmap"])
    cards = "".join(
        f"""<article class="acard">
          <a class="acard__link" href="{a.path}">
            <div class="acard__img">{img_tag(series, a.cover, a.title, sizes, sizes_attr="(max-width: 720px) 100vw, 400px")}</div>
            <div class="acard__body">
              <p class="acard__n caps">{t['articleOf'].format(n=f'{a.n:02d}', total=total)}</p>
              <h3 class="acard__title">{esc(a.title)}</h3>
              <p class="acard__desc">{esc(clip(a.description, 170))}</p>
              <p class="acard__meta"><span>{a.minutes} {t['minRead']}</span><span>{esc(a.level)}</span></p>
            </div>
          </a>
        </article>"""
        for a in published
    )
    first = published[0]
    desc = clip(series["description"][lang])
    item_list = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": SITE + path + "#page",
        "url": SITE + path,
        "name": f"{t['articles']} — Ibrahim Alobaid",
        "description": desc,
        "inLanguage": lang,
        "author": PERSON,
        "hasPart": series_ld(series, lang),
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": a.url, "name": a.title} for i, a in enumerate(published)],
        },
    }
    crumbs = [(t["home"], f"{p}/"), (t["articles"], path)]
    title = f"{t['articles']} — {series['short'][lang]} | {'إبراهيم العبيد' if lang == 'ar' else 'Ibrahim Alobaid'}"
    page = head(
        lang=lang, title=title, description=desc, path=path, alt_path=alt,
        image=f"/articles/assets/{series['slug']}/{Path(series['cover']).stem}-og.jpg", image_alt=series["name"][lang],
        og_type="website", jsonld=[item_list, breadcrumb_ld(crumbs)], feed=f"{p}/articles/feed.xml",
    )
    page += nav(lang, alt)
    page += f"""
  <main id="main">
    <header class="ahub-hero" id="top">
      <div class="post-hero__pattern pattern" aria-hidden="true"></div>
      <div class="wrap">
        <nav class="crumbs" aria-label="{t['breadcrumb']}"><ol><li><a href="{p}/">{t['home']}</a></li><li aria-current="page">{t['articles']}</li></ol></nav>
        <p class="caps gold">{t['indexEyebrow']}</p>
        <h1 class="ahub-hero__title display">{t['indexTitle']}</h1>
        <p class="ahub-hero__lede">{t['indexLede']}</p>
      </div>
    </header>

    <section class="wrap series-feature" aria-labelledby="series-title">
      <a class="series-feature__img" href="{first.path}">{img_tag(series, series['cover'], series['name'][lang], sizes, eager=True, sizes_attr="(max-width: 920px) 100vw, 640px")}</a>
      <div class="series-feature__body">
        <p class="caps gold">{t['series']} · {t['publishedCount'].format(n=len(published), total=total)}</p>
        <h2 id="series-title" class="series-feature__title">{esc(series['name'][lang])}</h2>
        <p class="series-feature__desc">{esc(series['description'][lang])}</p>
        <p class="series-feature__aud"><span class="caps">{t['audience']}</span>{esc(series['audience'][lang])}</p>
        <div class="series-feature__progress" role="img" aria-label="{t['publishedCount'].format(n=len(published), total=total)}"><span style="width:{len(published) / total * 100:.1f}%"></span></div>
        <a class="btn btn--solid" href="{first.path}"><span>{t['start']}</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M4 12h16M14 6l6 6-6 6"/></svg></a>
      </div>
    </section>

    <section class="wrap acards-wrap" aria-labelledby="all-title">
      <h2 id="all-title" class="caps acards-wrap__title">{t['allArticles']}</h2>
      <div class="acards">{cards}</div>
    </section>

    <section class="wrap series-box" id="roadmap" aria-labelledby="roadmap-title">
      <p class="caps gold">{t['roadmap']}</p>
      <h2 id="roadmap-title" class="series-box__title">{esc(series['name'][lang])}</h2>
      {roadmap_list(series, lang, {a.n: a for a in published})}
    </section>
  </main>"""
    page += footer(lang)
    return page


# --------------------------------------------------------------------------- home cards + feed
def home_cards(series: dict, lang: str, published: list[Article], sizes: dict) -> str:
    t = UI[lang]
    p = "/ar" if lang == "ar" else ""
    total = len(series["roadmap"])
    rows = "".join(
        f'<li><a href="{a.path}"><span class="wl__n">{a.n:02d}</span><span class="wl__t">{esc(a.title)}</span>'
        f'<span class="wl__m">{a.minutes} {t["minRead"]}</span></a></li>'
        for a in published
    )
    return f"""<div class="writing">
          <a class="writing__feature reveal" href="{p}/articles/">
            <div class="writing__img">{img_tag(series, series['cover'], series['name'][lang], sizes, sizes_attr="(max-width: 920px) 100vw, 560px")}</div>
            <div class="writing__body">
              <p class="caps gold">{t['series']} · {t['publishedCount'].format(n=len(published), total=total)}</p>
              <h3 class="writing__title">{esc(series['name'][lang])}</h3>
              <p class="writing__desc">{esc(series['description'][lang])}</p>
            </div>
          </a>
          <ol class="writing__list reveal" data-delay="1">{rows}</ol>
        </div>"""


def feed(series: dict, lang: str, published: list[Article]) -> str:
    p = "/ar" if lang == "ar" else ""
    items = "".join(
        f"""  <item>
    <title>{esc(a.title)}</title>
    <link>{a.url}</link>
    <guid isPermaLink="true">{a.url}</guid>
    <pubDate>{dt.datetime.fromisoformat(a.date).strftime('%a, %d %b %Y 09:00:00 +0000')}</pubDate>
    <description>{esc(clip(a.description, 300))}</description>
    <category>{esc(series['short'][lang])}</category>
  </item>
"""
        for a in reversed(published)
    )
    title = "مقالات إبراهيم العبيد" if lang == "ar" else "Ibrahim Alobaid — Articles"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{title}</title>
  <link>{SITE}{p}/articles/</link>
  <atom:link href="{SITE}{p}/articles/feed.xml" rel="self" type="application/rss+xml" />
  <description>{esc(series['description'][lang])}</description>
  <language>{lang}</language>
  <lastBuildDate>{dt.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
{items}</channel>
</rss>
"""


# --------------------------------------------------------------------------- entry point
def build() -> dict:
    series = json.loads((ROOT / "src" / "articles" / "series.json").read_text(encoding="utf-8"))
    faqs = json.loads((ROOT / "src" / "articles" / "faqs.json").read_text(encoding="utf-8"))
    sizes = process_images(series)

    # Lab files
    code_dir = ROOT / "articles" / "code" / series["slug"]
    code_dir.mkdir(parents=True, exist_ok=True)
    for a in series["articles"]:
        for f in a["code"]:
            shutil.copy2(ROOT / series["source_dir"] / "examples" / f, code_dir / f)

    loaded: dict[str, list[tuple[Article, list]]] = {"en": [], "ar": []}
    render_items = []
    for a in series["articles"]:
        for lang in ("en", "ar"):
            art, (pre, blocks) = load_article(a, lang, series, sizes)
            loaded[lang].append((art, [pre, blocks]))
            render_items += [(b["kind"], b["source"]) for b in blocks if b["kind"] in ("mermaid", "math")]
    rendered = render_all(render_items)

    published: dict[str, list[Article]] = {"en": [], "ar": []}
    for lang in ("en", "ar"):
        for art, (pre, blocks) in loaded[lang]:
            body = MD.render(pre)
            body = finish_html(body, art, series, sizes, blocks, rendered)
            art.body_html = body
            art.toc = [(m.group(1), text_of(re.sub(r'<a class="anchor".*?</a>', "", m.group(2))))
                       for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body)]
            plain = text_of(re.sub(r"<pre.*?</pre>|<svg.*?</svg>|<math.*?</math>", " ", body, flags=re.S))
            art.words = len(plain.split())
            art.minutes = max(1, round(art.words / (180 if lang == "ar" else 220)))
            published[lang].append(art)

    by_slug = {lang: {a.slug: a for a in published[lang]} for lang in published}
    for lang in ("en", "ar"):
        other = "ar" if lang == "en" else "en"
        base = ROOT / ("ar" if lang == "ar" else "") / "articles"
        for art in published[lang]:
            out = base / art.slug / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(
                article_page(art, by_slug[other][art.slug], series, published[lang], faqs[art.slug][lang], sizes),
                encoding="utf-8",
            )
        base.mkdir(parents=True, exist_ok=True)
        (base / "index.html").write_text(index_page(series, lang, published[lang], sizes), encoding="utf-8")
        (base / "feed.xml").write_text(feed(series, lang, published[lang]), encoding="utf-8")

    pages = [("/articles/", "/ar/articles/", f"/articles/assets/{series['slug']}/{Path(series['cover']).stem}-og.jpg")]
    pages += [
        (a.path, by_slug["ar"][a.slug].path, f"/articles/assets/{series['slug']}/{Path(a.cover).stem}-og.jpg")
        for a in published["en"]
    ]
    return {
        "pages": pages,
        "urls": [SITE + x for pair in pages for x in pair[:2]],
        "home_cards": {lang: home_cards(series, lang, published[lang], sizes) for lang in ("en", "ar")},
        "llms": [(a.title, a.url, by_slug["ar"][a.slug].title, by_slug["ar"][a.slug].url) for a in published["en"]],
    }

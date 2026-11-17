#!/usr/bin/env python3
"""Build the website into _site/.

Content lives in content/ (Markdown pages with YAML front matter, plus YAML
data files), page templates in templates/, and static files in static/ and
assets/. Pages are rendered with Jinja2 first, so they can call the macros in
templates/macros.html, and then converted from Markdown to HTML.

    python build.py            # build into _site/
    python build.py --serve    # build, then preview at http://localhost:8000
"""

import argparse
import datetime as dt
import functools
import html
import http.server
import re
import shutil
import socketserver
from pathlib import Path

import jinja2
import markdown
import yaml
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
OUT = ROOT / "_site"
COPY_DIRS = ["static", "assets"]
COPY_FILES = ["CNAME", "favicon.ico"]

MD_EXTENSIONS = ["extra", "sane_lists", "toc"]
MD_CONFIG = {"toc": {"permalink": False, "toc_depth": "2-3"}}

try:  # Pillow is optional; it lets the build add width/height to images.
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


# ---------------------------------------------------------------- helpers

def read_front_matter(path):
    """Split a Markdown file into (metadata dict, body text)."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        _, meta, body = text.split("---", 2)
        return yaml.safe_load(meta) or {}, body.lstrip("\n")
    return {}, text


def md_block(text):
    return markdown.markdown(text or "", extensions=MD_EXTENSIONS, extension_configs=MD_CONFIG)


def md_inline(text):
    """Markdown for short strings (captions, summaries) without the <p> wrapper."""
    out = md_block(text).strip()
    if out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1:
        out = out[3:-4]
    return out


def load_data():
    data = {}
    for path in sorted((CONTENT / "data").glob("*.yml")):
        data[path.stem] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data


def output_path(permalink):
    rel = permalink.strip("/")
    if not rel:
        return OUT / "index.html"
    if rel.endswith(".html") or rel.endswith(".xml") or rel.endswith(".txt"):
        return OUT / rel
    return OUT / rel / "index.html"


@functools.lru_cache(maxsize=None)
def image_size(src):
    if Image is None or not src.startswith("/"):
        return None
    path = ROOT / src.lstrip("/")
    if not path.exists() or path.suffix.lower() == ".svg":
        return None
    with Image.open(path) as im:
        return im.size


IMG_TAG = re.compile(r"<img\b([^>]*?)\s*/?>")


def add_image_sizes(page_html):
    """Give every local <img> explicit width/height so the layout does not jump."""

    def fix(match):
        attrs = match.group(1)
        if " width=" in attrs:
            return match.group(0)
        src = re.search(r'src="([^"]+)"', attrs)
        size = image_size(src.group(1)) if src else None
        if not size:
            return match.group(0)
        return f'<img{attrs} width="{size[0]}" height="{size[1]}">'

    return IMG_TAG.sub(fix, page_html)


# ---------------------------------------------------------------- build

def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in COPY_DIRS:
        if (ROOT / name).exists():
            shutil.copytree(ROOT / name, OUT / name)
    for name in COPY_FILES:
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, OUT / name)
    (OUT / ".nojekyll").write_text("")

    site = yaml.safe_load((ROOT / "site.yml").read_text(encoding="utf-8"))
    site["build_date"] = dt.date.today()
    data = load_data()

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATES)),
        autoescape=jinja2.select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["md"] = lambda s: Markup(md_block(s))
    env.filters["mdi"] = lambda s: Markup(md_inline(s))
    env.filters["date_fmt"] = lambda d, fmt="%b %Y": d.strftime(fmt) if hasattr(d, "strftime") else d
    env.globals.update(site=site, data=data)

    pages = []
    for path in sorted((CONTENT / "pages").glob("*.md")):
        meta, body = read_front_matter(path)
        meta.setdefault("template", "page.html")
        meta.setdefault("permalink", f"/{path.stem}/")
        pages.append((path, meta, body))

    for path, meta, body in pages:
        # 1) Jinja pass, so pages can use macros and data.
        source = '{% import "macros.html" as m %}\n' + body
        rendered = env.from_string(source).render(page=meta)
        # 2) Markdown pass.
        md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs=MD_CONFIG)
        content_html = md.convert(rendered)
        toc = [t for t in md.toc_tokens] if meta.get("toc") else []
        page_html = env.get_template(meta["template"]).render(
            page=meta, content=Markup(content_html), toc=toc
        )
        page_html = add_image_sizes(page_html)
        dest = output_path(meta["permalink"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page_html, encoding="utf-8")

    # Redirects for old URLs, so existing links keep working.
    for old, new in (site.get("redirects") or {}).items():
        dest = output_path(old)
        dest.parent.mkdir(parents=True, exist_ok=True)
        target = html.escape(new)
        dest.write_text(
            f'<!doctype html><meta charset="utf-8"><title>Redirecting</title>'
            f'<link rel="canonical" href="{target}"><meta name="robots" content="noindex">'
            f'<meta http-equiv="refresh" content="0; url={target}">'
            f'<a href="{target}">{target}</a>\n',
            encoding="utf-8",
        )

    # sitemap.xml and robots.txt
    urls = [m["permalink"] for _, m, _ in pages if not m.get("exclude_from_sitemap")]
    today = dt.date.today().isoformat()
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append(f"  <url><loc>{site['url']}{u}</loc><lastmod>{today}</lastmod></url>")
    sitemap.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nDisallow:\n\nSitemap: {site['url']}/sitemap.xml\n", encoding="utf-8"
    )
    print(f"Built {len(pages)} pages into {OUT.relative_to(ROOT)}/")


def serve(port):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving _site/ at http://localhost:{port} (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--serve", action="store_true", help="preview the site after building")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    build()
    if args.serve:
        serve(args.port)

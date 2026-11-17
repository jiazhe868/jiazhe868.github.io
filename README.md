# jiazhe868.github.io

Source of [jiazhe868.github.io](https://jiazhe868.github.io), the personal website of Zhe Jia.

The site is a small static site. `build.py` renders Markdown pages and YAML data into HTML with
Jinja2 templates. GitHub Actions runs the build on every push to `main` and publishes the result
to the `gh-pages` branch, which GitHub Pages serves.

## Layout

```text
.
├── site.yml                 # name, links, navigation, redirects for old URLs
├── content/
│   ├── pages/               # one Markdown file per page (front matter + body)
│   │   ├── index.md         # home page: hero, project cards, about text
│   │   ├── llm.md           # language-model write-up
│   │   ├── sensoformer.md   # Sensoformer project page
│   │   ├── submit.md        # SubMIT project page
│   │   ├── earthquakes.md   # earthquake gallery (cards come from data/studies.yml)
│   │   ├── publications.md  # publication list (entries come from data/publications.yml)
│   │   ├── teaching.md
│   │   └── cv.md
│   └── data/
│       ├── news.yml         # news items, newest first
│       ├── publications.yml # all papers
│       ├── studies.yml      # earthquake gallery entries with plain-language summaries
│       └── trace.yml        # the seismogram drawn on the home page
├── templates/               # Jinja2 templates and macros
├── static/                  # CSS, JavaScript, favicon, social preview image
├── assets/
│   ├── img/                 # figures (WebP) and photos
│   └── pdf/                 # papers and CV
├── tools/prepare_images.py  # converts figures to web-sized WebP
└── build.py                 # the site builder
```

## Common updates

**Add a news item.** Add an entry at the top of `content/data/news.yml`:

```yaml
- date: 2026-12-01
  text: Our paper on ... is published in *Journal*. [Paper](https://doi.org/...)
```

**Add a paper.** Add an entry to `content/data/publications.yml`. Put the PDF in `assets/pdf/`
and set `pdf:` to its path. `story:` can point to a gallery entry, for example
`/earthquakes/#turkey2023`.

**Add an earthquake study to the gallery.** Add an entry to `content/data/studies.yml`. Entries
with `feature: true` get a large row with figures; others appear as compact cards. Convert figures
first:

```bash
python tools/prepare_images.py figure.png assets/img/quakes/name-fig1.webp
```

**Update the CV.** Replace `assets/pdf/CV_Zhe.pdf`.

**Edit a page.** Pages are Markdown with optional macros from `templates/macros.html`, for example
`{{ m.fig('/assets/img/llm/pretrain-scaling.webp', 'Caption', wide=True) }}`.

Edits made directly on GitHub are fine: the site rebuilds automatically after each push.

## Build locally

```bash
pip install -r requirements.txt
python build.py --serve      # http://localhost:8000
```

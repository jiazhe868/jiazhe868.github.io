# Zhe Jia Academic Website

Source code for [jiazhe868.github.io](https://jiazhe868.github.io), the academic homepage of **Zhe Jia**.

This site is built with [Jekyll](https://jekyllrb.com/) and the [al-folio](https://github.com/alshedivat/al-folio) academic theme. It hosts research highlights, publications, news, teaching and mentoring information, selected PDFs, and professional links.

[![Deploy site](https://github.com/jiazhe868/jiazhe868.github.io/actions/workflows/deploy.yml/badge.svg)](https://github.com/jiazhe868/jiazhe868.github.io/actions/workflows/deploy.yml)
[![Website](https://img.shields.io/badge/site-jiazhe868.github.io-blue)](https://jiazhe868.github.io)

## About

The website presents research at the intersection of **AI for Science** and **seismology**, including:

- physics-based solvers and inverse problems,
- Bayesian optimization for geophysical inference,
- multi-modal Transformers and neural operators for seismology,
- earthquake source studies and rupture dynamics,
- teaching and mentoring activities at UT Austin.

The public site is served from GitHub Pages at:

```text
https://jiazhe868.github.io
```

## Repository Structure

The most important files for routine updates are:

```text
.
├── _config.yml              # site title, author info, navigation, theme settings
├── _pages/
│   ├── about.md             # homepage content
│   ├── publications.md      # publication page, generated from BibTeX
│   ├── projects.md          # project page
│   ├── teaching.md          # teaching and mentoring
│   └── news.md              # news archive
├── _bibliography/papers.bib # publications and selected-paper metadata
├── _news/                   # short dated news items on the homepage
├── _data/
│   ├── socials.yml          # email, CV, Scholar, ORCID, LinkedIn, etc.
│   ├── cv.yml               # structured CV data if the CV page is enabled
│   └── citations.yml        # generated Google Scholar citation counts
├── assets/
│   ├── img/                 # profile image and publication/project images
│   └── pdf/                 # CV and paper PDFs
└── .github/workflows/
    ├── deploy.yml           # builds and deploys the site
    └── update-citations.yml # scheduled Scholar citation refresh
```

## Common Updates

### Homepage

Edit:

```text
_pages/about.md
```

This controls the landing page biography, profile image, selected papers, social links, and recent news settings.

### Publications

Edit:

```text
_bibliography/papers.bib
```

Publications are rendered through `jekyll-scholar`. Mark important entries with:

```bibtex
selected={true}
```

to show them in the selected-paper section on the homepage.

### News

Add a Markdown file under:

```text
_news/
```

Example:

```markdown
---
layout: post
date: 2026-01-15 12:00:00-0500
inline: true
---

New paper accepted at ...
```

### Teaching and Mentoring

Edit:

```text
_pages/teaching.md
```

### CV and Social Links

Edit:

```text
_data/socials.yml
assets/pdf/CV_Zhe.pdf
```

The current social metadata includes email, CV PDF, LinkedIn, ORCID, and Google Scholar.

## Local Development

Install Ruby dependencies:

```bash
bundle install
```

Serve locally:

```bash
bundle exec jekyll serve
```

Then open:

```text
http://127.0.0.1:4000
```

For a production-style build:

```bash
JEKYLL_ENV=production bundle exec jekyll build
```

The generated site is written to:

```text
_site/
```

## Deployment

The site is deployed by GitHub Actions via:

```text
.github/workflows/deploy.yml
```

On pushes to `main`, the workflow builds the Jekyll site and deploys `_site/` to GitHub Pages using `JamesIves/github-pages-deploy-action`.

Note: `README.md` is intentionally excluded from the deploy trigger, so README-only changes update the repository front page but do not rebuild the public website.

## Maintenance Notes

- Keep personal/site content in `_pages/`, `_news/`, `_bibliography/`, `_data/`, and `assets/`.
- Avoid editing generated files under `_site/`.
- Keep large PDFs and images reasonably compressed before committing.
- The repository still contains some upstream al-folio helper docs and workflows; the active personal-site content is concentrated in the paths listed above.
- Before major theme changes, test locally with `bundle exec jekyll serve`.

## Credits

This website is based on the excellent [al-folio](https://github.com/alshedivat/al-folio) Jekyll theme for academic websites.

## License

Site content belongs to Zhe Jia unless otherwise noted. The underlying theme and template code follow the licenses inherited from al-folio and included third-party assets.

# Ivanovo

Zola sources for [zderadicka.eu](https://zderadicka.eu), including all 154 posts
and 21 pages from the final WordPress snapshot. Edit Markdown directly; the
WordPress importer is retired. The site is not deployed by these commands.

## Setup

Use Python 3.11+, **Zola 0.23.6** and **Pagefind 1.5.2**. The binary versions are
pinned in `.zola-version` and `.pagefind-version`; both are already installed at
`~/.local/bin/` on this workstation. On another machine, install these versions
from the [Zola releases](https://github.com/getzola/zola/releases) and
[Pagefind releases](https://github.com/Pagefind/pagefind/releases), and put the
binaries on `PATH`.

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Write a new article

Create a draft with a descriptive slug:

```sh
python3 scripts/new_post.py my-new-article --title "My new article"
```

Edit `content/posts/my-new-article/index.md` in VS Code. The generated front matter
looks like this (use the actual publication date):

```toml
+++
title = "My new article"
path = "/my-new-article/"
date = "2026-10-29T12:00:00+00:00"
draft = true
[extra]
kind = "post"
author = "ivan"
categories = ["Programming"]
tags = ["Rust", "WebSocket"]
+++
```

Write a short introduction, then `<!-- more -->`, then the rest of the article.
The introduction becomes the homepage/archive excerpt. Text is UTF-8: write normal
quotes and apostrophes. Label fenced code blocks with their language, for example
`rust`, `python`, or `bash`. Existing migrated code sometimes uses reviewed HTML;
preserve its whitespace and escaping when editing those examples.

Put new images beside `index.md` and reference them with Markdown:

```markdown
![Description of the diagram](diagram.png)
```

Keep media you place beside drafts suitable for public distribution: Zola may copy
page assets independently of draft visibility. Sensitive material belongs outside
the site tree. Existing uploads remain in `static/wp-content/uploads/` so their
public URLs keep working. GitHub gists remain remote script embeds; their code is
not copied locally or included in search.

## Preview and revise

```sh
python3 scripts/preview.py --drafts
```

Open **http://127.0.0.1:1111/**. This builds the site and search index, includes
local drafts, and serves legacy URL redirects and RSS with the right MIME type.
Stop an older server before reusing the port. Use `--port 1112` for another port.

After an edit, stop the preview with Ctrl-C and rerun it to rebuild. There is no
automatic reload. `--no-build` serves the last build only when its URL/draft
settings match. A complete rebuild regenerates summaries, categories, tags,
calendar/author archives, pagination, adjacent-post links, feeds, and search from
the current Markdown. Do not edit `content/_generated/` or `data/site.json`.

Categories and tags are arrays of display labels. Existing labels retain their
historical URLs through `data/taxonomy-slugs.json`; new labels normally derive a
slug automatically. If two labels would share a slug (for example `C++` and `C#`),
add distinct mappings to that file. A build reports the collision instead of
silently merging them.

Edit existing articles in place. Keep their `path` and migrated WordPress ID/GUID
metadata: those preserve inbound links and RSS subscriber identity. Project and
other standalone pages use `extra.kind = "page"`, `include_in_feeds = false`,
and optionally `extra.parent = "/projects/"` and `extra.menu_order = 0`. Parent
paths determine the project navigation hierarchy.

## Prepare an article for publication

1. Set the final date, remove `draft = true` (or set it to `false`), and review
   the title, categories, tags, links, code, and media.
2. Run the production build and review the site without drafts:

   ```sh
   python3 scripts/build_site.py
   python3 scripts/preview.py
   ```

3. Run the regression checks and review your Git diff:

   ```sh
   python3 -m unittest discover -s tests -v
   git diff --check
   git status --short
   ```

4. Commit the Markdown and adjacent media. Include any intentional template,
   stylesheet, script, or taxonomy-map changes.
5. For a release, run `python3 scripts/build_site.py` again after previewing, so
   the artifact uses production URLs and excludes drafts. Deploy **only `public/`**.

The build runs Zola, Pagefind, offline Zola checks, and local route/fragment/feed
validation. External websites are not requested. Production builds exclude draft
articles. Future dates are metadata, not a publication scheduler; use drafts until
ready. Raw `zola build`/`zola serve` omit our archive preparation and Pagefind step;
use the Python commands for complete builds.

For HTTP Docker hosting behind your reverse proxy:

```sh
python3 scripts/prepare_hosting.py
docker compose -f deploy/compose.yaml up -d --wait
```

The backend listens on **http://127.0.0.1:8080/**; your proxy handles HTTPS. It
serves an immutable release with read-only mounts, legacy redirects, RSS types,
compression, and media ranges. Ordinary updates need only `prepare_hosting.py`, with no restart or reload.
A graceful Nginx reload is needed only when legacy redirect mappings change. See [deployment.md](docs/deployment.md) for the exact
commands, Docker proxy-network option, server paths, and manual rollback.
Automatic remote publishing and cutover are not configured.

## Repository layout

- `content/posts/<slug>/index.md`: editable posts and standalone pages.
- `static/`: shared assets, historical media, and attachment redirect pages.
- `templates/`: Tera templates; `static/css/` and `static/js/`: presentation.
- `data/taxonomy-slugs.json`: historical category/tag URL mappings.
- `scripts/`: authoring, build, preview, validation, and local release tools.
- `deploy/`: pinned HTTP container and reverse-proxy network configuration.
- `tests/`: synthetic authoring/publication regression tests.
- `public/`, `.build/`, `content/_generated/`, `data/site.json`: ignored build output.

The accepted snapshot is final; no further WordPress export is needed.
[Migration summary](docs/migration-summary.md) records the completed checks and
cleanup. Backups, importer tools, and working copies are outside the active site;
ordinary authoring never needs them.

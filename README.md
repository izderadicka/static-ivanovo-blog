# Ivanovo

A small Zola blog containing 154 posts and 21 standalone pages from the accepted
WordPress snapshot. Markdown is authoritative. Zola renders the articles, homepage
pagination, year-grouped archive, navigation, sitemap, and main RSS feed directly.
Pagefind adds search. There is no generated content model or archive generator.

## Setup

Use Python 3.11+, Zola **0.23.6**, and Pagefind **1.5.2**. The binary versions are
pinned in `.zola-version` and `.pagefind-version`; put those binaries on `PATH`.

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Write and preview

```sh
python3 scripts/new_post.py my-new-article --title "My new article"
python3 scripts/preview.py --drafts
```

Edit `content/posts/my-new-article/index.md`, then open **http://127.0.0.1:1111/**.
Restart the preview after edits to rebuild search as well as the pages. Use
`--port 1112` for a second preview. Preview always builds fresh output before
serving; there are no saved build settings to manage.

A post needs very little front matter:

```toml
+++
title = "My new article"
path = "/my-new-article/"
date = "2026-10-31T12:00:00+00:00"
draft = true
+++
```

Write a short introduction, then `<!-- more -->`, then the article. Homepage
excerpts use the introduction as plain text, capped at 420 characters. Label
fenced code blocks with their language, such as `python` or `rust`; Zola handles
highlighting. Place new images beside `index.md` and use relative links:

```markdown
![Diagram](diagram.svg)
```

Drafts stay out of production pages, feeds, and search. Colocated media may still
be copied by Zola, so keep private material outside the site tree. Future dates
are metadata, not a publication scheduler: keep `draft = true` until ready.

For faster writing without rebuilding search, `zola serve --drafts` also works
and reloads on edits. Use the Python preview when reviewing search and legacy
query redirects; those are outside Zola's development server.

## Existing content and standalone pages

Keep existing public `path` values, WordPress IDs/GUIDs, source dates, code
whitespace, and media. Historical uploads remain in `static/wp-content/uploads/`.
Gists stay remote GitHub embeds; their code is not downloaded or searched.

Standalone pages live in `content/pages/<slug>/index.md`. Set
`include_in_feeds = false` and `extra.kind = "page"`. An optional `extra.parent`
public path adds the page to its parent's list of subpages. Moving a source
between directories does not change its explicit public URL.

Archives are now a single `/archives/` page grouped by year. The homepage has
native Zola pagination. Category, tag, author, daily, and monthly archive pages
and their feeds are retired; old taxonomy metadata can remain in articles but
is not used for navigation. `/rss.xml` and `/feed/` serve the same main feed,
retaining migrated subscriber GUIDs.

## Publish occasionally

1. Set the final date and remove `draft = true`.
2. Review with `python3 scripts/preview.py`.
3. Build and validate production output:

   ```sh
   python3 scripts/build_site.py
   ```

4. Copy **only `public/`** to your static host. See [deployment.md](docs/deployment.md)
   for the optional Docker server and the simple build-and-copy workflow.

The production build excludes drafts, builds search, and validates local links,
fragments, feed membership, and article coverage. It never publishes remotely.
Always rebuild production after previewing, since previews use local URLs.

For changes to tooling or templates:

```sh
python3 -m unittest discover -s tests -v
git diff --check
```

## Layout

- `content/posts/`: blog posts; `content/pages/`: standalone pages.
- `content/archives/`, `content/search/`: ordinary Zola sections for those views.
- `templates/`, `static/`: rendering, styles, scripts, fonts, and media.
- `scripts/`: draft creation, build checks, and local preview.
- `deploy/`: optional static Nginx server, including a fixed map of old WordPress IDs.
- `public/`, `.build/`: ignored build output and validation reports.

The [migration summary](docs/migration-summary.md) records the original migration.
The accepted snapshot is final; ordinary writing needs no WordPress tools.

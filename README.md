# Technical blog

Zola site with Markdown articles and Python migration tooling for the
existing WordPress content. The templates follow the original WordPress layout, with accessible static-site
navigation and locally served assets. All 175 published WordPress posts/pages are staged under
`migration/work/full-site/`; curated content has not been promoted. See the
[full staging report](docs/full-staging-status.md) and [audit fixes](docs/parity-fixes.md).

## Local workflow

Use **Zola 0.23.6**, pinned in `.zola-version`, from the
[official release](https://github.com/getzola/zola/releases/tag/v0.23.6).
It is installed at `~/.local/bin/zola` in this environment. The scaffold and
full staging site both pass `zola build` and `zola check --skip-external-links`.

```sh
python3 scripts/build_site.py
python3 scripts/preview.py
```

After migration review/promotion, edit Markdown in `content/posts/` using VS Code
and use `zola serve --drafts` for authoring previews. Current migrated content is
still isolated under `migration/work/full-site/`. The example article is a draft
and excluded from production builds. Future articles can use
`content/posts/article-slug/index.md` with adjacent images. Migrated public URLs
will be controlled explicitly rather than inferred from these folder names.

Python tooling targets Python 3.11+:

```sh
python3 -m venv .venv
. .venv/bin/activate
```

Install migration dependencies with `python3 -m pip install -r requirements-migration.txt`.
See [migration commands](scripts/README.md) for inventory, normalization,
conversion, validation, and tests. To preview the full staging site:

```sh
python3 scripts/preview.py
```

## Search and full builds

Use `python3 scripts/build_site.py` to build Zola and its browser-side Pagefind
index together. Zola 0.23.6 and Pagefind 1.5.2 are pinned in `.zola-version` and
`.pagefind-version`; both are installed at `~/.local/bin/` in this environment.
The Python preview above rebuilds with local URLs and serves the complete indexed
site at **http://127.0.0.1:1111**. Stop an older server first. `zola serve` remains
useful for draft authoring but does not regenerate the search index.

Search includes rendered article text, code, and captions. Remote gist contents
are not indexed. Queries remain in the browser; use quotes for an exact phrase
or identifier. Navigation and article content work without JavaScript.

## Planned deployment and publishing

The built site will be mounted read-only into a Docker web-server container.
A Python publishing workflow will build Zola and Pagefind, validate and transfer
an isolated release, then activate it with rollback available. Article updates
will not require rebuilding the serving image. These tools are not implemented yet.
See [deployment and publishing](docs/deployment.md) for the proposed workflow.

## Layout

- `docs/migration-plan.md`: migration phases, acceptance criteria, and open decisions.
- `content/`, `templates/`, `static/`: Markdown, Tera templates, and public assets.
- `scripts/`, `tests/`: Python migration tools and synthetic regression tests.
- `migration/`: configuration example and private working-directory conventions.
- `public/`: generated site output, ignored by Git.

Before publication, set the real title, domain, language, and agreed URL mappings.
Only deploy `public/`; never deploy this repository root or migration backups.

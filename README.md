# Technical blog

Zola site with Markdown articles and Python migration tooling for the
existing WordPress content. The templates are a minimal starting point, not the
final visual design. All 175 published WordPress posts/pages are staged under
`migration/work/full-site/`; curated content has not been promoted. See the
[full staging report](docs/full-staging-status.md).

## Local workflow

Use **Zola 0.23.6**, pinned in `.zola-version`, from the
[official release](https://github.com/getzola/zola/releases/tag/v0.23.6).
It is installed at `~/.local/bin/zola` in this environment. The scaffold and
full staging site both pass `zola build` and `zola check --skip-external-links`.

```sh
zola serve --drafts
zola check
zola build
```

Edit Markdown in `content/posts/` using VS Code. The example article is a draft
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
zola --root migration/work/full-site serve
```

## Planned search

Browser-side full-text search will use a build-time index. The migration plan
recommends Pagefind after `zola build`, with no search server or Node requirement.
Search integration and its post-build command are not implemented yet; see the
[search plan](docs/migration-plan.md#static-full-text-search).

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

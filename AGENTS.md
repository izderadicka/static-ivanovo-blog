# Repository Guidelines

## Project Structure & Module Organization

This repository contains a Zola blog scaffold and plans for migrating WordPress.
Articles live in `content/posts/`, Tera templates in `templates/`, and public assets
in `static/`. Use `content/posts/article-slug/index.md` for new articles with
adjacent media. Python migration tools belong in `scripts/`; sanitized fixtures
belong in `tests/fixtures/`. Generated site output is `public/`.

Before changing conversion, URLs, media handling, search, or deployment, read
`docs/migration-plan.md`. Read `scripts/README.md` before implementing migration
commands; those interfaces are currently planned, not runnable.

## Build, Test, and Development Commands

- `zola serve --drafts`: preview locally, including draft articles.
- `zola check`: check the site's content and links.
- `zola build`: generate production files in `public/`.
- `python3 -m venv .venv`: create the Python development environment.
- `. .venv/bin/activate`: activate it in a POSIX shell.
- `git diff --check`: check tracked changes for whitespace errors.

Install and pin a tested Zola release before migration. Python requires 3.11+.
Pagefind search is planned as a post-build step; integration is not implemented.

## Coding Style & Naming Conventions

Use four-space indentation and snake_case names for Python; use two-space
indentation in HTML/Tera. Match surrounding CSS and TOML formatting. No formatter
or linter is configured yet. Use descriptive, hyphenated article directory names
and language-labelled fenced code blocks. Preserve migrated public URLs explicitly.

Keep conversion deterministic and write generated results to staging. Preserve
code whitespace and original media. Maintain visual similarity to the existing
WordPress site; the current templates are placeholders.

## Testing Guidelines

No test framework, test suite, or coverage threshold exists yet. Add migration
tests as conversion logic is implemented; name Python test files `test_*.py` and
document the selected runner command. Cover entity decoding, code fences, media
references, route collisions, and private-content exclusion with sanitized fixtures.
For site changes, run Zola checks/builds and review representative desktop/mobile
pages. Report unavailable tools and unverified checks explicitly.

## Commit & Pull Request Guidelines

There are no commits yet, so no established message convention exists. Use concise,
imperative subjects such as `Add WordPress media inventory`. Keep changes focused.
PR descriptions should explain the result, validation, and remaining limitations;
link relevant issues and include screenshots for visual changes.

## Security & Configuration

Keep backups in ignored `migration/source/` and generated migration data in
`migration/work/` or `migration/reports/`. Commit only sanitized fixtures. Publish
only `public/`, and replace the placeholder domain before deployment.

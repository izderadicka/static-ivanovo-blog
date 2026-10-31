# Repository guidelines

This is a simple Zola blog preserving the accepted WordPress articles and media.
Editable Markdown is authoritative. Read README.md for authoring/build behavior
and docs/deployment.md before changing hosting or publishing.

## Structure and conventions

- Posts: content/posts/<slug>/index.md; standalone pages: content/pages/<slug>/index.md.
  Keep adjacent media with its page and preserve explicit public paths.
- Zola templates own pagination, the year-grouped archive, navigation, and feeds.
  Python supports authoring, preview, and validation; there is no generated page model.
- Templates: templates/; CSS, JavaScript, fonts, historical uploads: static/.
- Generated, ignored output: public/ and .build/.

Use four spaces in Python, two in HTML/Tera, and match surrounding CSS/TOML style.
Write UTF-8 prose and language-labelled code fences. Preserve migrated code
whitespace, original media, WordPress IDs/GUIDs, and source dates. WordPress
comments are omitted. Keep gists as remote embeds without downloading their code.
Standalone pages need include_in_feeds = false and extra.kind = "page".

## Verification

Run python3 scripts/build_site.py for production rendering, search, and offline
link/feed validation. Use python3 scripts/preview.py --drafts for complete local
review; restart after edits. Plain Zola rendering works but omits Pagefind and the
Python validation checks.

After tooling changes, run python3 -m unittest discover -s tests -v. Cover
publication behavior, privacy, routing, and content integrity rather than mirroring
implementation. Run git diff --check while preserving intentional migrated code
whitespace. For visual changes, review desktop/mobile output and report unavailable
checks. Docker integration tests are opt-in with RUN_DOCKER_TESTS=1.

## Publishing and commits

Publish only a fresh production public/ directory. Keep credentials and private
material outside the site tree. Hosting is a static published directory; see
docs/deployment.md for copying files and the optional Docker server. Local draft
previews must never be copied to the published directory.

Use concise imperative commit subjects. Commit completed changes when requested.
Explain resulting behavior, validation, and material limitations.

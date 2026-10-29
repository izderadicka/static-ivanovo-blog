# Repository guidelines

This is the migrated Ivanovo Zola site. The accepted WordPress snapshot is final;
editable Markdown is authoritative. Read README.md for authoring and build behavior.
Read docs/deployment.md before changing hosting or publishing.

## Structure and conventions

- Articles and standalone pages: content/posts/<descriptive-slug>/index.md, with
  new media adjacent to the article. Preserve existing explicit public paths.
- Templates: templates/; shared CSS, JavaScript, fonts, and historical uploads: static/.
- Authoring/build/preview/validation tools: scripts/; synthetic regression tests: tests/.
- Taxonomy URL overrides: data/taxonomy-slugs.json.
- Generated, ignored output: public/, .build/, content/_generated/, data/site.json.

Use four spaces in Python, two in HTML/Tera, and match surrounding CSS/TOML style.
Write prose in UTF-8 and use language-labelled code fences. Preserve migrated code
whitespace, original media, WordPress IDs/GUIDs, and source dates when editing posts.
Comments are omitted. Keep gists as remote GitHub embeds without downloading code.

## Verification

Use python3 scripts/build_site.py for complete production builds and offline local
link/feed validation. Use python3 scripts/preview.py --drafts for local draft review;
restart after edits. Plain Zola commands omit archive preparation and search indexing.

Run python3 -m unittest discover -s tests -v after tooling changes. Add tests for
publication behavior, privacy, routing, or content integrity risks rather than
mirroring implementation. Run git diff --check; preserve intentional source code
whitespace in migrated articles. For visual changes, review desktop/mobile output
and report checks that could not be performed.

## Publishing and commits

Publish only public/. Keep credentials and private material outside the site tree.
Production build commands exclude drafts; avoid publishing a local draft preview.
Hosting and automated publishing remain unconfigured until the deployment stage.

Use concise imperative commit subjects. Commit completed changes as requested by
the owner. Explain the resulting behavior, validation, and material limitations.

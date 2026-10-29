# Completed WordPress migration

The owner accepted the migrated appearance and confirmed on 2026-10-29 that the
current source snapshot is final. No final re-export or media delta is required.
The accepted articles/media have been promoted into the main Git-managed site.

- 154 published posts and 21 standalone pages retain their public paths and dates.
- Three drafts and all comments were excluded from the import.
- 434 block-code and 830 inline-code payloads were validated against the source.
- 254 original/referenced media files retain their checksums, including responsive
  variants. Historical attachment redirect pages remain in static/.
- Eight gists remain remote GitHub script embeds. No gist source was downloaded.
- All seven live-site audit findings were addressed: highlighting, automatic video
  embeds, navigation/archives/search/feeds, tables, typography, tabs/galleries, and
  responsive/lazy images. The accepted build indexed exactly 175 source pages.
- On promotion, all 175 rendered article bodies matched the accepted staging
  bodies exactly. Regular authoring now derives archives and summaries from Markdown.

Final WXR SHA-256: `1455c1f40866d4fb8044a306fd4bd5ad39af903135b6cde376910972a4667e39`.

The importer, synthetic migration fixtures, plans, audit reports, snapshots, and
intermediate builds were removed from the active project. A local migration archive
is retained alongside the checkout at
`/home/ivan/workspace/new-blog-migration-archive-20261029/`. Earlier commits retain
tracked migration tooling and documentation; source backups were never committed.
The owner also retains a separate backup.

Regular builds need only this checkout, pinned Zola/Pagefind binaries, and the
Python dependencies in requirements.txt. Generated archives, models, validation
reports, and the public artifact are ignored. The example scaffold post is removed.
Original public media is intentionally versioned with the site.

Promotion verification passed from a clean export of the staged Git files:
production build, 175 indexed pages, 406 valid RSS feeds, 87,791 local references,
and five authoring/publication regression tests. Twenty-six browser/HTTP checks
passed, with eight desktop/mobile captures showing no page-wide overflow.

Hosting has not changed. Remaining work is Docker/reverse-proxy/TLS integration,
production redirect and media response checks, release/rollback setup, and cutover.
Nginx adapters are examples and have not been tested on the destination server.
The retained PayPal form and third-party video/gist availability still depend on
their providers. See deployment.md for the hosting plan.

# WordPress to Zola migration plan

## Objective and current state

Move the locally hosted WordPress blog to a static Zola site. Author future
articles in Markdown in VS Code. Use Python for migration automation. Preserve
article content, code, images, videos, publication metadata, and public links.
Remove the production dependency on WordPress, PHP, and a database.

The owner has access to WordPress administration, files, and database. The initial
export, backup, and mirror inspection is recorded in [source-inventory.md](source-inventory.md):
154 published posts, 21 published pages, 3 drafts, and 128 attachments. Existing
comments will be omitted; Docker host configuration remains unresolved. The new
site will retain a similar visual appearance and run in Docker with mounted build
output. Inventory, normalization, and full staged content conversion
are implemented; see [full-staging-status.md](full-staging-status.md). The [audit fixes](parity-fixes.md) implement visual design, search, and archive/feed
routes; final hosting integration and acceptance remain outstanding. The Tera templates now reproduce the original layout with accessible enhancements. No deployment or change to the old site is part of
this step.

## Decisions and principles

- Use Zola with Tera templates; no Go templates or frontend framework required.
- Use ordinary Markdown and fenced code where possible; reserve HTML or small
  shortcodes for features Markdown cannot express faithfully.
- Prefer preserving public URLs over reorganizing them for appearance.
- Separate immutable inputs, generated staging output, and curated final content.
- Make conversion repeatable and auditable, with every source item accounted for.
- Preserve originals before optimizing media. Never silently drop content.
- Keep private backups outside the published site and version control.
- Pin a tested Zola release and Python dependency versions before full migration.

## 1. Inventory and backup

Collect a WordPress Tools → Export → All content WXR file, a consistent database
backup, and a full copy of WordPress files, especially `wp-content/uploads`.
Record WordPress/PHP versions, active plugins and theme, permalink configuration,
site/home URLs, timezone, language, and any web-server redirects. Note custom
post types, custom fields, code-highlighting plugins, galleries, and video players.
Export does not contain media binaries; verify the separate media copy.

Store originals under ignored `migration/source/`, with a separate backup outside
this checkout. Produce a manifest of relative paths, sizes, and SHA-256 hashes.
Verify the backup can be read and document how WordPress could be restored.
Do not modify the only source copy to repair parsing problems.

Inventory:

- Posts/pages by status: published, draft, private, scheduled, and trashed.
- Titles, IDs, slugs, dates, authors, tags, categories, comments, attachments.
- Actual public permalinks, archive/feed routes, pagination, attachment pages,
  query-string routes such as `?p=123`, and inbound fragment targets.
- Code markup, shortcode names, Gutenberg blocks, tables, footnotes, raw HTML,
  downloadable files, image variants, external assets, and video providers.
- Media counts, total bytes, missing references, and filename case/Unicode issues.

Capture rendered HTML from the working old site for representative articles and,
where feasible, all published URLs. WXR source alone may contain plugin shortcodes
rather than the text or markup readers actually saw. If public and local hostnames
differ, record both; do not infer public routes from localhost links.

**Exit gate:** readable backups, source manifest, content/media inventory, baseline
URL list, and a list of unsupported or ambiguous constructs.

## 2. Resolve migration policy

Confirm before implementing dependent conversions:

- Real domain and whether it remains the same; Docker host, volume type, reverse
  proxy/HTTPS setup, and publishing trigger (see `deployment.md`).
- Whether existing comments should become a static archive, be omitted with an
  explicit decision, or move to a service. New commenting is a separate choice.
- Treatment of drafts/private/scheduled posts. Default public output is published
  posts/pages only; private content must never be exposed as an ordinary draft.
- Required author attribution, categories/tags, archives, feed routes, and languages.
- Video hosting: copy existing uploaded files or use agreed external storage.
- Media volume and whether large binaries belong in Git or separate backed-up storage.
- Visual design and search interface details; browser-side full-text search is required.

Record decisions in this document or a companion migration decisions document.
Hosting and comment choices do not block initial read-only inventory work.

### Decisions recorded 2026-10-28

- Omit all existing comments; normalized records retain counts only. Do not add a
  commenting service during migration.
- Preserve GitHub gist script embeds as remote embeds, as requested by the owner.
  Do not download or inline gist source. Gist availability depends on GitHub and
  JavaScript; its code is absent from the static search index.
- The owner confirms a separate backup exists outside this checkout. An isolated
  restore test has not been performed; backup restoration is not a pilot prerequisite.
- Continue published-only output and preservation of existing public URL paths.

## 3. Build a representative pilot

Select roughly 5–10 articles, or fewer if the blog is small, covering the oldest
and newest formats plus the most difficult examples: nested lists, tables,
non-ASCII text, multiple code languages, captions, galleries, and videos.

Build Python conversion against these fixtures and review rendered output next
to the old site. Do not commit private source data as test fixtures; use synthetic
or sanitized equivalents. Demonstrate that the same input and configuration
produce identical content and mapping files on repeated runs.

**Exit gate:** owner-reviewed pilot with intact code and working media, no
unexplained content loss, and a documented strategy for every discovered construct.

## 4. Python pipeline design

Planned entry point: `python scripts/migrate.py --config PATH COMMAND`.
Use `migration/config.example.toml` as the starting configuration. Commands should
resolve paths consistently from the repository root and validate configuration
before writing. Refuse overlapping source/output trees, traversal paths, and
unexpected overwrite of existing curated files. Restrict asset access to approved
local roots; external downloads, if needed, use an explicit host allowlist.

| Command | Input | Output |
| --- | --- | --- |
| `inventory` | WXR, uploads, optional baseline HTML | Counts, shortcode/markup inventory, asset checksums, source URLs |
| `normalize` | WXR and inspected source metadata | Stable records keyed by WordPress ID; original HTML retained |
| `convert` | Records, URL/media maps, reviewed overrides | Staging Zola content/assets and a conversion report |
| `validate` | Source records, staging build, manifests | Content, code, media, route, and privacy checks |

Normalize before rendering Markdown. Each record should retain source ID/type,
status, public URL, title, slug, original and modified timestamps, timezone evidence,
author, taxonomies, original HTML, and attachment relationships. WordPress GUIDs
are identifiers, not authoritative current permalinks. Identify items by stable
IDs rather than title or slug. Preserve source timezone semantics; flag ambiguous
dates rather than guessing and potentially moving an article to a different day.

Reports should contain the source ID/URL, severity, location, explanation, and
suggested repair. Emit nonzero exit codes for blocking failures. Record skipped
items with reasons. Keep deterministic maps and reports separate from run timestamps.
Store reviewed exceptions in an explicit overrides file rather than ad hoc edits
to generated Markdown. Choose and lock XML/HTML/Markdown libraries after the pilot.
XML parsing must not resolve external entities or fetch network resources.

### Code conversion

Extract code before generic HTML-to-Markdown conversion. Handle `pre/code`, plugin
shortcodes, and block-editor code separately. Preserve tabs, indentation, blank
lines, punctuation, and Unicode. Decode HTML entities exactly at the correct layer;
never normalize code whitespace or apply typographic substitutions to code.
Choose a fence longer than any run of backticks inside its payload. Map known
language names; keep unknown languages as plain code and report them. Compare
extracted source and destination code text, and check rendered code for Zola
shortcode/template delimiter interactions. Include examples containing `{{`,
`{%`, HTML tags, ampersands, and nested fences in regression fixtures.

### Media conversion

Initially preserve uploaded public paths using `static/wp-content/uploads/...`;
this reduces broken external links and avoids duplicating assets shared by posts.
New articles can colocate assets beside `index.md`. Inventory originals and all
referenced resized images, `srcset` candidates, posters, captions, alt text, linked
full-size images, subtitles, PDFs, and other downloads. Never replace a full-size
original with a thumbnail. Check collisions and missing files before copying.

Copy self-hosted videos and use browser-compatible HTML video markup with controls
and posters where available. Preserve source files even if a separate transcoded
web version becomes necessary. Convert provider embeds deliberately; do not treat
an iframe URL as a downloadable video. Verify playback and content types on the
actual host. Report unavailable third-party media separately from migration errors.

### Links and routes

Create a mapping for every old published URL to its final route or explicit
retirement decision. Use Zola page `path` where appropriate; directory layout need
not dictate the public URL. Detect collisions across articles, pages, assets,
taxonomies, aliases, sitemap, and feeds before writing output.

Rewrite internal links using the map, retaining fragments and meaningful query
parameters. Check percent encoding, case, Unicode, trailing slashes, historical
HTTP URLs, and changed heading IDs. Preserve fragment anchors where feasible.
Use host-level permanent redirects for changed routes. Zola aliases produce HTML
redirect pages, not HTTP 301/308 responses, and cannot alone handle query-string
routing. Generate server-specific redirect rules only after hosting is selected.
Preserve `/feed/` or redirect it intentionally; verify subscriber-facing feed URLs.

### Other content

Preserve tables, lists, inline code, blockquotes, captions, and useful anchors.
Use limited reviewed HTML when Markdown loses meaning. Do not blanket-delete HTML
or shortcodes. Unknown constructs must be flagged for review. Remove WordPress
runtime references only after their content or behavior has been replaced.
Audit retained scripts and forms: a static site cannot execute PHP endpoints.

## 5. Complete the Zola site

The current templates are deliberately minimal. After the pilot:

- Pin and test Zola, then reproduce the current site’s typography, navigation,
  colors, code styling, and layout using its theme and desktop/mobile references.
- Add agreed taxonomies, archive pages, pagination, RSS/Atom, sitemap and canonical
  metadata, a 404 page, and browser-side full-text search (see below).
- Set the actual title, base URL, language, author information, and descriptions.
- Check code scrolling, long lines, mobile layout, contrast, keyboard access,
  image alt text, and video controls.
- Document Markdown authoring, preview, adding images, and publishing in README.

Promote reviewed staging content into the main content tree only after validation.
Once editorial changes start, never rerun conversion over them blindly: regenerate
in staging and review a diff, or apply reviewed overrides before regeneration.

### Static full-text search

Requirement: build the full-text index with the site and query it in the browser,
without a backend service. Recommended implementation: **Pagefind**, subject to
pilot validation on real articles. Search is implemented with pinned Pagefind 1.5.2; `scripts/build_site.py` runs the
post-build step and `scripts/preview.py` serves the indexed result.

Zola can generate indexes for Elasticlunr or Fuse, but the search interface still
needs integration. Pagefind indexes the final HTML, provides a search UI, and loads
index chunks on demand. Its extra post-build step is an acceptable tradeoff for a
ready-made interface and bounded initial downloads. Keep Zola's
`build_search_index = false` when using Pagefind to avoid duplicate indexes.

Implementation sequence:

1. Pin a tested Pagefind release. Use its standalone binary or Python wrapper;
   no Node toolchain is required. Keep migration scripts in Python.
2. Mark article content for indexing using Pagefind's content-selection attributes.
   Include titles, headings, prose, and code text. Exclude navigation, footers,
   archive duplicates, redirect pages, the search page, and nonpublic content.
3. Add an accessible search page or dialog reachable from site navigation. Use
   the prebuilt UI initially, with local assets and styling matching the blog.
   Show result titles, excerpts, and links; handle empty queries and no results.
4. Build in order: `zola build`, then `pagefind --site public`. Publish the entire
   output including `public/pagefind/` atomically. Every rebuild must regenerate
   the index; otherwise results may point at deleted or changed articles.
5. Preview the indexed production output using a static HTTP server. Do not rely
   on `zola serve` alone to exercise the post-build search step.
6. Keep queries in the browser, without analytics or external search services.
   Article navigation must remain usable when JavaScript is disabled.

Acceptance checks: known titles and body phrases find the expected articles;
code identifiers and technical terms such as `C++`, `C#`, `std::vector`, paths,
and error messages are evaluated explicitly. Tokenization may not preserve
punctuation as exact substring search would; document the observed behavior and
adjust configuration or reconsider the engine if it fails real use cases. Check
Unicode and actual article languages, keyboard operation, mobile layout, result
anchors, and no-results behavior. Confirm private/draft content is absent from
both results and generated index files. Measure downloaded bytes and perceived
latency against the full corpus, with the index fetched only when needed.

The index covers rendered text, including captions; it does not automatically
search text inside images, video speech, or linked PDFs. Transcripts or additional
indexing would be separate enhancements.

References: [Zola search](https://www.getzola.org/documentation/content/search/),
[Pagefind overview](https://pagefind.app/), and
[Pagefind installation and workflow](https://pagefind.app/docs/).

## 6. Full migration and acceptance

Run the complete pipeline into a staging copy of the site. Build with the pinned
Zola version and run `zola check`, then inspect generated HTML with Python checks.
Use offline internal checks as the reliable gate; report external link failures
separately because rate limiting and temporary outages are not proof of bad content.

Required acceptance criteria:

- Every eligible source post/page maps to exactly one intended destination.
- Exclusions and unsupported features are explicit and reviewed.
- No drafts/private content, backup files, or credentials appear in public output.
- Code payload comparisons pass with no unexplained differences.
- Every referenced local asset exists; copied originals match source checksums.
- Internal links, fragments, and redirect targets resolve; no route collisions.
- No unconverted shortcodes or dependencies on old WordPress runtime endpoints.
- Dates, authors, titles, and required taxonomies are preserved.
- Images and both embedded/uploaded videos work in browser review.
- Production builds exclude the scaffold draft and use the real domain.
- Feeds, canonical URLs, sitemap, mobile rendering, and representative long articles
  are reviewed. Redirect responses are checked on the destination server.

Use Python tests for actual migration risks: entity decoding, whitespace, code
fences, malformed records, duplicate routes, path traversal, private status,
missing assets, and deterministic regeneration. Add tests alongside implemented
conversion logic, not placeholder tests for the directory scaffold.

**Exit gate:** zero unexplained blocking failures and a review report that records
any accepted exceptions with their source IDs and rationale.

## 7. Publish and retain rollback

Serve the generated site in Docker with mounted build output. Follow
[the deployment and publishing plan](deployment.md) for release directories,
atomic activation, Python publishing automation, search integration, and rollback.
The steps below describe the initial WordPress cutover; routine article publishing
uses that separate workflow and does not repeat the migration.

1. Preview the complete build on staging; prevent indexing during review and
   restrict access if the preview contains material that is not public yet.
2. Freeze WordPress editing briefly, or capture a final consistent export and
   media delta. Re-run conversion and acceptance against that final snapshot.
3. Archive the accepted static artifact, tool versions, source checksums, route
   map, and reports. Retain a restorable WordPress backup outside the web root.
4. Deploy only `public/`, configure HTTPS, redirects, MIME types, and agreed cache
   settings. Remove staging indexing restrictions for production.
5. Switch the web-server root or DNS as appropriate. Keep rollback instructions
   specific to that hosting setup and include cache/DNS considerations.
6. Verify real URLs, redirects, feeds, images, downloads, video playback, and 404
   behavior immediately after the switch. Monitor missing routes afterwards.

Rollback if articles or media are widely missing, routes fail, or private content
is exposed. Restore the prior server configuration/artifact, verify service, and
repair in staging before retrying. Agree an observation period before retiring
WordPress. Retained WordPress backups need not remain publicly accessible.

## Suggested implementation milestones

1. **Inventory:** backups and source/feature reports; resolve policy questions.
2. **Pilot:** tested Python parser/converter and reviewed difficult articles.
3. **Complete staging:** full conversion, chosen design, media and route maps.
4. **Acceptance:** automated checks, browser review, host-specific redirect tests.
5. **Cutover:** final snapshot, deploy, verify, observe, then retire old runtime.

Estimate effort after inventory; plugin-specific formatting and missing media are
likely to dominate more than the number of articles alone.

## References

Consulted 2026-10-28. Pin the actual tested release rather than assuming these
living documentation pages match an older locally installed binary.

- [Zola directory structure](https://www.getzola.org/documentation/getting-started/directory-structure/)
- [Zola configuration](https://www.getzola.org/documentation/getting-started/configuration/)
- [Zola page metadata and paths](https://www.getzola.org/documentation/content/page/)
- [Zola syntax highlighting](https://www.getzola.org/documentation/content/syntax-highlighting/)
- [WordPress export workflow](https://learn.wordpress.org/lesson/tools-export-and-import/)

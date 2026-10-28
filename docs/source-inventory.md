# Initial WordPress source inspection

Inspected locally on 2026-10-28. Originals were read without modification. No
conversion, WordPress execution, database import, or network requests were made.

## Inputs and verification

| Input | Findings |
| --- | --- |
| `migration/source/ivanovo.WordPress.2026-10-28.xml` | Readable WXR 1.2; parsed successfully; no DTD/entity declarations |
| `migration/source/backup/` | WordPress files, configuration, uploads, themes/plugins, BackWPup manifest, and SQL gzip |
| `migration/source/backup/d51399_wp.sql.gz` | Entire gzip stream read successfully, including CRC validation; 175,203,059 uncompressed bytes; 26 table definitions including posts, metadata, users, comments, options, and taxonomies |
| `migration/source/snapshot/zderadicka.eu/` | 1,121 HTML files; an HTML file exists at every exported published post/page path |

The source manifest covers 10,099 files and 367,675,683 bytes, with relative paths,
sizes, and SHA-256 hashes. Detailed data remains in ignored `migration/reports/`:
`source-manifest.json`, `inventory-summary.json`, `content-inventory.json`,
`published-urls.json`, `missing-upload-references.json`, `backup-metadata.json`,
and `supplemental-checks.json`. The initial inspection script is retained locally
as `migration/work/inspect_sources.py`; this is not the planned migration CLI.

## Content and configuration

- 154 published posts, 21 published pages, and 3 draft posts.
- 128 attachments, 5 navigation items, and 5 `ml-slider` records.
- 184 exported comments, all approved. Owner decision: omit all comments.
- Published local dates range from 2012-09-21 through 2026-07-18.
- Site title: Ivanovo; language: en-US; domain: `zderadicka.eu`.
- WordPress version: 5.2.29, confirmed in core and backup metadata.
- Theme: Twenty Fourteen Child, parent `twentyfourteen`; child theme files exist.
- All 15 active plugin entrypoint files listed by the backup manifest exist.
- SQL permalink setting: `/%postname%/`. WXR and SQL URLs use HTTP; backup
  metadata uses HTTPS. Preserve paths and establish the production scheme explicitly.
- SQL timezone is an empty named zone with fixed `gmt_offset = 1`. Do not infer
  Europe/Prague or historical daylight-saving rules from the current environment.

The mirror rewrites canonical links into relative local filenames such as
`../index.html%3Fp=43.html`; it is a rendering baseline, not an authoritative
source of production canonical URLs. Query-style mirror files also exist. The
published URL report uses WXR links, supported by the SQL permalink setting;
archive/feed routes, historical redirects, fragments, and query routing still
need a complete inventory.

## Media

The backup uploads tree contains 485 files totaling 84,114,233 bytes, including
images, ZIP downloads, 5 MP4s, 3 WebMs, 3 WAVs, and SVGs. All 128 attachment URLs
resolve to files in that tree. No missing upload files were found in the initial
HTML attribute scan or the supplemental scan of upload URLs in source bodies
(including shortcode text). These are initial checks, not full media acceptance:
CSS references, rendered plugin assets, relative URLs, playback, and external
availability still need validation.

Two filename pairs differ only by case: `MBS2.png` / `mbs2.png` and
`MBS2-150x150.png` / `mbs2-150x150.png`. Preserve case and use case-sensitive
staging/storage, or resolve these through reviewed mappings.

Do not publish the uploads tree wholesale. It includes statistics logs, a GeoIP
database, BackWPup temporary PHP files, and access-control files. Inventory and
copy public media deliberately, preserving original paths and hashes.

## Conversion risks and pilot candidates

The source contains 439 `pre` elements, 842 `code` elements, legacy Crayon markup,
27 `EnlighterJSRAW` elements, and 23 Gutenberg `enlighter/codeblock` blocks.
Code must be extracted before generic Markdown conversion. The shortcode report
is deliberately a list of candidates: array indexing and code produce false
positives and must not be treated as WordPress shortcodes automatically.

Confirmed constructs needing strategies include tabs, MetaSlider, video/audio
shortcodes, embeds, tables, scripts, and a contribution form. Suggested pilot:

| Source ID | Reason |
| --- | --- |
| 94 | Downloader Python3: early format and tabs |
| 209 | MyBookshelf: tabs and slider |
| 139 | Visual Python: uploaded video |
| 834 | Audio captchas: audio examples |
| 1096 | Contribute: form behavior |
| 1137 | imap_detach: multiple tables |
| 1466 | MyBookshelf2: provider embeds |
| 2112 | Higher Rank Trait Bounds: technical code and scripts |
| 2336 | Rust generics: recent technical article and script |

Confirm the pilot includes both legacy and block-editor highlighting by examining
the actual code payloads. Preserve rendered plugin output as evidence. Scripts
and forms need individual review; a static site cannot inherit PHP behavior.

## Remaining inventory exit gate

Inputs are sufficient to begin pilot analysis, but the inventory gate is not yet
complete. Gzip integrity and file presence do not prove a restorable WordPress
instance or a transactionally consistent snapshot. Restore into an isolated,
nonpublic environment: recreate the original WordPress directory layout from the
backup manifest, import SQL into a compatible database, configure local database
access, and verify posts, themes, plugins, and media with outbound mail/jobs
disabled. Do not execute the backup in the published site directory.

The owner confirmed a separate backup outside this checkout on 2026-10-28.

Still needed: isolated restore test, original PHP/database versions, snapshot
consistency evidence, complete routes and asset inventories, rendered baseline quality review, and
policies for custom content, scripts/forms, and canonical scheme.
Server redirects beyond the supplied standard WordPress `.htaccess` are unknown.
No browser rendering, video playback, or external link checks were performed.

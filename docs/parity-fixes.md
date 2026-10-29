# Live-site audit fixes

Implemented 2026-10-29, following [the live-site audit](live-site-audit.md).
All seven findings have corresponding implementation and verification.

## Changes

1. **Code:** ordinary examples retain readable Markdown fences. HTML fallbacks
   (including nested lists and Django template text) now use Pygments 2.17.2 with
   their mapped language, preserving whitespace and literal delimiters. Rendered
   validation checks language-aware highlighting as well as exact payloads.
2. **Automatic embeds:** standalone YouTube URLs become responsive players with
   ordinary link fallbacks. URLs in prose, links, and code are not auto-embedded.
3. **Structure:** the homepage lists posts, with excerpts and ten posts per page
   (16 pages). Homepage summaries keep safe inline links/emphasis and full-size image links.
   Project pages retain their hierarchy and WordPress menu order.
   Category, tag, author, year/month/day archives and paginated archive routes
   are generated. Previous/next post links, visible taxonomy/author metadata,
   canonical URLs, a sitemap, search page, and a styled 404 page are provided.
4. **Tables:** reference tables have borders, padding, alignment, and keyboard
   accessible scroll containers, including without JavaScript.
5. **Visuals:** the original public logo and locally served Lato fonts restore
   the black header/sidebar, green links, 16px/24px body text, lighter uppercase
   headings, project menu, popular 45-tag cloud, categories, and month selector.
   Code has numbered striped rows and a green left rule. Project pages do not
   display post dates. Mobile navigation is keyboard accessible.
6. **Tabs/galleries:** four tab sets and five galleries are progressively enhanced
   with keyboard tabs, previous/next buttons, and live slide counters. All content
   remains present without JavaScript. WordPress tab and slider anchor IDs are
   retained. Galleries do not autoplay.
7. **Images:** responsive candidates/sizes/dimensions are recovered from the
   configured mirror, restricted to approved upload files, and checksummed when
   copied (254 original/referenced media files in this build). Lazy loading is preserved or added appropriately; originals and
   full-size links remain intact.

Comments remain omitted. All eight gist scripts remain remote; no gist source is
stored locally. No WordPress runtime endpoints are required by the new layout.

## Search and feeds

Pagefind 1.5.2 indexes exactly the 175 source posts/pages, including code and
captions. Archive duplicates, RSS, redirects, drafts/private records, navigation,
and search itself are excluded. Search assets/queries stay on the site and the
index is loaded on the search page. No analytics or external search API is used.
Gist code inserted at runtime remains outside the static index by owner policy.

Browser checks found the expected Tiny Etude title result, relevant `C++` and
`C#` results, and the exact `std::ops::Mul` article. Pagefind's normal prefix
matching can broaden `std::vector` to other `std::` identifiers, and can broaden
unmatched strings to short prefixes. Quoted queries provide exact matching;
quoted unmatched input returns no results. The search page explains this syntax.

RSS preserves original WordPress GUIDs to avoid presenting migrated entries as
new items. It includes the ten newest matching posts and their full rendered content;
project pages are excluded. Root `/feed/` and taxonomy/author/date feed routes
are generated in addition to `/rss.xml`. The preview server returns the correct
RSS MIME type and redirects legacy `?p=ID`, `?page_id=ID`, and `?s=` requests.

For production, generated `redirects/nginx-maps.conf` belongs at Nginx `http`
scope; `redirects/nginx-site.conf` is an adapter example for the selected root,
feed MIME types, query redirects, and 404 handling. It must be integrated with
actual hosting/TLS configuration. Nginx is not installed here, so that adapter
has not been tested by `nginx -t` or deployed. The equivalent local HTTP behaviors
were tested against the preview server. Only `public/` is a publishing artifact.

## Build and preview

```sh
python3 scripts/build_site.py
python3 scripts/preview.py
```

Stop an older preview process before reusing port 1111. The preview command
builds Zola and Pagefind together, then serves `http://127.0.0.1:1111`. For a
previously built preview, `--no-build` skips rebuilding. `zola serve` alone does
not execute Pagefind's post-build step; use the Python preview for search testing.

## Verification

- 32 synthetic regression tests pass, including real Zola builds, literal/nested
  code highlighting, responsive variants, automatic-embed boundaries, private
  exclusion, RSS XML escaping, metadata, and output integrity.
- All 175 source pages retain publication metadata, prose, 434 block-code payloads,
  and 830 inline-code payloads. Known-language samples all reach a highlighter.
- Zola build/check and migration validation pass. Validation checks 874 generated
  routes, 406 RSS feeds, archive pagination links, fragments, and media hashes.
- Pagefind indexes exactly 175 source pages and 11,340 distinct words.
- Twenty desktop/mobile captures cover the theme, code, projects, media, tables,
  gist, latest post, template-code examples, and search. Lato loads locally and
  no page-wide horizontal overflow was observed in those views.
- Browser interaction checks cover keyboard tabs, gallery counters, mobile menu,
  YouTube/fallback links, table borders/keyboard scrolling, search results,
  query redirects, unknown-ID 404s, and RSS response types.
- A corpus-wide comparison with cached live audit HTML finds no remaining
  missing responsive/lazy attributes and no known-language highlighting bypass.

Artifacts are ignored under `migration/reports/parity/`. The previous staging
site and reports are retained as the pre-fix reference. These checks are not a
claim of pixel-identical rendering or exhaustive third-party playback testing.

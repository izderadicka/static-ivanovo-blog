# Migration, build, and preview tools

Python 3.11+ is required. Install local migration dependencies in a virtual
environment with `python3 -m pip install -r requirements-migration.txt`.
XML parsing uses defusedxml with DTDs/entities/external access forbidden; HTML
uses Beautiful Soup. Pygments 2.17.2 highlights retained HTML code. Zola 0.23.6
and Pagefind 1.5.2 are pinned in `.zola-version` and `.pagefind-version`.

From the repository root:

```sh
python3 scripts/migrate.py --config migration/full.example.toml inventory
python3 scripts/migrate.py --config migration/full.example.toml normalize
python3 scripts/migrate.py --config migration/full.example.toml convert
python3 scripts/build_site.py
python3 -m unittest discover -s tests -v
python3 scripts/preview.py
```

`build_site.py` builds Zola, generates Pagefind, runs offline Zola checks, and
validates the migration. `preview.py` rebuilds with local URLs and serves the
complete indexed site at `http://127.0.0.1:1111`. Stop an older server first.
Use `--port`, `--bind`, `--config`, or `--no-build` as needed. Raw `zola serve`
does not run Pagefind and should not be used as the search acceptance check.

`migration/full.example.toml` selects all published posts/pages using
`[selection] scope = "all"`. The original `migration/config.example.toml` selects
nine pilot IDs. To regenerate an older output after converter changes, copy its
config into `migration/work/` and choose a fresh `output.site` directory.

## Data boundaries

Paths resolve from the repository root regardless of invocation directory.
Sources remain read-only. Site/record output must stay under `migration/work/`,
reports under `migration/reports/`. Source/output overlap, traversal, asset
symlink escapes, unsafe taxonomy slugs, and route collisions are refused.
Those directories are ignored; never publish their parent or normalized records.

`inventory` writes status counts, route lists, upload hashes, case collisions,
comment counts, and a WXR fingerprint. `normalize` retains stable IDs, original
HTML, local/GMT dates, authors, taxonomies, hierarchy/menu order, attachments,
and exclusion reasons. Nonpublic HTML stays only in ignored normalization data;
comment text, contact addresses, and IPs are not normalized.

`convert` writes selected eligible articles, explicit public paths, original and
responsive media, attachment redirects, navigation/archive models, RSS templates,
and generated archive/search pages. It also emits Nginx adapter examples outside
`public/`. Results, code/prose evidence, review items, and SHA-256 fingerprints are
in `conversion.json`. Blocking article errors return a nonzero status and withhold
that article. Curated root `content/` is never overwritten.

Identical reruns are allowed, including after building. Only `public/` and
`.zola-cache/` are excluded from the input comparison. Edited or changed staging
inputs are protected: regenerate into a fresh directory and review a diff.

## Content conversion

Directories use descriptive WordPress slugs or titles; repeated slugs use parent
paths and unresolved collisions fail. IDs stay in metadata/reports. Prose keeps
literal UTF-8 quotes and apostrophes, escaping only Markdown syntax when needed.

Ordinary code uses fenced Markdown. Nested HTML code and samples containing
literal template delimiters use Pygments with the mapped language. Newlines in
retained HTML blocks use character references so Markdown cannot terminate or
reinterpret those blocks. Giallo fences include the structural last line needed
to preserve exact code text, including the absence of a terminating newline.

Tabs and galleries preserve content/anchors server-side, with accessible keyboard
and previous/next enhancements from local JavaScript. Tables keep their structure
and receive scroll containers. WordPress read-more comments become `more-ID`
anchors without dropping surrounding list text. Standalone YouTube URLs and
explicit embed shortcodes get responsive players and normal fallback links;
URLs within code or ordinary prose are not replaced.

The configured mirror supplies responsive image attributes. Every local candidate
is checked inside approved uploads and copied with its source checksum. Originals,
filename case, alt text, captions, and full-size links are retained. Nonpublic
plugin data, logs, temporary PHP, and backups are not bulk-copied from uploads.
Unknown elements/languages or unresolved behavior are reported, with blocking
failures for unsafe URLs, missing assets, and unsupported scripts/forms.

Comments remain omitted. All GitHub gist scripts remain remote and therefore do
not contribute their dynamic code to the static search index. The original
PayPal contribution form is retained; automated checks never submit it.

## Navigation, feeds, and search

Selected public metadata drives the project hierarchy, 45 most-used sidebar tags,
category/author/date archives, post-only homepage with ten items per page, and
previous/next links. Project pages use a distinct presentation without post dates.
RSS includes full rendered post contents, excludes project pages, and is exposed
at `/rss.xml`, `/feed/`, and matching archive feed routes. The sitemap excludes
feed/search duplicates. `data/site.json` is generated input, not a public export.
These models describe migration staging; routine authoring/publishing after
promotion must update the corresponding models when new posts are added.

Pagefind indexes only `[data-pagefind-body]` article regions. Drafts/private data,
archives, navigation, feeds, redirects, and search itself are excluded. Queries
are local and index assets load on the search page. Prefix matching can broaden
technical queries; quotes enforce exact phrases/identifiers. The browser checks
cover title, `C++`, `C#`, `std::ops::Mul`, and unmatched exact queries.

The preview server gives extensionless feed files `application/rss+xml`, returns
308s for known `?p=`/`?page_id=` links while retaining other query parameters,
returns 404 for unknown IDs, and maps `?s=` to search. The generated Nginx maps
belong at `http` scope; adapt the example server root/TLS/proxy before deployment.
Nginx syntax/deployment has not been exercised here. HTML attachment redirects
remain distinct from HTTP permanent redirects.

## Validation

`validate` verifies source/staging hashes, public IDs and metadata, exact rendered
block/inline code, highlighting eligibility, prose retention, copied/built media,
links/fragments, generated archive routes, and RSS XML/feed membership. It requires
an existing full build. Detailed reports are `validation.json` and
`rendered-validation.json`. External URLs are listed without being requested.

See `docs/parity-fixes.md` for browser checks and the live-audit follow-up.
Publishing/cutover and final host integration remain separate from these tools.

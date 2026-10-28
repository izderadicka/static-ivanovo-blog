# Python migration tools

Python 3.11+ is required. Install the tested dependencies with
`python3 -m pip install -r requirements-migration.txt` in a virtual environment.
XML uses defusedxml with DTDs, entities, and external access forbidden; HTML uses
Beautiful Soup's built-in HTML parser. Zola is pinned to 0.23.6 in `.zola-version`.

Run the full workflow from the repository root:

```sh
python3 scripts/migrate.py --config migration/full.example.toml inventory
python3 scripts/migrate.py --config migration/full.example.toml normalize
python3 scripts/migrate.py --config migration/full.example.toml convert
zola --root migration/work/full-site build
zola --root migration/work/full-site check --skip-external-links
python3 scripts/migrate.py --config migration/full.example.toml validate
python3 -m unittest discover -s tests -v
zola --root migration/work/full-site serve
```

`migration/full.example.toml` selects all published posts/pages with
`[selection] scope = "all"`. The original `migration/config.example.toml` selects
nine pilot IDs. To regenerate that older pilot with the revised converter, copy
its config into `migration/work/` and choose a fresh `output.site` directory.

Configuration paths resolve from the repository root even when invoked elsewhere.
Sources are read-only; records and site output must be under `migration/work/`,
reports under `migration/reports/`. Source/output overlap, traversal, asset symlink
escapes, and public route collisions are refused. These directories are ignored.

- `inventory`: status counts, public routes, upload sizes/hashes, case collisions,
  omitted comment count, and WXR fingerprint.
- `normalize`: stable records sorted by WordPress ID, original HTML, local/GMT
  dates, authors, taxonomies, attachment relationships, routes, and exclusions.
  Comment text, emails, and IPs are omitted. Nonpublic original article HTML is
  retained only in ignored records; never publish that directory.
- `convert`: writes a separate Zola scaffold, selected eligible articles, public
  attachment originals and HTML redirects, and referenced resized media. Produces
  `conversion.json` with results, code/prose evidence, review items, and output
  SHA-256 fingerprints. Articles with errors are withheld; blocking errors return
  a nonzero exit status. No changes are made to curated `content/`.
- `validate`: checks source/staging fingerprints, metadata, public IDs, rendered
  block/inline code, prose retention, media checksums, internal URLs, and fragment
  targets. Full conversion requires an existing build. Detailed results are in
  `validation.json` and `rendered-validation.json`. External links are listed,
  without network requests. Browser review is still required.

Identical reruns are permitted, including after a build. Build output under
`public/` and `.zola-cache/` is excluded from the input comparison. Changed or
edited staging inputs are never overwritten: choose a fresh output directory.
Reports are regenerated; edited staging content is protected.

Article directories use descriptive WordPress slugs (falling back to the title).
Duplicate slugs are qualified by their public parent paths; unresolved collisions
are refused. Public URLs remain controlled by front matter `path`; IDs remain
in `extra.wordpress_id` and reports. Prose uses literal UTF-8 quotes and apostrophes.
Only syntax Markdown would interpret is escaped.

The converter handles code fences, legacy HTML, tabs as headings, sliders as
static galleries, uploaded audio/video, and YouTube embeds confirmed against the
mirror. Tables/lists/captions remain HTML for fidelity. Inline code uses Markdown
spans or escaped HTML. Nested code and samples with Django/Zola delimiters use
HTML where needed to preserve exact payloads. Newlines in code inside retained
HTML blocks use character references to avoid CommonMark block termination.
Highlighted fences include a structural empty last line because Giallo otherwise
removes the source's final newline. The rendered-code check verifies this behavior
against the pinned Zola release. Legacy `lang:` labels are mapped explicitly.
Samples without a final newline also use fences: Giallo removes the structural
newline, preserving the original payload while keeping syntax highlighting.

Read-more comments become `more-ID` anchors, preserving their surrounding text;
Zola's summary marker can discard text when it occurs inside a source list line.
Unknown elements, unsafe URLs, unsupported scripts/forms, and missing media block
conversion. Unknown code language labels are retained as plain code and reported.

Owner policy omits comments and retains remote GitHub gist script embeds. No gist
content is downloaded. Its code depends on GitHub/JavaScript and is absent from
static search. The encrypted PayPal contribution form is retained for review;
submissions are not tested automatically.

Full staging preserves attachment URLs with HTML redirect pages linking to their
original files. These are not HTTP 301/308 responses; host-specific rules remain
for deployment. The one historical attachment alias in `full.example.toml` was
verified against the mirror. Aliases may target only eligible attachment originals.
WordPress `?p=ID`/`?page_id=ID` links in article content are rewritten to known
published routes while retaining other parameters and fragments. Arbitrary inbound
query routing still needs host configuration.

Full staging uses the real site origin and title but retains placeholder styling.
Archives/feed routes, theme completion, Pagefind, browser review, and deployment
remain subsequent work. See `docs/full-staging-status.md` for current evidence.

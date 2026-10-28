# Python migration tools

Python 3.11+ is required. Install the tested dependencies with
`python3 -m pip install -r requirements-migration.txt` in a virtual environment.
XML uses defusedxml with DTDs, entities, and external access forbidden; HTML uses
Beautiful Soup's built-in HTML parser. Dependencies are pinned for this pilot.

Run from the repository root:

```sh
python3 scripts/migrate.py --config migration/config.example.toml inventory
python3 scripts/migrate.py --config migration/config.example.toml normalize
python3 scripts/migrate.py --config migration/config.example.toml convert
python3 scripts/migrate.py --config migration/config.example.toml validate
python3 -m unittest discover -s tests -v
```

Configuration paths resolve from the repository root even when invoked elsewhere.
Copy the example configuration to `migration/work/` for local changes. Sources
are read-only; records and site output must be under `migration/work/`, reports
under `migration/reports/`. Source/output overlap, traversal, asset symlink escapes,
and public route collisions are refused. These directories are ignored by Git.

- `inventory`: status counts, public routes, upload sizes/hashes, case collisions,
  omitted comment count, and WXR fingerprint.
- `normalize`: stable records sorted by WordPress ID, original HTML, local/GMT
  dates, authors, taxonomies, attachment relationships, routes, and exclusions.
  Comment text, emails, and IPs are omitted. Nonpublic original article HTML is
  retained only in ignored records; never publish that directory.
- `convert`: **pilot only**, selecting configured IDs. Writes a separate Zola
  scaffold with eligible articles and only referenced approved media. Produces
  `pilot.json` with per-article results, issues, and output SHA-256 fingerprints.
  Articles with errors are withheld; exit status is nonzero for blocking errors.
- `validate`: verifies source/output fingerprints and reports conversion errors;
  it does not replace Zola checks, rendered code comparison, or browser review.

Identical conversion reruns are permitted. A changed or edited staging tree is
never overwritten: select a fresh `output.site` directory for revised inputs or
converter behavior. Generated Zola files, reports, and normalized records are
separate from curated `content/`. Do not promote pilot output before review.

Article directories use descriptive WordPress slugs (falling back to the title),
not numeric IDs. Duplicate slugs are qualified by their public parent paths;
unresolved directory collisions are refused. Public URLs remain controlled by
front matter `path`, and WordPress IDs remain in `extra.wordpress_id` and reports.
Plain prose uses literal UTF-8 characters, quotes, and apostrophes. Only syntax
that Markdown would interpret is escaped; retained HTML still escapes attribute
values and literal code markup where required.

The converter handles fenced code, legacy HTML, tabs as headings, sliders as
static galleries from the local mirror, uploaded audio/video, and YouTube embeds
confirmed against that mirror. Tables/lists/captions remain HTML for fidelity;
code nested in HTML lists remains escaped `pre/code`. Unknown elements, unsafe
URLs, unsupported scripts/forms, unresolved media, and Zola shortcode delimiters
block the affected article. Unknown code language labels are reported.

Owner policy omits comments and preserves GitHub gist script embeds. No gist
content is downloaded. Gist code remains dependent on GitHub and JavaScript and
will not be included in static full-text search. The original encrypted PayPal
contribution form is retained for review; submissions are not tested automatically.

Zola 0.23.6 is installed and pinned in `.zola-version`. The scaffold and nine-page
pilot pass builds and checks with external links skipped. Build/check the pilot
with the configured site as its root, then compare desktop/mobile pages with the
mirror. The pilot retains the
scaffold's placeholder domain and styling deliberately; it is not deployable.
Full conversion, server redirects, complete link/fragment checks, Pagefind,
rendered-code validation, and publishing remain subsequent work.

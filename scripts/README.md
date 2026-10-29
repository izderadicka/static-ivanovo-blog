# Site tools

Run from the repository root with Python 3.11+ and the dependencies in
`requirements.txt`. Zola and Pagefind binaries must match their version pins.

- `python3 scripts/new_post.py SLUG --title "Title"`: create a draft and media directory.
- `python3 scripts/build_site.py`: generate archives/navigation, build production
  HTML and search, and validate local routes, fragments, feeds, and search assets.
- `python3 scripts/preview.py [--drafts] [--port 1111]`: rebuild with local URLs and
  serve the indexed site. Restart after edits; there is no file watcher.
- `python3 -m unittest discover -s tests -v`: run authoring/publication regression tests.

`build_site.py --drafts` is for local review. Its optional `--base-url` overrides
URLs for a review environment. A production release must use a fresh build with
neither option. `preview.py --no-build` refuses mismatched URL/draft settings.

`site_content.py` reads TOML front matter and Markdown summaries; `site_model.py`
prepares the public navigation/archive models. Zola renders complete article bodies.
`server_routes.py` prepares the historical query redirect adapter from retained
WordPress IDs. `validate_site.py` performs offline checks of the built artifact.
Generated reports and Nginx adapter examples are in ignored `.build/`.

These tools do not read WordPress exports or migration reports. Source Markdown is
authoritative. Edit only source files; generated archives/data are replaced on every
build. See the repository README for the complete authoring process.

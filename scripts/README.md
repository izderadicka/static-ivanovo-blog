# Site tools

- `python3 scripts/new_post.py SLUG --title "Title"`: create a Markdown draft.
- `python3 scripts/build_site.py`: run Zola, Pagefind, and offline validation.
- `python3 scripts/preview.py [--drafts] [--port 1111]`: build with local URLs and serve.
- `python3 -m unittest discover -s tests -v`: run regression checks.

Zola owns rendering, pagination, taxonomies, navigation, archives, and feed selection. There
is no preparation step or generated content model. Plain `zola build` and
`zola serve` work for rendering; the Python wrapper adds search and validation.
The preview rebuilds before serving and must be restarted after edits. A failed
build never starts a preview server.

`site_content.py` validates source metadata. `validate_site.py` checks the output.
These tools never rewrite article sources. Publishing is a production build and
copy of `public/`; see [deployment.md](../docs/deployment.md).

Production builds write `public/`; builds with `--drafts` or `--base-url` write
`.build/preview/`. This keeps local reviews separate from the Docker document root.

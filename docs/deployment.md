# Publish a static directory

The site needs only a static web server. Build production output, then copy
`public/` into the server's document root. No release IDs, manifests, activation
symlinks, or deployment service are needed.

```sh
python3 scripts/build_site.py
scripts/publish.sh user@host:/path/to/blog-document-root/
```

Use a directory dedicated to this blog: `--delete` removes files from the
destination that no longer exist in `public/`. Run these commands in sequence,
and copy only after the build succeeds. `scripts/publish.sh` syncs the existing
production build over SSH using rsync; it does not build the site. Pass the
remote document root as its argument. The repository does not contain the live
server's SSH host or document root, so configure SSH access in your normal SSH
configuration and supply the destination when publishing. The script refuses
to run if `public/index.html` is missing.

Keep the last successful copy if you want a rollback; restoring it is another
copy operation. Updates are not atomic, so visitors can briefly see mixed files
during a transfer. For an occasional personal-blog update, this is the deliberate
tradeoff for a much simpler publishing workflow.

## Optional Docker server

The supplied Nginx container serves one published directory over HTTP; your
existing reverse proxy owns HTTPS. The production base URL remains
`https://zderadicka.eu`.

For a local installation, from the repository root:

```sh
python3 scripts/build_site.py
docker compose -f deploy/compose.yaml up -d --force-recreate --wait
```

The backend listens at **http://127.0.0.1:8080/** and mounts `../public` directly
(relative to `deploy/`). Repeat those two commands for an update. Zola replaces
the output directory during a build, so recreating the container attaches its
bind mount to the newly built directory. A reload alone does not refresh that mount.

Python previews and review builds write `.build/preview/`, leaving `public/`
untouched. For raw Zola previews, use
`zola serve --drafts --output-dir .build/preview --force` as well. Run production builds
without `--drafts` or `--base-url` before starting the Docker server.

For a server directory such as `/srv/ivanovo`, set `BLOG_SITE_ROOT=/srv/ivanovo`
in `deploy/.env` (see `.env.example`) and copy there instead. Paths refer to the
Docker daemon's host. The container reads files as UID 101: directories must be
traversable and files readable by that UID, typically modes 755 and 644.

For an existing proxy on the same host, use upstream `http://127.0.0.1:8080`.
For a proxy on a shared Docker network:

```sh
BLOG_PROXY_NETWORK=your-proxy-network docker compose \
  -f deploy/compose.yaml -f deploy/compose.proxy.yaml up -d --wait
```

Use upstream `http://ivanovo-blog:8080` and the same Compose file arguments for
later management commands. Neither option changes DNS or a live proxy for you.

## Migrating from the previous release layout

In an existing checkout, remove the old disposable generated sources once:

```sh
rm -rf content/_generated
rm -f data/site.json
```

Then build production output. Remove an existing `BLOG_SITE_ROOT` override to use
`../public`, or point it at a separately maintained document root. This also applies
to an override of `../.build/published` from the earlier simplified configuration.
Recreate the container:

```sh
docker compose -f deploy/compose.yaml up -d --force-recreate --wait
```

The old `current -> releases/...` layout is no longer used. Keep it until you
have verified the new server; its files are not removed automatically.

## Compatibility and verification

Nginx serves the styled 404 with HTTP status 404, RSS with its MIME type, compressed
text, and byte ranges for media. All redirect locations are relative so they work
behind an HTTPS proxy. The container and site mounts are read-only.

`deploy/legacy-redirects.conf` is the fixed map of accepted WordPress IDs to article
URLs. New posts need no entry. If you deliberately change an old URL, update that
map and reload Nginx after checking the configuration. `/feed/rss2/` redirects to
`/feed/`; retired calendar archives redirect to the corresponding year anchor on
`/archives/`, and author archives redirect to `/archives/`. Tags and categories are served as
native Zola topic pages. Four legacy taxonomy spellings redirect to their native
Zola URLs. These
HTTP redirects are optional compatibility provided by this server, not additional
rendered archive pages. Other static hosts need equivalent redirect configuration
if you want those old archive and query URLs supported.

```sh
docker compose -f deploy/compose.yaml exec -T blog nginx -t
docker compose -f deploy/compose.yaml exec -T blog nginx -s reload
RUN_DOCKER_TESTS=1 python3 -m unittest discover -s tests -p test_hosting.py -v
```

The opt-in tests use an isolated temporary server. Normal tests need no Docker.
Always review a fresh production build before copying it; a local draft preview
is not a publishable artifact.

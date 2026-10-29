# HTTP hosting behind a reverse proxy

The site uses the official `nginx:1.30.6-alpine3.24` image, pinned by digest in
`deploy/compose.yaml`. No custom image build, PHP, database, or TLS setup is needed.
Your existing reverse proxy owns HTTPS and the public domain. Zola's production
base URL remains `https://zderadicka.eu`.

The container runs one unprivileged Nginx worker on **HTTP port 8080**, with a
read-only root filesystem and read-only site/configuration mounts. Temporary
runtime files use a small tmpfs. Logs go to Docker stdout/stderr; the health check
requests the homepage. The image version/digest should be updated deliberately.

## Start locally

From the repository root, with the authoring dependencies and Docker Compose installed:

```sh
python3 scripts/prepare_hosting.py
docker compose -f deploy/compose.yaml run --rm --no-deps blog -t
docker compose -f deploy/compose.yaml up -d --wait
```

This builds and validates a fresh production artifact, stages an immutable local
release under `.build/hosting/`, and serves it at **http://127.0.0.1:8080/**.
The canonical, asset, and navigation URLs remain production URLs. Use the regular
Python preview when reviewing navigation locally with local URLs.

```sh
docker compose -f deploy/compose.yaml ps
docker compose -f deploy/compose.yaml logs -f blog
docker compose -f deploy/compose.yaml down
```

No live reverse-proxy configuration, DNS, or WordPress service is changed by these commands.

## Connect the reverse proxy

For a proxy running on the same host, set its upstream to `http://127.0.0.1:8080`.
Preserve the public `Host` and forward the client address using your proxy's normal
configuration. Serve the blog at the domain root. The backend does not redirect
HTTP to HTTPS or require forwarded-protocol headers. All backend redirects are
relative, including directory slash redirects, so they do not expose HTTP or a
container port to visitors.

For a proxy already attached to a Docker network, use the optional overlay:

```sh
BLOG_PROXY_NETWORK=your-proxy-network docker compose \
  -f deploy/compose.yaml -f deploy/compose.proxy.yaml up -d --wait
```

Point that proxy at **`http://ivanovo-blog:8080`** on the shared network. The
network must already exist. Use the same Compose file arguments when managing
that setup later.

Overrides can be put in `deploy/.env` (copy `deploy/.env.example`):

- `BLOG_PORT`: published host port, default `8080`.
- `BLOG_BIND`: host bind address, default `127.0.0.1`.
- `BLOG_SITE_ROOT`: release storage on the Docker host, default `../.build/hosting`
  relative to `deploy/`. Absolute paths are convenient on the destination host.
- `BLOG_PROXY_NETWORK`: existing Docker network name, only for the optional overlay.

For example, stage with `python3 scripts/prepare_hosting.py --site-root /srv/blog`
and set `BLOG_SITE_ROOT=/srv/blog` on that same host. For remote Docker daemons,
release storage must be on the daemon host, not merely on the workstation.

## Release layout and updates

```text
.build/hosting/                 # or BLOG_SITE_ROOT on the server
  current -> releases/RELEASE_ID
  releases/
    RELEASE_ID/
      public/                   # only this directory is web-accessible
      nginx-maps.conf           # generated legacy query redirects
      release.json              # checksums and previous release target
```

The container mounts the stable parent at `/site:ro`, with the document root at
`/site/current/public`. Replacing the relative `current` symlink is visible inside
the container without recreation. Operational metadata and redirect configuration
stay outside the document root. Site files are copied from `public/`, never from
the repository root or backups.

For a local content update:

```sh
python3 scripts/prepare_hosting.py
```

That is all for ordinary article, image, CSS, and search-index updates: the running
container sees the new release immediately. No Nginx reload or container restart
is required. The helper reports whether the legacy redirect map changed relative
to the previous release. New posts do not have WordPress IDs and normally leave
that map unchanged.

Only when the helper reports changed legacy redirects, gracefully reload Nginx:

```sh
docker compose -f deploy/compose.yaml exec -T blog nginx -t
docker compose -f deploy/compose.yaml exec -T blog nginx -s reload
```

This reload rereads Nginx configuration without restarting the container. If a
previous update reported changed maps, its reload remains necessary until done,
even if a later update reports the maps unchanged. A first deployment needs the
container startup described above.

The helper always builds production URLs without drafts, copies to a temporary
release, records checksums, then activates it with an atomic symlink replacement.
Failed preparation leaves the active release intact. It retains previous releases.
The reload loads that release's legacy ID maps; ordinary file changes become
visible when the symlink changes. Run staging operations one at a time.

For manual rollback, read the previous relative target from the active
`release.json`, create a temporary symlink to that release, and replace `current`
atomically. If the legacy maps differ between the two releases, validate/reload
Nginx afterwards to restore its matching legacy maps.
For example, from the release storage directory, with the actual previous ID:

```sh
ln -s releases/PREVIOUS_RELEASE .rollback
mv -Tf .rollback current
```

Run the `nginx -t` and `nginx -s reload` commands above if the rollback changes
legacy maps, and check the public site through the proxy. Container recreation is unnecessary. For image, mount, or server configuration changes, recreate the container with
`docker compose -f deploy/compose.yaml up -d --force-recreate --wait`.

This is a local release-staging helper, not an automated remote publisher. SSH
transfer, deployment locking, post-activation health checks with automatic rollback,
release pruning, and compatibility for already-open Pagefind sessions across
content-changing releases remain for the publishing stage. Retaining old release
directories alone does not make their old hashed assets reachable at current URLs.

## HTTP behavior and verification

Nginx serves the built files with directory listing disabled, conditional requests,
gzip for text, and byte ranges for media. HTML and unversioned assets use revalidation
(`Cache-Control: no-cache`), including Pagefind entry points. Unknown routes return
the styled page with an actual HTTP 404 response.

`/rss.xml`, `/feed/`, and archive feeds use `application/rss+xml`.
`/feed/rss2/` redirects to `/feed/`. Known `?p=ID` and `?page_id=ID` requests return
308 redirects, removing the routing parameters while preserving other parameters;
unknown/empty IDs return 404. `?s=` redirects to `/search/?q=`. Historical attachment
pages retain their HTML redirects. No WordPress endpoints are needed.

```sh
python3 -m unittest discover -s tests -v
RUN_DOCKER_TESTS=1 python3 -m unittest discover -s tests -p test_hosting.py -v
```

The opt-in suite creates an isolated temporary Compose project and removes it on
completion. It tests the pinned image/configuration, redirect query ordering and
proxy-safe locations, feed types, HEAD/404 behavior, media ranges, gzip, cache
revalidation, read-only content, symlink activation/rollback, and redirect-map reload.
Ordinary tests run without Docker access and report these integration tests as skipped.

The accepted WordPress snapshot is final. Once destination-host integration is
ready, switch the existing reverse proxy to this HTTP backend, verify the real
URLs/feeds/search/media, and retain the prior WordPress configuration for rollback
during the observation period. No new export is required.

References: [official Nginx image](https://hub.docker.com/_/nginx),
[Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/), and
[Nginx HTTP core directives](https://nginx.org/en/docs/http/ngx_http_core_module.html).

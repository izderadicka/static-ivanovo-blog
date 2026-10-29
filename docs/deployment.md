# Docker deployment and publishing workflow

## Decisions and scope

Serve the generated site from a Docker web-server container, with site files
mounted read-only. Build outside the serving container. Publishing an article
updates the mounted content; it should not require rebuilding the web-server image.

Recommended starting point: Nginx with a host-directory bind mount. This is a
proposal pending the host, existing reverse proxy, and HTTPS arrangement. If a
Docker-managed named volume is preferred, a publisher container must mount it
read-write; do not manipulate Docker's internal volume directories directly.

The regular build emits Nginx adapter examples in `.build/redirects/`, covering legacy queries and extensionless RSS routes. These have not
been deployed or syntax-tested by Nginx here. No publishing script is implemented yet. This document
specifies their intended behavior. The accepted WordPress snapshot is final and promoted; regular publishing uses
only the source Markdown in this repository.

## Filesystem layout

Example on the Docker host:

```text
/srv/blog/
  releases/
    20261028T120000Z-<commit>/   # complete generated public/ contents
    20261029T090000Z-<commit>/
  current -> releases/20261029T090000Z-<commit>
```

Mount the stable parent `/srv/blog` at `/site:ro`; configure the server document
root as `/site/current`. Mount the parent, not the symlink target, so replacing
`current` is visible inside the container. Use relative symlinks whose targets
remain within the mount. Only generated public artifacts belong in release trees;
keep manifests containing operational metadata outside the document root.

Upload into a temporary directory, verify it, rename it to a final release
location, then atomically replace `current` with a newly created symlink using
`os.replace`. Temporary links and their destination must share a filesystem.
Never build into or synchronize files directly over the active release.

For a remote Docker host, transfer artifacts to that host first: a bind mount
references the daemon host's filesystem, not the publishing workstation.

## Everyday author workflow

1. Create `content/posts/article-slug/index.md` with title, date, and `draft = true`.
   Put new article images alongside it. `python3 scripts/new_post.py SLUG --title "Title"` scaffolds a draft and refuses
   to overwrite an existing article.
2. Edit in VS Code and use `python3 scripts/preview.py --drafts` for local review.
   Restart the preview after edits.
3. Use `python3 scripts/build_site.py` to generate a production build with Pagefind. Draft previews must stay separate from production artifacts.
4. Remove the draft flag when ready, review the diff, and commit the article.
5. Run one Python publish command that builds, validates, transfers, activates,
   and checks the release. The publisher should use a clean committed revision
   and record its commit ID, tool versions, and artifact hashes.

Suggested future interface (not executable today):

```sh
python scripts/publish.py new article-slug
python scripts/publish.py preview
python scripts/publish.py publish --target production
python scripts/publish.py rollback --target production --release RELEASE_ID
```

Start with explicit local publishing over SSH when the host is remote. Later, CI
can invoke the same pipeline after an intentional push to a release branch or tag.
Keep credentials outside Git. Decide the release trigger before enabling automatic
production updates. Publishing future-dated posts is not a scheduler: initially
use drafts and explicit publication; add scheduled builds only if needed.

## Publish pipeline

1. Acquire a deployment lock on the destination host so publishers cannot race.
2. Check the target, canonical domain, committed source, disk space, and pinned
   tool versions. Build in an isolated workspace with production settings and
   without `--drafts`. Reject the placeholder domain.
3. Run content/link checks, `zola build`, and Pagefind on the resulting HTML.
   Keep external-link outages separate from hard internal validation failures.
4. Validate expected pages, local assets, feed, search bundle, and absence of
   private/draft content. Produce a checksum manifest for the artifact.
5. Copy the completed artifact to a new temporary release directory. Verify it
   on the target, including file hashes and read permissions. An interrupted
   upload leaves the current release untouched.
6. Finalize the release directory and replace the `current` symlink atomically.
   Retain the previous target for rollback. Content updates normally need no
   container restart; verify symlink/cache behavior with the chosen web server.
7. Check the public homepage, new article, representative media, feed, and search
   assets over HTTP. Check a video byte-range request where videos are hosted.
   On failed checks, restore the previous target under the same lock and report
   the failed release. On first deployment there is no prior target to restore;
   report that condition explicitly and use the initial-cutover rollback plan.
8. Keep several recent releases and prune only after success. Never remove the
   active release or rollback target. Release the lock and print the public URL
   and release ID.

An atomic switch prevents partially uploaded trees, but browsers make multiple
requests and may straddle a release switch. Preserve old fingerprinted assets and
Pagefind bundles through a defined compatibility window, using versioned asset
URLs or a retained asset store served explicitly. Simply keeping old release
folders is insufficient if their assets have no reachable URLs. Test an already
open page and search session across publication before choosing the retention
policy. Avoid long caching for HTML and unversioned search entry points; immutable
caching is appropriate only for versioned assets.

For large media, begin with complete release trees and measure cost. Add transfer
reuse or deduplication if necessary, preserving immutable releases; never mutate
hard-linked assets in place. Keep original media separately backed up.

## Container and host configuration

Planned implementation files: `deploy/compose.yaml`, web-server configuration,
publishing configuration, and `scripts/publish.py`.

- Pin the serving image version/digest and update it deliberately.
- Mount release storage read-only in the web server; grant writes only to the publisher.
- Serve static files with correct MIME types, real 404 responses, directory indexes
  disabled, compression for text, and byte-range support for video seeking.
- Implement WordPress URL redirects in server configuration. Test query-string
  routes separately; no PHP or application fallback is needed.
- Resolve HTTPS termination and port exposure against the existing reverse proxy.
- Validate server configuration before reload; configuration changes may need a
  reload/recreation even though article publication does not.
- Back up content sources, original media, deployment configuration, and release
  metadata. The serving image alone is not a backup of the mounted site.

## Verification before enabling production publishing

Test interrupted transfer, failed build, missing search assets, concurrent publish,
failed health checks, rollback, and retention behavior. Confirm the running container
sees symlink switches without recreation. Check HTTPS, redirects, cache behavior,
search across a release transition, and video playback on the target host.

Open setup details: Docker host/OS and SSH access, bind mount versus named volume,
existing proxy and domain, release storage path, media size, and preferred manual
versus CI publishing trigger. These do not block migration inventory work.

## References

- [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [Docker storage and named volumes](https://docs.docker.com/engine/storage/)
- [Pagefind build integration](https://pagefind.app/docs/running-pagefind/)

## Initial cutover

The existing accepted snapshot is final, as confirmed by the owner. No new
WordPress export is required. Deploy the reviewed production artifact after host
integration and keep the previous WordPress server configuration available for
rollback during the observation period.

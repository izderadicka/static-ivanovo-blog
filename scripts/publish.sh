#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    printf 'Usage: %s user@host:/remote/document-root\n' "$0" >&2
    exit 2
fi

destination=$1
if [[ "$destination" != *:* ]]; then
    printf 'Destination must be a remote rsync path such as user@host:/srv/ivanovo\n' >&2
    exit 2
fi

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
public_dir="$repo_root/public"

if [[ ! -f "$public_dir/index.html" ]]; then
    printf 'No production site found at %s; run python3 scripts/build_site.py first\n' "$public_dir" >&2
    exit 1
fi

rsync --archive --delete --human-readable --progress \
    "$public_dir/" "$destination"

#!/usr/bin/env python3
"""Build and stage a local immutable release for the HTTP hosting container."""
import argparse
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import uuid

from build_site import build
from site_content import ROOT, write_json


def stage(public, maps, site_root):
    site_root = site_root.resolve()
    public = public.resolve()
    if site_root == public or site_root.is_relative_to(public) or public.is_relative_to(site_root):
        raise ValueError('Release storage and build output must not overlap')
    if any(path.is_symlink() for path in public.rglob('*')):
        raise ValueError('Public artifacts must contain ordinary files, not symlinks')
    site_root.mkdir(parents=True, exist_ok=True)
    site_root.chmod(0o755)
    current = site_root / 'current'
    if current.exists() and not current.is_symlink():
        raise ValueError('Expected current to be a release symlink')
    release_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    releases = site_root / 'releases'
    releases.mkdir(exist_ok=True)
    releases.chmod(0o755)
    temporary = releases / ('.upload-' + release_id)
    final = releases / release_id
    link = site_root / ('.current-' + release_id)
    try:
        temporary.mkdir()
        shutil.copytree(public, temporary / 'public')
        shutil.copyfile(maps, temporary / 'nginx-maps.conf')
        hashes = {p.relative_to(temporary).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in temporary.rglob('*') if p.is_file()}
        previous = os.readlink(current) if current.is_symlink() else None
        write_json(temporary / 'release.json', dict(release=release_id, previous=previous, sha256=hashes))
        # Containers run as nginx: make the completed release readable across UIDs.
        for path in temporary.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        temporary.chmod(0o755)
        temporary.rename(final)
        link.symlink_to(Path('releases') / release_id)
        os.replace(link, current)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
        if link.is_symlink():
            link.unlink()
    return final


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-root', type=Path, default=ROOT / '.build/hosting')
    args = parser.parse_args()
    try:
        public = build()
        release = stage(public, ROOT / '.build/redirects/nginx-maps.conf', args.site_root)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Hosting preparation failed: {error}\n')
    print(f'Ready: {release}')
    print('Start/reload the HTTP container to load this release’s legacy URL maps.')


if __name__ == '__main__':
    main()

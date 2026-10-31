#!/usr/bin/env python3
"""Build the editable Zola site, archives, feeds, and Pagefind index."""
import argparse
import re
import shutil
import subprocess
import sys
import tomllib

from site_content import ROOT, read_content, write_json
from validate_site import validate


def require_version(program, pin):
    executable = shutil.which(program)
    if not executable:
        raise ValueError(f'Install {program} {pin} before building')
    version = subprocess.run([executable, '--version'], check=True, capture_output=True, text=True).stdout.strip()
    if not re.search(r'\b' + re.escape(pin) + r'\b', version):
        raise ValueError(f'{program} version mismatch: expected {pin}, found {version}')
    return executable


def build(base_url=None, drafts=False, root=ROOT):
    config = tomllib.loads((root / 'zola.toml').read_text())
    if not config['base_url'].startswith('https://') or 'example.invalid' in config['base_url']:
        raise ValueError('Set the production HTTPS base_url in zola.toml')
    zola = require_version('zola', (root / '.zola-version').read_text().strip())
    pagefind = require_version('pagefind', (root / '.pagefind-version').read_text().strip())
    records = read_content(root, drafts)
    command = [zola, '--root', str(root), 'build']
    if base_url:
        command += ['--base-url', base_url]
    if drafts:
        command.append('--drafts')
    subprocess.run(command, check=True)
    subprocess.run([pagefind, '--site', str(root / 'public'), '--root-selector',
                    '[data-pagefind-body]', '--include-characters', '+#:_/'], check=True)
    subprocess.run([zola, '--root', str(root), 'check', '--skip-external-links'], check=True)
    report = validate(root, records, base_url or config['base_url'])
    write_json(root / '.build/validation.json', report)
    if report['failures']:
        raise ValueError(f"{len(report['failures'])} validation failures; see .build/validation.json")
    print(f"Validated {len(records)} articles/pages and {report['local_links']} local references.")
    return root / 'public'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', help='Override URLs for a review build')
    parser.add_argument('--drafts', action='store_true', help='Include drafts for local review only')
    args = parser.parse_args()
    try:
        build(args.base_url, args.drafts)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Build Zola and its pinned, browser-only Pagefind search index."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys

from migration_source import ROOT, load_config, write_json
from migrate import validate


def require_version(program, pin):
    executable = shutil.which(program)
    if not executable:
        raise ValueError(f'Install {program} {pin} before building')
    version = subprocess.run([executable, '--version'], check=True, capture_output=True, text=True).stdout.strip()
    if not re.search(r'\b' + re.escape(pin) + r'\b', version):
        raise ValueError(f'{program} version mismatch: expected {pin}, found {version}')
    return executable


def build(config_path, base_url=None):
    config, paths = load_config(config_path)
    zola = require_version('zola', (ROOT / '.zola-version').read_text().strip())
    pagefind = require_version('pagefind', (ROOT / '.pagefind-version').read_text().strip())
    command = [zola, '--root', str(paths['site']), 'build']
    if base_url:
        command += ['--base-url', base_url]
    subprocess.run(command, check=True)
    write_json(paths['reports'] / 'build-context.json', {
        'base_url': base_url or config['source']['site_url'],
        'zola': (ROOT / '.zola-version').read_text().strip(),
        'pagefind': (ROOT / '.pagefind-version').read_text().strip(),
    })
    subprocess.run([pagefind, '--site', str(paths['site'] / 'public'),
                    '--root-selector', '[data-pagefind-body]', '--include-characters', '+#:_/'], check=True)
    subprocess.run([zola, '--root', str(paths['site']), 'check', '--skip-external-links'], check=True)
    failures = validate(paths, base_url=base_url)
    if failures:
        raise ValueError(f'{len(failures)} migration validation failures; see validation.json')
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'migration/full.example.toml')
    parser.add_argument('--base-url')
    args = parser.parse_args()
    try:
        build(args.config, args.base_url)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Run deterministic inventory, normalization, and a restricted conversion pilot."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from migration_source import ROOT, content_slugs, digest, inventory, load_config, normalize, routes, write_json
from migration_convert import PILOT_IDS, convert


def generate_pilot(config, paths, records):
    route_map = routes(records, config['source']['site_url'])
    slugs = content_slugs(records)
    selected = config.get('pilot', {}).get('ids', PILOT_IDS)
    if len(selected) != len(set(selected)):
        raise ValueError('Duplicate pilot IDs')
    by_id = {r['id']: r for r in records}
    files, results, issues, originals = {}, [], [], {}
    for ident in selected:
        record = by_id.get(str(ident))
        if record is None or not record['eligible']:
            raise ValueError(f'Pilot ID {ident} is absent or not published')
        content, assets, code, found = convert(record, records, paths, config['source']['site_url'], route_map)
        issues.extend(found)
        ready = not any(x['severity'] == 'error' for x in found)
        results.append(dict(id=record['id'], url=record['url'], ready=ready,
                            code_blocks=len(code), path=route_map[record['id']],
                            content_path=f"content/posts/{slugs[record['id']]}/index.md"))
        if not ready:
            continue
        files[f"content/posts/{slugs[record['id']]}/index.md"] = content.encode('utf-8')
        for relative, source in assets.items():
            files['static/wp-content/uploads/' + relative] = source.read_bytes()
            originals[relative] = digest(source)
    for directory in ('templates', 'static/css'):
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file():
                files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    files['content/_index.md'] = b'+++\ntitle = "Ivanovo pilot"\n+++\n'
    files['content/posts/_index.md'] = b'+++\ntitle = "Pilot articles"\nsort_by = "date"\npage_template = "page.html"\n+++\n'
    files['zola.toml'] = (ROOT / 'zola.toml').read_bytes()
    files['.migration-generated'] = b'WordPress pilot output; regenerate rather than edit.\n'
    output = paths['site']
    # Immutable generated output: identical reruns are allowed, differing or extra
    # files are never overwritten. Choose a fresh site directory for new inputs.
    if output.exists():
        existing = {p.relative_to(output).as_posix(): p for p in output.rglob('*') if p.is_file()}
        if set(existing) != set(files) or any(p.is_symlink() or p.read_bytes() != files[name] for name, p in existing.items()):
            raise ValueError('Staging output differs; choose a fresh output.site directory')
    else:
        for relative, data in sorted(files.items()):
            path = output / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    report = dict(articles=results, issues=issues, comments='omitted', scope='pilot',
                  source_assets=originals, internal_links='full-site targets not yet verified',
                  build_verified=False, wxr_sha256=digest(paths['wxr']),
                  files={name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())})
    write_json(paths['reports'] / 'pilot.json', report)
    return report


def validate(paths):
    report = json.loads((paths['reports'] / 'pilot.json').read_text())
    failures = []
    if digest(paths['wxr']) != report['wxr_sha256']:
        failures.append('Source WXR has changed since conversion')
    for name, expected in report['files'].items():
        path = paths['site'] / name
        if not path.is_file() or path.is_symlink() or digest(path) != expected:
            failures.append('Staged file missing or changed: ' + name)
    from migration_source import local_file
    for name, expected in report.get('source_assets', {}).items():
        original = local_file(paths['uploads'], name)
        if not original.is_file() or digest(original) != expected:
            failures.append('Source media changed or missing: ' + name)
    actual = {p.relative_to(paths['site']).as_posix() for p in paths['site'].rglob('*') if p.is_file()}
    extra = actual - set(report['files'])
    # Zola build artifacts are checked separately once the binary is available.
    failures.extend('Unexpected staging file: ' + name for name in sorted(extra) if not name.startswith(('public/', '.zola-cache/')))
    failures.extend(x['explanation'] for x in report['issues'] if x['severity'] == 'error')
    write_json(paths['reports'] / 'validation.json', dict(failures=failures, zola_build='not verified by this command'))
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('command', choices=('inventory', 'normalize', 'convert', 'validate'))
    args = parser.parse_args()
    try:
        config, paths = load_config(args.config)
        if args.command == 'validate':
            failures = validate(paths)
            print(f'{len(failures)} blocking validation findings; see validation.json')
            return bool(failures)
        records = normalize(paths['wxr'])
        route_map = routes(records, config['source']['site_url'])
        if args.command == 'inventory':
            write_json(paths['reports'] / 'inventory.json', inventory(records, paths, config['source']['site_url']))
        elif args.command == 'normalize':
            write_json(paths['records'] / 'records.json', records)
            write_json(paths['records'] / 'routes.json', route_map)
            write_json(paths['reports'] / 'exclusions.json', [dict(id=r['id'], reason=r['exclusion_reason']) for r in records if not r['eligible']])
        else:
            report = generate_pilot(config, paths, records)
            ready = sum(r['ready'] for r in report['articles'])
            print(f"{ready}/{len(report['articles'])} pilot articles staged; see pilot.json")
            return any(x['severity'] == 'error' for x in report['issues'])
        print(f'{args.command}: {len(records)} source records; {len(route_map)} eligible public routes')
        return 0
    except (ValueError, KeyError, OSError) as error:
        print(f'Migration refused: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

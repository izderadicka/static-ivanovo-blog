#!/usr/bin/env python3
"""Run deterministic inventory, normalization, and staged conversion."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import sys
import tomllib

from migration_source import ROOT, attachment_routes, content_slugs, digest, inventory, load_config, local_file, normalize, routes, write_json
from migration_convert import PILOT_IDS, convert
from migration_validate import source_evidence, validate_build
from migration_site import build_site_model, generated_pages, json_bytes
from migration_routes import nginx_files


def generate_site(config, paths, records):
    scope = config.get('selection', {}).get('scope', 'pilot')
    if scope not in ('pilot', 'all'):
        raise ValueError('selection.scope must be pilot or all')
    route_map = routes(records, config['source']['site_url'])
    slugs = content_slugs(records)
    selected = ([r['id'] for r in records if r['eligible']] if scope == 'all'
                else config.get('pilot', {}).get('ids', PILOT_IDS))
    if len(selected) != len(set(selected)):
        raise ValueError('Duplicate pilot IDs')
    by_id = {r['id']: r for r in records}
    files, results, issues, originals, converted = {}, [], [], {}, {}
    for ident in selected:
        record = by_id.get(str(ident))
        if record is None or not record['eligible']:
            raise ValueError(f'Pilot ID {ident} is absent or not published')
        content, assets, code, found = convert(record, records, paths, config['source']['site_url'], route_map,
                                              config.get('attachment_aliases'))
        issues.extend(found)
        ready = not any(x['severity'] == 'error' for x in found)
        results.append(dict(id=record['id'], kind=record['post_type'], url=record['url'], ready=ready,
                            source_guid=record.get('guid', ''),
                            code_blocks=len(code), source_code=[x['payload'] for x in code],
                            source_languages=[x['language'] for x in code],
                            source_evidence=source_evidence(record['html']),
                            path=route_map[record['id']],
                            content_path=f"content/posts/{slugs[record['id']]}/index.md"))
        if not ready:
            continue
        files[f"content/posts/{slugs[record['id']]}/index.md"] = content.encode('utf-8')
        converted[record['id']] = content
        for relative, source in assets.items():
            files['static/wp-content/uploads/' + relative] = source.read_bytes()
            originals[relative] = digest(source)
    redirects = attachment_routes(records, config['source']['site_url'], config.get('attachment_aliases')) if scope == 'all' else {}
    for old_path, target in redirects.items():
        if old_path in route_map.values() or old_path in ('/', '/posts/'):
            raise ValueError('Attachment and page routes collide')
        relative = target[len('/wp-content/uploads/'):]
        source = local_file(paths['uploads'], relative)
        if source.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.mp4', '.webm', '.wav', '.mp3', '.ogg', '.pdf', '.zip') or not source.is_file():
            raise ValueError('Attachment original is missing or not approved public media')
        files['static' + target] = source.read_bytes()
        originals[relative] = digest(source)
        escaped = html.escape(target, quote=True)
        files['static' + old_path + 'index.html'] = (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<title>Attachment</title><link rel="canonical" href="' + escaped + '">'
            '<meta http-equiv="refresh" content="0;url=' + escaped + '"></head>'
            '<body><a href="' + escaped + '">Open original attachment</a></body></html>\n'
        ).encode('utf-8')
    for directory in ('templates', 'static', 'data'):
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file():
                files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    selected_records = [r for r in records if r['id'] in converted]
    model, cards, listings = build_site_model(selected_records, converted)
    occupied = set(route_map.values()) | set(redirects)
    if occupied & {'/search/', '/archives/', '/rss.xml', '/feed/'}:
        raise ValueError('Source route collides with a generated search/archive/feed route')
    for definition in listings.values():
        if definition['path'] in occupied:
            raise ValueError('Generated archive/feed route collides with a source route: ' + definition['path'])
        occupied.add(definition['path'])
    for ident, card in cards.items():
        card['mdpath'] = f"posts/{slugs[ident]}/index.md"
    files.update(generated_pages(listings))
    files['data/site.json'] = json_bytes(model)
    files.update(nginx_files(results))
    files['content/_generated/_index.md'] = b'+++\ntransparent = true\nrender = false\n+++\n'
    files['content/_index.md'] = b'+++\ntitle = "Ivanovo"\n+++\n'
    files['content/posts/_index.md'] = b'+++\ntitle = "Articles"\nsort_by = "date"\npage_template = "page.html"\n+++\n'
    settings = (ROOT / 'zola.toml').read_text()
    if scope == 'all':
        settings = settings.replace('https://example.invalid', config['source']['site_url']).replace('title = "Technical notes"', 'title = "Ivanovo"')
    files['zola.toml'] = settings.encode('utf-8')
    files['.migration-generated'] = b'WordPress generated output; regenerate rather than edit.\n'
    output = paths['site']
    # Immutable generated output: identical reruns are allowed, differing or extra
    # files are never overwritten. Choose a fresh site directory for new inputs.
    if output.exists():
        existing = {p.relative_to(output).as_posix(): p for p in output.rglob('*')
                    if p.is_file() and not p.relative_to(output).as_posix().startswith(('public/', '.zola-cache/'))}
        if set(existing) != set(files) or any(p.is_symlink() or p.read_bytes() != files[name] for name, p in existing.items()):
            raise ValueError('Staging output differs; choose a fresh output.site directory')
    else:
        for relative, data in sorted(files.items()):
            path = output / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    report = dict(articles=results, issues=issues, comments='omitted', scope=scope,
                  attachment_redirects=redirects, generated_routes=sorted(d['path'] for d in listings.values()) + ['/search/', '/archives/', '/rss.xml', '/feed/'],
                  source_assets=originals, internal_links='full-site targets not yet verified',
                  site_url=config['source']['site_url'], wxr_sha256=digest(paths['wxr']),
                  files={name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())})
    write_json(paths['reports'] / 'conversion.json', report)
    return report


def validate(paths, base_url=None):
    context_path = paths['reports'] / 'build-context.json'
    if base_url is None and context_path.is_file():
        base_url = json.loads(context_path.read_text())['base_url']
    report = json.loads((paths['reports'] / 'conversion.json').read_text())
    failures = []
    if digest(paths['wxr']) != report['wxr_sha256']:
        failures.append('Source WXR has changed since conversion')
    for name, expected in report['files'].items():
        path = paths['site'] / name
        if not path.is_file() or path.is_symlink() or digest(path) != expected:
            failures.append('Staged file missing or changed: ' + name)
    for name, expected in report.get('source_assets', {}).items():
        original = local_file(paths['uploads'], name)
        if not original.is_file() or digest(original) != expected:
            failures.append('Source media changed or missing: ' + name)
    actual = {p.relative_to(paths['site']).as_posix() for p in paths['site'].rglob('*') if p.is_file()}
    extra = actual - set(report['files'])
    # Zola build artifacts are checked separately once the binary is available.
    failures.extend('Unexpected staging file: ' + name for name in sorted(extra) if not name.startswith(('public/', '.zola-cache/')))
    failures.extend(x['explanation'] for x in report['issues'] if x['severity'] == 'error')
    records = normalize(paths['wxr'])
    public_ids = {r['id'] for r in records if r['eligible']}
    staged_ids = {r['id'] for r in report['articles'] if r['ready']}
    if not staged_ids <= public_ids or (report['scope'] == 'all' and staged_ids != public_ids):
        failures.append('Public output does not match eligible source IDs')
    for article in report['articles']:
        if not article['ready']:
            continue
        source = next(r for r in records if r['id'] == article['id'])
        path = paths['site'] / article['content_path']
        if not path.is_file():
            continue
        try:
            metadata = tomllib.loads(path.read_text(encoding='utf-8').split('+++', 2)[1])
        except (IndexError, tomllib.TOMLDecodeError):
            failures.append('Invalid article metadata for ID ' + source['id'])
            continue
        if (metadata['extra']['wordpress_id'] != int(source['id']) or metadata['title'] != source['title']
                or metadata['date'] != source['post_date'].replace(' ', 'T')
                or metadata['extra']['author'] != source['author']
                or json.loads(metadata['extra']['taxonomies_json']) != source['taxonomies']):
            failures.append('Metadata differs from source ID ' + source['id'])
    build_result = None
    if (paths['site'] / 'public/index.html').is_file():
        build_result = validate_build(paths, report, report['site_url'], base_url=base_url)
        failures.extend(x['explanation'] for x in build_result['failures'])
        write_json(paths['reports'] / 'rendered-validation.json', build_result)
    elif report['scope'] == 'all':
        failures.append('Build the full staging site before validation')
    write_json(paths['reports'] / 'validation.json', dict(failures=failures, rendered=build_result))
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
            report = generate_site(config, paths, records)
            ready = sum(r['ready'] for r in report['articles'])
            print(f"{ready}/{len(report['articles'])} articles staged; see conversion.json")
            return any(x['severity'] == 'error' for x in report['issues'])
        print(f'{args.command}: {len(records)} source records; {len(route_map)} eligible public routes')
        return 0
    except (ValueError, KeyError, OSError) as error:
        print(f'Migration refused: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

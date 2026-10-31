"""Read source metadata for authoring checks; Zola owns rendering and navigation."""
from datetime import date, datetime
import json
from pathlib import Path
import re
import tomllib
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def read_article(path):
    text = path.read_text(encoding='utf-8')
    match = re.match(r'\A\+\+\+\r?\n(.*?)\r?\n\+\+\+(?:\r?\n|$)(.*)\Z', text, re.S)
    if not match:
        raise ValueError(f'{path}: expected TOML front matter between +++ lines')
    return tomllib.loads(match[1]), match[2]


def read_content(root=ROOT, drafts=False):
    origin = tomllib.loads((root / 'zola.toml').read_text())['base_url'].rstrip('/')
    records, occupied, ids = [], set(), set()
    static_routes = {'/' + p.relative_to(root / 'static').as_posix()
                     for p in (root / 'static').rglob('*') if p.is_file()}
    for folder, kind in [('posts', 'post'), ('pages', 'page')]:
        for path in sorted((root / 'content' / folder).rglob('*.md')):
            if path.name == '_index.md':
                continue
            meta, _ = read_article(path)
            extra = meta.get('extra', {})
            if meta.get('draft', False) and not drafts:
                continue
            route = meta.get('path')
            if (not isinstance(route, str) or not route.startswith('/') or not route.endswith('/')
                    or '//' in route or '%' in route or '\\' in route or '\x00' in route
                    or any(part in ('.', '..') for part in route.split('/'))
                    or urlsplit(route).query or urlsplit(route).fragment):
                raise ValueError(f'{path}: set an unescaped public path such as /article-slug/')
            if route in occupied or route in ('/', '/search/', '/archives/', '/feed/', '/rss.xml/', '/pages/', '/posts/') or route.startswith('/page/'):
                raise ValueError(f'Duplicate or reserved route: {route}')
            if route + 'index.html' in static_routes or route.rstrip('/') in static_routes:
                raise ValueError(f'Article route overlaps a static asset: {route}')
            occupied.add(route)
            if extra.get('kind', 'post') != kind:
                raise ValueError(f'{path}: {kind}s belong in content/{folder}/')
            if kind == 'page' and meta.get('include_in_feeds', True):
                raise ValueError(f'{path}: standalone pages need include_in_feeds = false')
            stamp = meta.get('date')
            if kind == 'post' and not stamp:
                raise ValueError(f'{path}: posts need a date')
            if stamp:
                datetime.fromisoformat(stamp.isoformat() if isinstance(stamp, (date, datetime)) else stamp)
            ident = extra.get('wordpress_id')
            if ident is not None:
                if type(ident) is not int or ident <= 0 or ident in ids:
                    raise ValueError(f'{path}: wordpress_id must be unique and positive')
                ids.add(ident)
            records.append(dict(url=origin + route, post_type=kind, wordpress_id=ident,
                                include_in_feeds=meta.get('include_in_feeds', True)))
    return records

"""Read editable Markdown and prepare the derived Zola navigation inputs."""
from datetime import date, datetime
import json
from pathlib import Path
import re
import shutil
import tomllib
import unicodedata
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]


def safe_relative(value):
    path = Path(unquote(value))
    if path.is_absolute() or '..' in path.parts or '\\' in value or '\x00' in value:
        raise ValueError(f'Unsafe relative path: {value!r}')
    return path


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def read_article(path):
    text = path.read_text(encoding='utf-8')
    match = re.match(r'\A\+\+\+\r?\n(.*?)\r?\n\+\+\+(?:\r?\n|$)(.*)\Z', text, re.S)
    if not match:
        raise ValueError(f'{path}: expected TOML front matter between +++ lines')
    return tomllib.loads(match[1]), match[2]


def slugify(label):
    normalized = unicodedata.normalize('NFKD', label).casefold()
    return re.sub(r'[^\w]+', '-', ''.join(c for c in normalized if not unicodedata.combining(c))).strip('-')


def read_content(root=ROOT, drafts=False):
    config = tomllib.loads((root / 'zola.toml').read_text())
    origin = config['base_url'].rstrip('/')
    slugs = json.loads((root / 'data/taxonomy-slugs.json').read_text())
    markdown = MarkdownIt('commonmark', {'html': True}).enable('table')
    records, occupied, ids = [], {}, set()
    # Static redirects, media, and generated collections must not shadow articles.
    static_routes = {'/' + p.relative_to(root / 'static').as_posix()
                     for p in (root / 'static').rglob('*') if p.is_file()}
    for path in sorted((root / 'content/posts').rglob('*.md')):
        if path.name == '_index.md':
            continue
        meta, body = read_article(path)
        extra = meta.get('extra', {})
        if meta.get('draft', False) and not drafts:
            continue
        route = meta.get('path')
        if not isinstance(route, str) or not route.startswith('/') or not route.endswith('/') or route.startswith('//'):
            raise ValueError(f'{path}: set an explicit path such as /article-slug/')
        safe_relative(route.lstrip('/'))
        if urlsplit(route).query or urlsplit(route).fragment or '%' in route or '//' in route or '.' in route.split('/'):
            raise ValueError(f'{path}: path must be an unescaped public URL path')
        if route in occupied or route in ('/', '/search/', '/archives/', '/feed/', '/rss.xml/'):
            raise ValueError(f'Duplicate or reserved route: {route}')
        if route + 'index.html' in static_routes or route.rstrip('/') in static_routes:
            raise ValueError(f'Article route overlaps a static asset: {route}')
        occupied[route] = path
        ident = str(extra.get('node_key', route))
        if ident in ids:
            raise ValueError(f'Duplicate article key: {ident}')
        ids.add(ident)
        if extra.get('wordpress_id') is not None and (type(extra['wordpress_id']) is not int or extra['wordpress_id'] <= 0):
            raise ValueError(f'{path}: wordpress_id must be a positive integer')
        kind = extra.get('kind', 'post')
        if kind not in ('post', 'page'):
            raise ValueError(f'{path}: extra.kind must be post or page')
        stamp = meta.get('date')
        if kind == 'post' and not stamp:
            raise ValueError(f'{path}: published posts need a date')
        if isinstance(stamp, (datetime, date)):
            stamp = stamp.isoformat()
        stamp = str(stamp or '1970-01-01T00:00:00')
        datetime.fromisoformat(stamp)
        author = extra.get('author', config.get('author', 'ivan'))
        terms = []
        for key, domain in [('categories', 'category'), ('tags', 'post_tag')]:
            labels = extra.get(key, [])
            if not isinstance(labels, list) or any(not isinstance(label, str) or not label for label in labels):
                raise ValueError(f'{path}: extra.{key} must be an array of nonempty labels')
            for label in labels:
                slug = slugs.get(key, {}).get(label, slugify(label))
                if not slug:
                    raise ValueError(f'{path}: cannot derive taxonomy slug from {label!r}')
                terms.append(dict(domain=domain, name=label, slug=slug))
        records.append(dict(id=ident, wordpress_id=extra.get('wordpress_id'), title=meta['title'],
                            url=origin + route, post_date=stamp, post_type=kind,
                            post_parent=extra.get('parent', ''), menu_order=extra.get('menu_order', 0),
                            author=author, taxonomies=terms, html=markdown.render(body),
                            mdpath=path.relative_to(root / 'content').as_posix()))
    path_ids = {urlsplit(r['url']).path: r['id'] for r in records}
    for record in records:
        parent = record['post_parent']
        if parent and parent not in path_ids:
            raise ValueError(f'Missing parent page: {parent}')
        record['post_parent'] = path_ids.get(parent, '')
    return records


def prepare(root=ROOT, drafts=False):
    from site_model import build_site_model, generated_pages, json_bytes
    from server_routes import nginx_files

    records = read_content(root, drafts)
    model, cards, definitions = build_site_model(records)
    article_routes = {urlsplit(r['url']).path for r in records}
    for definition in definitions.values():
        route = definition['path']
        if route in article_routes:
            raise ValueError(f'Article overlaps a generated archive/feed: {route}')
        target = root / 'static' / route.strip('/')
        if target.is_file() or (target / 'index.html').exists():
            raise ValueError(f'Generated route overlaps a static asset: {route}')
    # This subtree contains only disposable derived pages, never author content.
    generated = root / 'content/_generated'
    if generated.is_symlink():
        raise ValueError('Generated content directory must not be a symlink')
    if generated.exists():
        shutil.rmtree(generated)
    generated.mkdir()
    (generated / '_index.md').write_text('+++\ntransparent = true\nrender = false\n+++\n')
    for relative, data in generated_pages(definitions).items():
        (root / relative).write_bytes(data)
    (root / 'data/site.json').write_bytes(json_bytes(model))
    routes = {str(r['wordpress_id']): urlsplit(r['url']).path for r in records if r['wordpress_id'] is not None}
    write_json(root / '.build/legacy-routes.json', routes)
    for relative, data in nginx_files([dict(id=k, path=v, ready=True) for k, v in routes.items()]).items():
        target = root / '.build' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return records, model

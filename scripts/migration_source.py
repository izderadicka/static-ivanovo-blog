"""Read-only WXR normalization and configured migration boundaries."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tomllib
import unicodedata
from urllib.parse import unquote, urlsplit

from defusedxml import ElementTree

ROOT = Path(__file__).resolve().parents[1]
NS = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
}


def write_json(path, value):
    if path.is_symlink():
        raise ValueError('Refusing symlink report destination')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def overlaps(a, b):
    return a == b or a in b.parents or b in a.parents


def safe_relative(value):
    path = Path(unquote(value))
    if path.is_absolute() or '..' in path.parts or '\\' in value or '\x00' in value:
        raise ValueError(f'Unsafe relative path: {value!r}')
    return path


def local_file(root, value):
    path = (root / safe_relative(value)).resolve()
    if root.resolve() not in path.parents:
        raise ValueError('Asset escapes approved root')
    return path


def load_config(path):
    config = tomllib.loads(path.read_text())
    if config['policy'] != {'published_only': True, 'preserve_upload_paths': True, 'comments': 'omit', 'gists': 'embed'}:
        raise ValueError('This pilot requires published-only output, original upload paths, omitted comments, and remote gist embeds')
    paths = {}
    for key in ('wxr', 'uploads', 'baseline'):
        value = config['source'][key]
        safe_relative(value)
        paths[key] = (ROOT / value).resolve()
        if not paths[key].exists():
            raise ValueError(f'Missing source: {key}')
    for key in ('site', 'reports', 'records'):
        value = config['output'][key]
        safe_relative(value)
        paths[key] = (ROOT / value).resolve()
        parent = ROOT / ('migration/reports' if key == 'reports' else 'migration/work')
        if parent.resolve() not in paths[key].parents and paths[key] != parent.resolve():
            raise ValueError(f'{key} must be inside {parent}')
        if paths[key] == parent.resolve() and key != 'reports':
            raise ValueError('Use a dedicated output subdirectory')
        if any(overlaps(paths[key], paths[source]) for source in ('wxr', 'uploads', 'baseline')):
            raise ValueError('Source and output trees overlap')
    for a, b in (('site', 'records'), ('site', 'reports'), ('records', 'reports')):
        if overlaps(paths[a], paths[b]):
            raise ValueError('Output trees overlap')
    site = urlsplit(config['source']['site_url'])
    if site.scheme not in ('http', 'https') or not site.netloc or site.path not in ('', '/'):
        raise ValueError('site_url must be an HTTP(S) origin')
    return config, paths


def normalize(wxr):
    channel = ElementTree.parse(wxr, forbid_dtd=True, forbid_entities=True,
                                forbid_external=True).find('channel')
    if channel is None:
        raise ValueError('WXR channel missing')
    records = []
    ids = set()
    for item in channel.findall('item'):
        def text(key):
            return item.findtext(key, default='', namespaces=NS)
        record = {key: text('wp:' + key) for key in (
            'post_id', 'post_type', 'status', 'post_name', 'post_date',
            'post_date_gmt', 'post_modified', 'post_modified_gmt', 'post_parent', 'menu_order',
        )}
        record['id'] = record.pop('post_id')
        if not record['id'].isdigit() or record['id'] in ids:
            raise ValueError('Missing, invalid, or duplicate WordPress ID')
        ids.add(record['id'])
        record.update(title=text('title'), url=text('link'), guid=text('guid'), author=text('dc:creator'),
                      html=text('content:encoded'), attachment_url=text('wp:attachment_url'),
                      taxonomies=[dict(domain=x.get('domain'), slug=x.get('nicename'), name=x.text or '')
                                  for x in item.findall('category')],
                      comment_count=len(item.findall('wp:comment', NS)),
                      timezone_evidence='WXR local and GMT timestamps; no named timezone inferred')
        record['eligible'] = record['status'] == 'publish' and record['post_type'] in ('post', 'page')
        record['exclusion_reason'] = None
        if not record['eligible']:
            record['exclusion_reason'] = {
                'attachment': 'Not an article; eligible attachments are handled as media and routes',
                'ml-slider': 'Not an article; sliders are converted in referring pages',
                'nav_menu_item': 'Not an article; navigation metadata retained for theme work',
            }.get(record['post_type'], 'Nonpublic or unsupported article status excluded from output')
        # Comment bodies, email addresses, and IPs are intentionally never normalized.
        records.append(record)
    return sorted(records, key=lambda r: int(r['id']))


def routes(records, site_url):
    result = {}
    seen = set()
    host = urlsplit(site_url).hostname
    for record in records:
        if not record['eligible']:
            continue
        url = urlsplit(record['url'])
        if url.hostname != host or url.query or url.fragment:
            raise ValueError(f"Ambiguous public URL for ID {record['id']}")
        safe_relative(url.path.lstrip('/'))
        path = url.path
        if not path.startswith('/') or path in seen:
            raise ValueError(f'Duplicate/invalid public route: {path}')
        if path in ('/', '/posts/', '/sitemap.xml', '/atom.xml', '/robots.txt', '/404.html') or path.startswith(('/wp-content/', '/css/')):
            raise ValueError(f'Reserved public route: {path}')
        seen.add(path)
        result[record['id']] = path
    return result


def content_slugs(records):
    """Readable directory names independent of public routes and source IDs."""
    def slugify(value):
        value = unicodedata.normalize('NFC', unquote(value)).casefold()
        return re.sub(r'[^\w]+', '-', value.replace('_', '-'), flags=re.UNICODE).strip('-')

    eligible = [record for record in records if record['eligible']]
    slugs = {}
    for record in eligible:
        slug = slugify(record['post_name'] or record['title'])
        if not slug:
            raise ValueError(f"No descriptive content slug for ID {record['id']}")
        slugs[record['id']] = slug
    counts = Counter(slugs.values())
    for record in eligible:
        if counts[slugs[record['id']]] > 1:
            slugs[record['id']] = slugify(urlsplit(record['url']).path)
    if len({slug.casefold() for slug in slugs.values()}) != len(slugs) or not all(slugs.values()):
        raise ValueError('Content directory collision; review source slugs and public paths')
    return slugs


def attachment_routes(records, site_url, aliases=None):
    """Only attachments of published items or unattached public media are eligible."""
    public_ids = {r['id'] for r in records if r['eligible']}
    host = urlsplit(site_url).hostname
    result = {}
    for record in records:
        if record['post_type'] != 'attachment' or record['status'] != 'inherit':
            continue
        if record['post_parent'] not in public_ids | {'0'}:
            continue
        old, target = urlsplit(record['url']), urlsplit(record['attachment_url'])
        if old.hostname != host or target.hostname != host or not target.path.startswith('/wp-content/uploads/'):
            raise ValueError(f"Unsupported attachment URL for ID {record['id']}")
        safe_relative(old.path.lstrip('/'))
        safe_relative(target.path[len('/wp-content/uploads/'):])
        if not old.path.endswith('/') or old.query or target.query:
            raise ValueError('Ambiguous attachment route')
        if old.path in result:
            raise ValueError('Attachment route collision')
        result[old.path] = target.path
    approved_targets = set(result.values())
    for old, target in (aliases or {}).items():
        if not old.startswith('/') or not old.endswith('/') or urlsplit(old).netloc or urlsplit(old).query or urlsplit(old).fragment:
            raise ValueError('Invalid historical attachment path')
        safe_relative(old.lstrip('/'))
        if target not in approved_targets or old in result:
            raise ValueError('Historical attachment mapping must name a public original and a new route')
        result[old] = target
    return result


def inventory(records, paths, site_url):
    uploads = []
    collisions = {}
    for path in sorted(paths['uploads'].rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(paths['uploads']).as_posix()
        local_file(paths['uploads'], relative)
        uploads.append(dict(path=relative, bytes=path.stat().st_size, sha256=digest(path)))
        collisions.setdefault(relative.casefold(), []).append(relative)
    return dict(counts=dict(Counter(r['post_type'] + ':' + r['status'] for r in records)),
                comments_omitted=sum(r['comment_count'] for r in records),
                routes=routes(records, site_url), uploads=uploads,
                case_collisions=[x for x in collisions.values() if len(x) > 1],
                wxr_sha256=digest(paths['wxr']))

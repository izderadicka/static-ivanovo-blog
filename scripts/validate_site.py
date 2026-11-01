"""Offline validation of published routes, links, feed membership, and assets."""
from functools import lru_cache
from pathlib import Path
import tomllib
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

from bs4 import BeautifulSoup


def validate(root, records, base_url, public=None):
    public = (public or root / 'public').resolve()
    origin = tomllib.loads((root / 'zola.toml').read_text())['base_url']
    hosts = {urlsplit(origin).hostname, urlsplit(base_url).hostname}
    failures, checked, feeds = [], 0, 0

    @lru_cache(maxsize=None)
    def document(path):
        return BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')

    @lru_cache(maxsize=None)
    def destination(route):
        path = (public / unquote(route).lstrip('/')).resolve()
        if not path.is_relative_to(public):
            raise ValueError(f'URL escapes the output: {route}')
        return path / 'index.html' if path.is_dir() else path

    def check(route, value):
        nonlocal checked
        if not value or value.startswith(('data:', 'mailto:', 'tel:')):
            return
        url = urlsplit(urljoin(base_url.rstrip('/') + route, value))
        if url.scheme not in ('http', 'https') or url.hostname not in hosts:
            return
        checked += 1
        target = destination(url.path)
        if not target.is_file():
            failures.append(f'{route}: missing local target {value}')
        elif url.fragment and target.suffix == '.html' and not url.fragment.startswith(':~:text='):
            fragment = unquote(url.fragment)
            soup = document(target)
            if not soup.find(id=fragment) and not soup.find('a', attrs={'name': fragment}):
                failures.append(f'{route}: missing fragment {value}')

    expected = {urlsplit(r['url']).path for r in records}
    for route in expected | {'/', '/archives/', '/search/', '/404.html', '/rss.xml', '/feed/'}:
        if not destination(route).is_file():
            failures.append(f'Missing public route: {route}')
    allowed_posts = {urlsplit(r['url']).path for r in records if r['post_type'] == 'post' and r['include_in_feeds']}
    actual_articles = set()
    for path in public.rglob('*'):
        if not path.is_file() or path.suffix not in ('.html', '.xml'):
            continue
        relative = path.relative_to(public).as_posix()
        route = '/' + relative.removesuffix('index.html')
        text = path.read_text(encoding='utf-8')
        if text.lstrip().startswith('<?xml'):
            try:
                tree = ElementTree.fromstring(text)
            except ElementTree.ParseError as error:
                failures.append(f'{route}: invalid XML: {error}')
                continue
            if tree.tag == 'rss':
                feeds += 1
                for item in tree.findall('./channel/item'):
                    if urlsplit(item.findtext('link', '')).path not in allowed_posts:
                        failures.append(f'{route}: feed contains an unpublished post or page')
                    content = item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded', '')
                    if not content:
                        failures.append(f'{route}: RSS item has no full content')
            continue
        soup = document(path)
        if soup.select_one('[data-pagefind-body]'):
            actual_articles.add(route)
        for node in soup.find_all(True):
            values = [node[k] for k in ('href', 'src', 'poster') if node.has_attr(k)]
            if node.has_attr('srcset'):
                values += [part.split()[0] for part in node['srcset'].split(',') if part.split()]
            for value in values:
                check(route, value)
    if actual_articles != expected:
        failures.append('Rendered article set differs from selected Markdown: ' + str(sorted(actual_articles ^ expected)))
    for name in ('pagefind.js', 'pagefind-ui.js', 'pagefind-ui.css'):
        if not (public / 'pagefind' / name).is_file():
            failures.append(f'Missing search asset: {name}')
    return dict(articles=len(records), feeds=feeds, local_links=checked, failures=failures)

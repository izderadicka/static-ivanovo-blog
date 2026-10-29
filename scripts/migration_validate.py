"""Offline checks of built pages, code payloads, public links, and fragments."""
import re
from functools import lru_cache
from xml.etree import ElementTree
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup

from migration_source import digest, local_file


def source_evidence(body):
    soup = BeautifulSoup(body, 'html.parser')
    for paragraph in list(soup.find_all('p')):
        if len(paragraph.contents) == 1 and re.fullmatch(r'https?://(?:youtu\.be/|(?:www\.)?youtube\.com/watch\?)[^\s<>]+', paragraph.get_text().strip()):
            paragraph.decompose()
    inline_code = [n.get_text() for n in soup.find_all('code') if not n.find_parent('pre')]
    for node in soup.find_all(['pre', 'code', 'script', 'form']):
        node.decompose()
    prose = soup.get_text(' ')
    prose = re.sub(r'(?m)^[ \t]*https?://(?:youtu\.be/|(?:www\.)?youtube\.com/watch\?)[^\s<>]+[ \t]*$', '', prose)
    prose = re.sub(r'\[embed\].*?\[/embed\]', '', prose, flags=re.S)
    prose = re.sub(r'\[/?(?:tab|end_tabset|metaslider|audio|video)\b[^\]]*\]', '', prose)
    return dict(inline_code=inline_code, prose_words=prose.split())


def validate_build(paths, report, site_url, base_url=None):
    public = paths['site'] / 'public'
    failures, external = [], set()
    checked_code, checked_inline, checked_links = 0, 0, 0
    parsed = {}
    hosts = {urlsplit(site_url).hostname}
    if base_url:
        hosts.add(urlsplit(base_url).hostname)

    def failure(ident, location, explanation):
        failures.append(dict(id=ident, location=location, explanation=explanation))

    def load(path):
        if path not in parsed:
            parsed[path] = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        return parsed[path]

    @lru_cache(maxsize=None)
    def destination(url):
        name = unquote(url.path).lstrip('/')
        path = local_file(public, name or 'index.html')
        if path.is_dir():
            path = local_file(public, name.rstrip('/') + '/index.html' if name else 'index.html')
        return path

    def check_link(ident, route, value):
        nonlocal checked_links
        if not value or value.startswith(('mailto:', 'tel:', 'data:')):
            return
        url = urlsplit(urljoin(site_url + route, value))
        if url.scheme not in ('http', 'https'):
            failure(ident, route, 'Unexpected URL scheme: ' + value)
            return
        if url.hostname not in hosts:
            external.add(value)
            return
        checked_links += 1
        if url.query and any(re.match(r'(?:p|page_id)=', q) for q in url.query.split('&')):
            failure(ident, route, 'Unconverted WordPress query route: ' + value)
            return
        target = destination(url)
        if not target.is_file():
            failure(ident, route, 'Missing local target: ' + value)
        elif url.fragment and target.suffix == '.html':
            fragment = unquote(url.fragment)
            if not fragment.startswith(':~:text='):
                doc = load(target)
                if not doc.find(id=fragment) and not doc.find('a', attrs={'name': fragment}):
                    failure(ident, route, 'Missing fragment target: ' + value)

    def check_document(ident, route, soup):
        for node in soup.find_all(True):
            values = [node[key] for key in ('href', 'src', 'poster') if node.has_attr(key)]
            if node.has_attr('srcset'):
                values += [item.split()[0] for item in node['srcset'].split(',') if item.split()]
            for value in values:
                check_link(ident, route, value)

    for article in report['articles']:
        ident, route = article['id'], article['path']
        path = destination(urlsplit(route))
        if not article['ready'] or not path.is_file():
            failure(ident, route, 'Published page absent from build')
            continue
        soup = load(path)
        body = soup.find('article')
        if body is None:
            failure(ident, route, 'Article body missing from rendered page')
            continue
        content = body.select_one('.entry-content') or body
        actual_code = [node.get_text() for node in content.find_all('pre')]
        expected_code = article['source_code']
        checked_code += len(expected_code)
        for index, (node, language) in enumerate(zip(content.find_all('pre'), article.get('source_languages', []))):
            if language not in ('', 'text') and not ({'giallo', 'code-highlight'} & set(node.get('class', []))):
                failure(ident, f'{route} code block {index}', 'Code with a known language bypasses highlighting')
        if actual_code != expected_code:
            for index in range(max(len(actual_code), len(expected_code))):
                expected = expected_code[index] if index < len(expected_code) else None
                actual = actual_code[index] if index < len(actual_code) else None
                if actual != expected:
                    failure(ident, f'{route} code block {index}', 'Rendered code differs from source payload')
        if 'source_evidence' in article:
            expected = article['source_evidence']
            checked_inline += len(expected['inline_code'])
            actual = [n.get_text() for n in content.find_all('code') if not n.find_parent('pre')]
            if actual != expected['inline_code']:
                failure(ident, route, 'Rendered inline code differs from source')
            prose = BeautifulSoup(str(content), 'html.parser')
            for node in prose.find_all(['pre', 'code', 'script', 'form', 'time']):
                node.decompose()
            if content is body and prose.h1:
                prose.h1.decompose()
            words = iter(prose.get_text(' ').split())
            for word in expected['prose_words']:
                if not any(candidate == word for candidate in words):
                    failure(ident, route, 'Source prose missing or reordered near word: ' + word)
                    break
        check_document(ident, route, soup)
    generated_count, feed_count = 0, 0
    allowed_feed_paths = {a['path'] for a in report['articles'] if a.get('kind', 'post') == 'post' and a['ready']}
    feed_guids = {a['path']: a.get('source_guid', '') for a in report['articles']}
    for route in report.get('generated_routes', []):
        path = destination(urlsplit(route))
        if not path.is_file():
            failure(None, route, 'Generated archive/search/feed route missing')
            continue
        generated_count += 1
        if route.endswith('/feed/') or route.endswith('.xml'):
            try:
                feed = ElementTree.parse(path)
                if feed.getroot().tag != 'rss':
                    raise ValueError('Expected RSS')
                for item in feed.findall('channel/item'):
                    item_path = urlsplit(item.findtext('link', '')).path
                    if item_path not in allowed_feed_paths:
                        failure(None, route, 'Feed contains a non-post or nonpublic route')
                    elif feed_guids.get(item_path) and item.findtext('guid') != feed_guids[item_path]:
                        failure(None, route, 'Feed changed a source WordPress GUID')
                feed_count += 1
            except (ElementTree.ParseError, ValueError) as error:
                failure(None, route, 'Invalid RSS feed: ' + str(error))
        else:
            check_document(None, route, load(path))
    for old, target in report.get('attachment_redirects', {}).items():
        path = destination(urlsplit(old))
        if not path.is_file() or not destination(urlsplit(target)).is_file():
            failure(None, old, 'Attachment redirect or target missing')
    for name, expected in report.get('source_assets', {}).items():
        path = local_file(public, 'wp-content/uploads/' + name)
        if not path.is_file() or digest(path) != expected:
            failure(None, name, 'Built media differs from source checksum')
    return dict(failures=failures, pages_checked=len(report['articles']), generated_routes_checked=generated_count, feeds_checked=feed_count,
                code_blocks_checked=checked_code, inline_code_checked=checked_inline,
                media_checked=len(report.get('source_assets', {})), local_links_checked=checked_links,
                external_urls=sorted(external), external_urls_checked=False)

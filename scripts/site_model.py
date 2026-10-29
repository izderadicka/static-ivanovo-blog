"""Navigation, archives, and feeds derived from published Markdown articles."""
from collections import defaultdict
from datetime import datetime
import json
import math
import re
import textwrap
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup, Comment

from site_content import safe_relative


def sort_key(value):
    return (0, int(value)) if value.isdigit() else (1, value)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def excerpt_markup(soup, source_url):
    """Keep useful summary links/emphasis without copying executable markup."""
    clean = BeautifulSoup(str(soup), 'html.parser')
    for comment in clean.find_all(string=lambda n: isinstance(n, Comment)):
        comment.extract()
    for node in list(clean.find_all(True)):
        if node.parent is None:
            continue
        if node.name in ('script', 'style', 'form', 'iframe', 'object', 'embed', 'img'):
            node.decompose()
            continue
        if node.name not in ('a', 'strong', 'em', 'b', 'i', 'code', 'p', 'ul', 'ol', 'li', 'br'):
            node.unwrap()
            continue
        href = node.get('href') if node.name == 'a' else None
        node.attrs = {}
        if href:
            target = urlsplit(urljoin(source_url, href))
            if target.scheme not in ('http', 'https', 'mailto'):
                node.unwrap()
            else:
                node['href'] = (urlunsplit(('', '', target.path, target.query, target.fragment))
                                if target.hostname == urlsplit(source_url).hostname else href)
    markup = str(clean).strip()
    return ''.join(part if re.match(r'^<(?:p|ul|ol)\b', part) else '<p>' + part + '</p>'
                   for part in re.split(r'\n\s*\n', markup) if part.strip())


def build_site_model(records):
    cards = {}
    for record in records:
        prefix = re.split(r'<!--\s*more\s*-->|<span id="more-\d+"', record['html'], maxsplit=1)[0]
        excerpt = BeautifulSoup(prefix, 'html.parser')
        for node in excerpt.find_all(['pre', 'script', 'form', 'style']):
            node.decompose()
        text = ' '.join(excerpt.get_text(' ').split())
        image = None
        if excerpt.img:
            image = {key: excerpt.img.get(key, '') for key in ('src', 'srcset', 'sizes', 'width', 'height', 'alt')}
            for key in ('src', 'srcset'):
                if key == 'src':
                    image[key] = urljoin(record['url'], image[key])
                elif image[key]:
                    image[key] = ', '.join(urljoin(record['url'], part.strip().split()[0]) + ' ' +
                                           ' '.join(part.strip().split()[1:]) for part in image[key].split(','))
            parent = excerpt.img.parent
            image['href'] = urljoin(record['url'], parent.get('href', record['url'])) if parent.name == 'a' else record['url']
            for key in ('src', 'href', 'srcset'):
                image[key] = image[key].replace(urlsplit(record['url']).scheme + '://' + urlsplit(record['url']).netloc, '')
        cards[record['id']] = dict(id=record['id'], title=record['title'],
                                  url=urlsplit(record['url']).path, date=record['post_date'][:10],
                                  excerpt=textwrap.shorten(text, width=420, placeholder='…'),
                                  excerpt_html=excerpt_markup(excerpt, record['url']),
                                  image=image, author=record['author'], mdpath=record['mdpath'])
    posts = sorted((r for r in records if r['post_type'] == 'post'),
                   key=lambda r: (r['post_date'], sort_key(r['id'])), reverse=True)
    pages = sorted((r for r in records if r['post_type'] == 'page'),
                   key=lambda r: (int(r.get('menu_order') or 0), sort_key(r['id'])))
    groups = {'categories': {}, 'tags': {}}
    labels, children, neighbors = {}, {}, {}
    for record in records:
        labels[record['id']] = dict(categories=[], tags=[])
        if record['post_type'] != 'post':
            continue
        for term in record['taxonomies']:
            kind = {'category': 'categories', 'post_tag': 'tags'}.get(term['domain'])
            if not kind:
                continue
            slug_path = safe_relative(term['slug'])
            if len(slug_path.parts) != 1 or urlsplit('/' + term['slug']).query or urlsplit('/' + term['slug']).fragment:
                raise ValueError('Taxonomy slug needs a safe single path component')
            prefix = 'category' if kind == 'categories' else 'tag'
            group = groups[kind].setdefault(term['slug'], dict(label=term['name'],
                url=f"/{prefix}/{term['slug']}/", records=[]))
            if group['label'] != term['name']:
                raise ValueError('Taxonomy labels share a slug; add distinct entries to data/taxonomy-slugs.json')
            group['records'].append(record)
            labels[record['id']][kind].append(dict(label=term['name'], url=group['url']))
    for record in pages:
        children[record['id']] = [cards[r['id']] for r in pages if r['post_parent'] == record['id']]
    def tree(record, ancestors=()):
        if record['id'] in ancestors:
            raise ValueError('Cycle in project page hierarchy')
        return dict(title=record['title'], url=cards[record['id']]['url'],
                    children=[tree(r, (*ancestors, record['id'])) for r in pages if r['post_parent'] == record['id']])
    project = next((r for r in pages if cards[r['id']]['url'] == '/projects/'), None)
    projects = tree(project)['children'] if project else []
    for index, record in enumerate(posts):
        neighbors[record['id']] = dict(
            previous=cards[posts[index + 1]['id']] if index + 1 < len(posts) else None,
            next=cards[posts[index - 1]['id']] if index else None)
    collections, generated = {}, {}
    def listing(key, title, url, members):
        ordered = sorted(members, key=lambda r: (r['post_date'], sort_key(r['id'])), reverse=True)
        chunks = [ordered[i:i + 10] for i in range(0, len(ordered), 10)] or [[]]
        for index, chunk in enumerate(chunks):
            suffix = index + 1
            path = url if index == 0 else url + f'page/{suffix}/'
            entry_key = key if index == 0 else key + f'-{suffix}'
            previous = None if not index else (url if index == 1 else url + f'page/{index}/')
            next_url = url + f'page/{suffix + 1}/' if index + 1 < len(chunks) else None
            collections[entry_key] = dict(title=title, items=[cards[r['id']] for r in chunk],
                                          previous=previous, next=next_url, number=suffix, total=len(chunks), url=path)
            if path != '/':
                generated[entry_key] = dict(title=title, path=path, template='listing.html', collection=entry_key)
        if key != 'home':
            generated['feed-' + key] = dict(title=title, path=url + 'feed/', template='feed_page.xml', collection=key)
        return collections[key]
    listing('home', 'Latest articles', '/', posts)
    for kind in ('categories', 'tags'):
        for slug, group in groups[kind].items():
            listing(kind + '-' + slug, group['label'], group['url'], group['records'])
    dates = defaultdict(list)
    for record in posts:
        for length in (4, 7, 10):
            dates[record['post_date'][:length]].append(record)
    for date, members in dates.items():
        fmt = {4: '%Y', 7: '%B %Y', 10: '%B %d, %Y'}[len(date)]
        title = datetime.strptime(date, {4: '%Y', 7: '%Y-%m', 10: '%Y-%m-%d'}[len(date)]).strftime(fmt)
        listing('date-' + date, title, '/' + date.replace('-', '/') + '/', members)
    authors = defaultdict(list)
    for record in posts:
        authors[record['author']].append(record)
    for author, members in authors.items():
        if not re.fullmatch(r'[\w-]+', author):
            if author:
                raise ValueError('Author route needs a reviewed slug')
            continue
        listing('author-' + author, author, '/author/' + author + '/', members)
    months = [dict(label=datetime.strptime(d, '%Y-%m').strftime('%B %Y'), url='/' + d.replace('-', '/') + '/')
              for d in sorted(dates, reverse=True) if len(d) == 7]
    public_groups = {}
    for kind, terms in groups.items():
        public_groups[kind] = [dict(label=g['label'], url=g['url'], count=len(g['records']))
                               for g in sorted(terms.values(), key=lambda g: g['label'].casefold())]
    primary = [dict(title=r['title'], url=cards[r['id']]['url']) for r in pages
               if cards[r['id']]['url'] in ('/about/', '/contact/', '/contribute/')]
    popular = sorted(public_groups['tags'], key=lambda t: (-t['count'], t['label'].casefold()))[:45]
    minimum = min((math.log(t['count']) for t in popular), default=0)
    maximum = max((math.log(t['count']) for t in popular), default=1)
    tag_cloud = [dict(t, size=round(10.67 + (math.log(t['count']) - minimum) / (maximum - minimum or 1) * 18.66, 2))
                 for t in sorted(popular, key=lambda t: t['label'].casefold())]
    model = dict(posts=[cards[r['id']] for r in posts], projects=projects, primary=primary, tag_cloud=tag_cloud,
                 collections=collections, labels=labels, children=children, neighbors=neighbors,
                 months=months, **public_groups)
    model['sitemap_routes'] = sorted({'/'} | {card['url'] for card in cards.values()}
                                     | {d['path'] for d in generated.values() if d['template'] != 'feed_page.xml'}
                                     | {'/archives/'})
    return model, cards, generated


def generated_pages(definitions):
    result = {}
    for index, (key, definition) in enumerate(sorted(definitions.items())):
        front = ['+++', 'title = ' + json.dumps(definition['title'], ensure_ascii=False),
                 'path = ' + json.dumps(definition['path'], ensure_ascii=False),
                 'template = ' + json.dumps(definition['template']),
                 'include_in_feeds = false', 'in_search_index = false', '[extra]',
                 'collection = ' + json.dumps(definition['collection']), '+++', '']
        result[f'content/_generated/listing-{index}.md'] = '\n'.join(front).encode('utf-8')
    for slug, title, template in [('search', 'Search', 'search.html'), ('archives', 'Archives', 'archives.html')]:
        result[f'content/_generated/{slug}.md'] = (f'+++\ntitle = "{title}"\npath = "/{slug}/"\ntemplate = "{template}"\ninclude_in_feeds = false\nin_search_index = false\n+++\n').encode()
    return result

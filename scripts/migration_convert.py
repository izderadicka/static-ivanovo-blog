"""Conservative pilot renderer. Unresolved behavior blocks an article."""
import html
import json
import re
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote

from bs4 import BeautifulSoup, Comment, NavigableString

from migration_source import local_file

PILOT_IDS = ['94', '209', '139', '834', '1096', '1137', '1466', '2112', '2336']


def markdown_text(text):
    """Keep Unicode prose readable while protecting literal Markdown syntax."""
    text = re.sub(r'([\\`*_\[\]<>])', r'\\\1', text)
    # A source spelling such as &amp;lt; represents literal text "&lt;".
    # Prevent Markdown from decoding that text a second time.
    text = re.sub(r'&(?=(?:#[0-9]+|#x[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]+);)', r'\\&', text)
    text = re.sub(r'(?m)^( {0,3})(?=[#+\-])', r'\1\\', text)
    text = re.sub(r'(?m)^( {0,3}\d+)([.)])(?=\s)', r'\1\\\2', text)
    return text


def fence(payload, language=''):
    runs = [len(x) for x in re.findall(r'`+', payload)]
    delimiter = '`' * max(3, max(runs, default=0) + 1)
    # One structural newline belongs to the fence, not the payload.
    return '\n\n' + delimiter + language + '\n' + payload + ('' if payload.endswith('\n') else '\n') + delimiter + '\n\n'


def convert(record, records, paths, site_url, route_map):
    issues, assets, code = [], {}, []
    def issue(message, severity='error'):
        issues.append(dict(id=record['id'], url=record['url'], severity=severity, explanation=message))
    source = BeautifulSoup(record['html'], 'html.parser')
    tokens = {}
    html_tokens = {}
    # Protect code before shortcode processing. Decode entities exactly once via HTML parser.
    for index, node in enumerate(source.find_all('pre')):
        payload = node.get_text()
        language = node.get('data-enlighter-language', '')
        if not language:
            inner = node.find('code')
            classes = node.get('class', []) + (inner.get('class', []) if inner else [])
            language = next((x[9:] for x in classes if x.startswith('language-')), '')
        language = {'js': 'javascript', 'py': 'python', 'rs': 'rust'}.get(language, language)
        if language and language not in ('python', 'rust', 'javascript', 'bash', 'sh', 'text', 'html', 'css', 'json', 'sql', 'c', 'cpp', 'xml'):
            issue(f'Unknown code language {language}; retained as plain code', 'warning')
            language = ''
        if '{{' in payload or '{%' in payload:
            issue('Code contains Zola shortcode delimiters; requires a tested escaping strategy')
        token = f'MIGRATIONCODE{index}PLACEHOLDER'
        if token in record['html']:
            raise ValueError('Code placeholder collision')
        tokens[token] = fence(payload, language)
        html_tokens[token] = '<pre><code>' + html.escape(payload, quote=False) + '</code></pre>'
        code.append(dict(index=index, language=language, payload=payload))
        node.replace_with(NavigableString(token))
    body = str(source)
    def attrs(value):
        return {m.group(1): next(x for x in m.groups()[1:] if x is not None)
                for m in re.finditer(r'''([\w-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s\]]+))''', value)}
    def media(match):
        kind, raw = match.group(1), match.group(2)
        attributes = attrs(raw)
        sources = []
        for ext, mime in (('mp4', 'video/mp4'), ('webm', 'video/webm'), ('wav', 'audio/wav'), ('mp3', 'audio/mpeg'), ('ogg', 'audio/ogg')):
            if ext in attributes:
                sources.append(f'<source src="{html.escape(attributes[ext], quote=True)}" type="{mime}">')
        if not sources:
            issue(f'{kind} shortcode has no supported source')
        poster = f' poster="{html.escape(attributes["poster"], quote=True)}"' if 'poster' in attributes else ''
        return f'<{kind} controls preload="metadata"{poster}>' + ''.join(sources) + f'</{kind}>'
    body = re.sub(r'\[(video|audio)\b([^\]]*)\]', media, body)
    body = re.sub(r'\[/(?:video|audio)\]', '', body)
    body = re.sub(r'\[tab\b([^\]]*)\]', lambda m: '<h2>' + html.escape(attrs(m.group(1)).get('name', 'Section')) + '</h2>', body)
    body = re.sub(r'\[(?:/tab|end_tabset)\]', '', body)
    baseline_path = local_file(paths['baseline'], urlsplit(record['url']).path.lstrip('/') + 'index.html')
    baseline = BeautifulSoup(baseline_path.read_text(), 'html.parser') if baseline_path.is_file() else None
    def gallery(match):
        slider_id = attrs(match.group(1)).get('id', '')
        slider = baseline.find(id='metaslider_' + slider_id) if baseline else None
        if not slider:
            issue(f'Slider {slider_id} has no rendered baseline')
            return ''
        figures = []
        for image in slider.find_all('img'):
            src = urljoin(record['url'], image.get('src', ''))
            caption = image.get('data-caption', '')
            slide = next((x[6:] for x in image.get('class', []) if x.startswith('slide-')), '')
            original = next((r['attachment_url'] for r in records if r['id'] == slide), None)
            if not original:
                issue(f'Slider image {slide} has no attachment original')
                original = src
            figures.append('<figure><a href="' + html.escape(original, quote=True) + '"><img src="' + html.escape(src, quote=True) + '" alt="' + html.escape(image.get('alt', ''), quote=True) + '"></a><figcaption>' + html.escape(caption) + '</figcaption></figure>')
        issue(f'Slider {slider_id} converted to a static gallery preserving order and captions', 'review')
        return ''.join(figures)
    body = re.sub(r'\[metaslider\b([^\]]*)\]', gallery, body)
    def embed(match):
        url = html.unescape(match.group(1).strip())
        parsed = urlsplit(url)
        if parsed.hostname in ('www.youtube.com', 'youtube.com', 'youtu.be'):
            frames = baseline.find_all('iframe') if baseline else []
            video_id = parsed.path.lstrip('/') if parsed.hostname == 'youtu.be' else parsed.query.split('v=')[-1].split('&')[0]
            frame = next((f for f in frames if video_id and '/embed/' + video_id in f.get('src', '')), None)
            if frame:
                return '<iframe title="YouTube video" loading="lazy" allowfullscreen src="' + html.escape(frame['src'], quote=True) + '"></iframe>'
        issue(f'Embed needs reviewed provider mapping: {url}')
        return html.escape(url)
    body = re.sub(r'\[embed\](.*?)\[/embed\]', embed, body, flags=re.S)
    soup = BeautifulSoup(body, 'html.parser')
    approved_behavior = set()
    for node in soup.find_all(['script', 'form']):
        if (node.name == 'script' and set(node.attrs) == {'src'}
                and not node.get_text().strip()
                and re.fullmatch(r'https://gist\.github\.com/[A-Za-z0-9_-]+/[0-9a-f]+\.js', node['src'])):
            approved_behavior.add(id(node))
            issue('GitHub gist retained as a remote embed by owner policy: ' + node['src'], 'review')
        elif (node.name == 'form' and node.get('action') == 'https://www.paypal.com/cgi-bin/webscr'
              and node.get('method', '').lower() == 'post'
              and node.find('input', attrs={'name': 'encrypted'}) is not None):
            approved_behavior.add(id(node))
            issue('Original PayPal contribution form retained; browser submission remains unverified', 'review')
        else:
            issue(f'Unresolved {node.name}: ' + node.get('src', node.get('action', 'inline behavior')))

    known_hosts = {urlsplit(site_url).hostname}
    known_paths = set(route_map.values())
    def rewrite(value, asset=False):
        parsed = urlsplit(value)
        if parsed.scheme and parsed.scheme not in ('http', 'https', 'mailto'):
            issue(f'Unsupported URL scheme: {parsed.scheme}')
            return value
        url = urlsplit(urljoin(record['url'], value))
        if url.hostname not in known_hosts:
            return value
        if url.path.startswith('/wp-content/uploads/'):
            relative = unquote(url.path[len('/wp-content/uploads/'):])
            file = local_file(paths['uploads'], relative)
            if file.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.mp4', '.webm', '.wav', '.mp3', '.ogg', '.pdf', '.zip'):
                issue(f'Unapproved public asset: {relative}')
            elif not file.is_file():
                issue(f'Missing media: {relative}')
            else:
                assets[relative] = file
            return urlunsplit(('', '', url.path, url.query, url.fragment))
        if url.path in known_paths:
            return urlunsplit(('', '', url.path, url.query, url.fragment))
        if asset:
            issue(f'Local asset outside uploads: {value}')
        else:
            issue(f'Internal route needs mapping: {value}', 'warning')
        return value
    for node in soup.find_all(True):
        for name in list(node.attrs):
            if name.lower().startswith('on'):
                issue(f'Inline event handler: {name}')
        for name in ('href', 'src', 'poster'):
            if node.has_attr(name):
                node[name] = rewrite(node[name], asset=name != 'href')
        if node.has_attr('srcset'):
            parts = []
            for candidate in node['srcset'].split(','):
                pieces = candidate.split()
                if pieces:
                    pieces[0] = rewrite(pieces[0], asset=True)
                    parts.append(' '.join(pieces))
            node['srcset'] = ', '.join(parts)
    def render(node):
        if isinstance(node, Comment):
            return '\n\n<!-- more -->\n\n' if str(node).strip() == 'more' else ''
        if isinstance(node, NavigableString):
            text = str(node)
            pattern = '(' + '|'.join(re.escape(t) for t in tokens) + ')' if tokens else None
            if pattern:
                return ''.join(tokens[chunk] if chunk in tokens else markdown_text(chunk)
                               for chunk in re.split(pattern, text))
            return markdown_text(text)
        tag = node.name
        if id(node) in approved_behavior:
            return '\n\n' + str(node) + '\n\n'
        if tag == '[document]':
            return ''.join(render(x) for x in node.children)
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            anchor = '<a id="' + html.escape(node['id'], quote=True) + '"></a>\n' if node.get('id') else ''
            prefix = '#' * int(tag[1]) + ' ' if tag.startswith('h') else ''
            return '\n\n' + anchor + prefix + ''.join(render(x) for x in node.children) + '\n\n'
        if tag in ('strong', 'b', 'em', 'i', 'a', 'code', 'span', 'br', 'img', 'sup', 'sub', 'del'):
            return str(node)
        # Preserve rich blocks as HTML instead of flattening tables/lists/captions.
        if tag in ('ul', 'ol', 'table', 'blockquote', 'figure', 'video', 'audio', 'iframe', 'div', 'dl', 'hr'):
            markup = str(node)
            for token, replacement in html_tokens.items():
                markup = markup.replace(token, replacement)
            return '\n\n' + markup + '\n\n'
        issue(f'Unsupported HTML element: {tag}')
        return str(node)
    markdown = render(soup).strip() + '\n'
    # Known executable WordPress shortcodes must never leak through.
    if re.search(r'\[/?(?:tab|end_tabset|metaslider|audio|video|embed|caption|gallery|crayon)\b', markdown):
        issue('Unconverted WordPress shortcode')
    if '{{' in markdown or '{%' in markdown:
        issue('Zola template/shortcode delimiters need escaping')
    for item in code:
        if (fence(item['payload'], item['language']).strip() not in markdown
                and '<pre><code>' + html.escape(item['payload'], quote=False) + '</code></pre>' not in markdown):
            issue(f"Code payload {item['index']} is absent or changed")
    meta = ['+++', 'title = ' + json.dumps(record['title'], ensure_ascii=False),
            'path = ' + json.dumps(route_map[record['id']], ensure_ascii=False),
            'date = ' + json.dumps(record['post_date'].replace(' ', 'T')),
            '[extra]', 'wordpress_id = ' + record['id'],
            'author = ' + json.dumps(record['author'], ensure_ascii=False),
            'source_url = ' + json.dumps(record['url']),
            'source_date_gmt = ' + json.dumps(record['post_date_gmt']),
            'taxonomies_json = ' + json.dumps(json.dumps(record['taxonomies'], ensure_ascii=False), ensure_ascii=False), '+++', '']
    return '\n'.join(meta) + markdown, assets, code, issues

#!/usr/bin/env python3
"""Build and serve the indexed site, including legacy WordPress URL handling."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit

from build_site import build
from migration_source import ROOT, load_config


class PreviewHandler(SimpleHTTPRequestHandler):
    routes = {}

    def do_GET(self):
        url = urlsplit(self.path)
        query = dict(parse_qsl(url.query, keep_blank_values=True))
        target = None
        status = 308
        if url.path == '/' and ('p' in query or 'page_id' in query):
            ident = query.get('p', query.get('page_id'))
            if ident not in self.routes:
                self.send_error(404)
                return
            target = self.routes[ident]
            remaining = [(k, v) for k, v in parse_qsl(url.query, keep_blank_values=True) if k not in ('p', 'page_id')]
            if remaining:
                target += '?' + urlencode(remaining)
        elif url.path == '/' and query.get('s'):
            target, status = '/search/?' + urlencode({'q': query['s']}), 302
        elif url.path.endswith('/feed/rss2/'):
            target = url.path.removesuffix('rss2/')
        if target:
            self.send_response(status)
            self.send_header('Location', target)
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        super().do_GET()

    def guess_type(self, path):
        if urlsplit(self.path).path.rstrip('/').endswith('/feed'):
            return 'application/rss+xml; charset=utf-8'
        return super().guess_type(path)

    def send_error(self, code, message=None, explain=None):
        page = Path(self.directory) / '404.html'
        if code == 404 and page.is_file():
            data = page.read_bytes()
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(data)
            return
        super().send_error(code, message, explain)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'migration/full.example.toml')
    parser.add_argument('--port', type=int, default=1111)
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--no-build', action='store_true', help='Serve an existing indexed build')
    args = parser.parse_args()
    if args.no_build:
        _, paths = load_config(args.config)
        if not (paths['site'] / 'public/index.html').is_file():
            parser.error('No existing build; omit --no-build')
    else:
        paths = build(args.config, f'http://{args.bind}:{args.port}')
    report = json.loads((paths['reports'] / 'conversion.json').read_text())
    PreviewHandler.routes = {a['id']: a['path'] for a in report['articles'] if a['ready']}
    handler = partial(PreviewHandler, directory=str(paths['site'] / 'public'))
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        print(f'Preview including search: http://{args.bind}:{args.port}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()

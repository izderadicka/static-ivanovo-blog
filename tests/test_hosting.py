"""Opt-in checks of the simple static HTTP container."""
import gzip
import http.client
import os
from pathlib import Path
import socket
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from site_content import ROOT, read_content


@unittest.skipUnless(os.environ.get('RUN_DOCKER_TESTS') == '1',
                     'Set RUN_DOCKER_TESTS=1 to exercise the Docker HTTP server')
class DockerHostingTests(unittest.TestCase):
    @classmethod
    def compose(cls, *args, **kwargs):
        return subprocess.run(['docker', 'compose', '-p', cls.project, '-f',
                               str(cls.root / 'deploy/compose.yaml'), *args],
                              env=cls.environment, check=True, capture_output=True, text=True, **kwargs)

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='ivanovo-http-test-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        shutil.copytree(ROOT / 'deploy', cls.root / 'deploy', ignore=shutil.ignore_patterns('.env'))
        cls.public = cls.root / 'public'
        cls.public.mkdir()
        files = {
            'index.html': '<html>release-one</html>',
            'article/index.html': '<html>Article</html>',
            'category/programming/index.html': '<html>Programming articles</html>',
            'tag/rust/index.html': '<html>Rust articles</html>',
            'projects/index.html': '<html>Projects</html>',
            '404.html': '<html>Styled missing page</html>',
            'feed/index.html': '<?xml version="1.0"?><rss version="2.0"><channel/></rss>',
            'rss.xml': '<?xml version="1.0"?><rss version="2.0"><channel/></rss>',
            'pagefind/pagefind.js': 'export const ready = true;',
            'large.css': 'body { color: green; }\n' * 200,
        }
        for name, body in files.items():
            path = cls.public / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
        cls.video = bytes(range(256)) * 8
        (cls.public / 'movie.mp4').write_bytes(cls.video)
        records = [r for r in read_content(ROOT) if r['wordpress_id'] is not None][:2]
        cls.legacy = [(r['wordpress_id'], r['url'].split('://', 1)[1].split('/', 1)[1]) for r in records]
        for _, route in cls.legacy:
            target = cls.public / route / 'index.html'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('<html>Legacy article</html>')
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            cls.port = listener.getsockname()[1]
        cls.project = 'ivanovo-http-test-' + uuid.uuid4().hex[:8]
        cls.environment = dict(os.environ, BLOG_PORT=str(cls.port), BLOG_BIND='127.0.0.1')
        cls.environment.pop('BLOG_SITE_ROOT', None)
        cls.addClassCleanup(lambda: cls.compose('down', '--volumes', '--remove-orphans'))
        cls.compose('run', '--rm', '--no-deps', 'blog', '-t')
        cls.compose('up', '-d', '--wait', '--wait-timeout', '30')

    @classmethod
    def request(cls, path='/', headers=None, method='GET'):
        connection = http.client.HTTPConnection('127.0.0.1', cls.port, timeout=5)
        connection.request(method, path, headers={'Host': 'blog.example', 'X-Forwarded-Proto': 'https', **(headers or {})})
        response = connection.getresponse()
        status, output_headers, body = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return status, output_headers, body

    def test_static_feeds_and_errors(self):
        for route in ('/article/', '/category/programming/', '/tag/rust/'):
            self.assertEqual(self.request(route)[0], 200)
        self.assertIn('javascript', self.request('/pagefind/pagefind.js')[1]['Content-Type'])
        for path in ('/feed/', '/feed', '/rss.xml'):
            status, headers, body = self.request(path)
            self.assertEqual(status, 200, path)
            self.assertEqual(headers['Content-Type'].split(';')[0], 'application/rss+xml')
            self.assertIn(b'<rss', body)
        status, headers, body = self.request('/does-not-exist/')
        self.assertEqual(status, 404)
        self.assertIn('text/html', headers['Content-Type'])
        self.assertIn(b'Styled missing page', body)
        self.assertEqual(self.request('/nginx-maps.conf')[0], 404)
        status, headers, body = self.request('/article/', method='HEAD')
        self.assertEqual(status, 200)
        self.assertGreater(int(headers['Content-Length']), 0)
        self.assertEqual(body, b'')

    def test_legacy_queries_and_proxy_redirects(self):
        ident, route = self.legacy[0]
        other_id, other_route = self.legacy[1]
        route, other_route = '/' + route, '/' + other_route
        cases = {
            f'/?p={ident}': route,
            f'/?page_id={other_id}': other_route,
            f'/?p={ident}&view=full': route + '?view=full',
            f'/?view=full&p={ident}': route + '?view=full',
            f'/?x=1&p={ident}&y=2': route + '?x=1&y=2',
            f'/?p={ident}&page_id={other_id}&x=1': route + '?x=1',
            '/article': '/article/',
            '/feed/rss2/': '/feed/',
            '/author/ivan/': '/archives/',
            '/category/security-2/': '/category/security/',
            '/tag/plsql/': '/tag/pl-sql/',
            '/2019/03/20/': '/archives/#2019',
        }
        for path, location in cases.items():
            status, headers, _ = self.request(path)
            self.assertIn(status, (301, 308), path)
            self.assertEqual(headers['Location'], location, path)
        self.assertEqual(self.request(f'/?p={ident}', method='HEAD')[0], 308)
        self.assertEqual(self.request('/?s=C%2B%2B')[1]['Location'], '/search/?q=C%2B%2B')
        for path in ('/?p=999999', '/?page_id=999999', '/?p=', f'/?p=999999&page_id={other_id}'):
            self.assertEqual(self.request(path)[0], 404, path)

    def test_ranges_compression_and_caching(self):
        status, headers, body = self.request('/movie.mp4', {'Range': 'bytes=3-13'})
        self.assertEqual(status, 206)
        self.assertEqual(body, self.video[3:14])
        self.assertEqual(headers['Content-Range'], 'bytes 3-13/2048')
        self.assertEqual(headers['Content-Type'], 'video/mp4')
        status, headers, body = self.request('/large.css', {'Accept-Encoding': 'gzip'})
        self.assertEqual(headers['Content-Encoding'], 'gzip')
        self.assertEqual(gzip.decompress(body), (self.public / 'large.css').read_bytes())
        _, headers, _ = self.request('/')
        self.assertIn('no-cache', headers['Cache-Control'])
        self.assertEqual(self.request('/', {'If-None-Match': headers['ETag']})[0], 304)

    def test_read_only_content(self):
        with self.assertRaises(subprocess.CalledProcessError):
            self.compose('exec', '-T', 'blog', 'touch', '/site/should-not-write')
        self.assertFalse((self.public / 'should-not-write').exists())

    def test_content_updates_need_no_reload(self):
        (self.public / 'index.html').write_text('<html>updated-content</html>')
        self.assertIn(b'updated-content', self.request('/')[2])

    def test_z_recreate_serves_replaced_build_directory(self):
        previous = self.root / 'old-public'
        self.public.rename(previous)
        shutil.copytree(previous, self.public)
        (self.public / 'index.html').write_text('<html>fresh-build</html>')
        self.compose('up', '-d', '--force-recreate', '--wait', '--wait-timeout', '30')
        self.assertIn(b'fresh-build', self.request('/')[2])


if __name__ == '__main__':
    unittest.main()

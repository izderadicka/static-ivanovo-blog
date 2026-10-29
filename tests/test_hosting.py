"""Local release checks and opt-in tests of the real HTTP Docker container."""
import gzip
import http.client
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_hosting import stage
from server_routes import nginx_files
from site_content import ROOT


class ReleaseTests(unittest.TestCase):
    def test_failed_stage_preserves_active_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            public = root / 'public'
            public.mkdir()
            (public / 'index.html').write_text('accepted')
            maps = root / 'maps.conf'
            maps.write_text('# maps')
            site = root / 'site'
            first = stage(public, maps, site)
            with self.assertRaises(FileNotFoundError):
                stage(public, root / 'missing.conf', site)
            self.assertEqual((site / 'current').resolve(), first)
            self.assertFalse(list((site / 'releases').glob('.upload-*')))
            (public / 'link').symlink_to(maps)
            with self.assertRaises(ValueError):
                stage(public, maps, site)
            self.assertEqual((site / 'current').resolve(), first)


@unittest.skipUnless(os.environ.get('RUN_DOCKER_TESTS') == '1',
                     'Set RUN_DOCKER_TESTS=1 to exercise the Docker HTTP server')
class DockerHostingTests(unittest.TestCase):
    @classmethod
    def compose(cls, *args, **kwargs):
        return subprocess.run(['docker', 'compose', '-p', cls.project, '-f',
                               str(ROOT / 'deploy/compose.yaml'), *args],
                              env=cls.environment, check=True, capture_output=True, text=True, **kwargs)

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='ivanovo-http-test-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.public = cls.root / 'public'
        cls.public.mkdir()
        files = {
            'index.html': '<html>release-one</html>',
            'article/index.html': '<html>Article</html>',
            'projects/index.html': '<html>Projects</html>',
            '404.html': '<html>Styled missing page</html>',
            'feed/index.html': '<?xml version="1.0"?><rss version="2.0"><channel/></rss>',
            'category/programming/feed/index.html': '<?xml version="1.0"?><rss version="2.0"><channel/></rss>',
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
        cls.maps = cls.root / 'maps.conf'
        cls.maps.write_bytes(nginx_files([dict(id='12', path='/article/', ready=True),
                                        dict(id='43', path='/projects/', ready=True)])['redirects/nginx-maps.conf'])
        cls.site = cls.root / 'site'
        cls.first = stage(cls.public, cls.maps, cls.site)
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            cls.port = listener.getsockname()[1]
        cls.project = 'ivanovo-http-test-' + uuid.uuid4().hex[:8]
        cls.environment = dict(os.environ, BLOG_SITE_ROOT=str(cls.site), BLOG_PORT=str(cls.port), BLOG_BIND='127.0.0.1')
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
        self.assertEqual(self.request('/article/')[0], 200)
        self.assertIn('javascript', self.request('/pagefind/pagefind.js')[1]['Content-Type'])
        for path in ('/feed/', '/feed', '/category/programming/feed/', '/rss.xml'):
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
        cases = {
            '/?p=12': '/article/',
            '/?page_id=43': '/projects/',
            '/?p=12&view=full': '/article/?view=full',
            '/?view=full&p=12': '/article/?view=full',
            '/?x=1&p=12&y=2': '/article/?x=1&y=2',
            '/?p=12&page_id=43&x=1': '/article/?x=1',
            '/?page_id=43&p=12': '/article/',
            '/article': '/article/',
            '/feed/rss2/': '/feed/',
        }
        for path, location in cases.items():
            status, headers, _ = self.request(path)
            self.assertIn(status, (301, 308), path)
            self.assertEqual(headers['Location'], location, path)
        self.assertEqual(self.request('/?p=12', method='HEAD')[0], 308)
        self.assertEqual(self.request('/?s=C%2B%2B')[1]['Location'], '/search/?q=C%2B%2B')
        for path in ('/?p=999999', '/?page_id=999999', '/?p=', '/?p=999999&page_id=43', '/?p=&page_id=43'):
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
            self.compose('exec', '-T', 'blog', 'touch', '/site/current/public/should-not-write')
        self.assertFalse((self.first / 'public/should-not-write').exists())

    def test_z_atomic_release_and_rollback(self):
        (self.public / 'index.html').write_text('<html>release-two</html>')
        self.maps.write_bytes(nginx_files([dict(id='99', path='/article/', ready=True)])['redirects/nginx-maps.conf'])
        second = stage(self.public, self.maps, self.site)
        first = self.first
        self.assertNotEqual(first, second)
        self.assertIn(b'release-two', self.request('/')[2])
        self.compose('exec', '-T', 'blog', 'nginx', '-t')
        self.compose('exec', '-T', 'blog', 'nginx', '-s', 'reload')
        deadline = time.monotonic() + 5
        while self.request('/?p=99')[0] != 308 and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertEqual(self.request('/?p=99')[1]['Location'], '/article/')
        replacement = self.site / '.rollback'
        replacement.symlink_to(Path('releases') / first.name)
        os.replace(replacement, self.site / 'current')
        self.assertIn(b'release-one', self.request('/')[2])
        self.assertTrue(second.is_dir())


if __name__ == '__main__':
    unittest.main()

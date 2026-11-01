"""Authoring and publication regression tests; no WordPress inputs are needed."""
import json
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
import shutil
import sys
import tempfile
import subprocess
import unittest
from unittest.mock import patch
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_site import build
from new_post import create_post
import preview
from site_content import ROOT, read_content
from validate_site import validate


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('templates',):
            shutil.copytree(ROOT / name, self.root / name)
        for name in ('brand', 'css', 'fonts', 'js'):
            shutil.copytree(ROOT / 'static' / name, self.root / 'static' / name)
        for name in ('zola.toml', '.zola-version', '.pagefind-version'):
            shutil.copy2(ROOT / name, self.root / name)
        for folder in ('posts', 'pages', 'archives', 'search'):
            (self.root / 'content' / folder).mkdir(parents=True)
        for name in ('content/_index.md', 'content/posts/_index.md', 'content/pages/_index.md',
                     'content/archives/_index.md', 'content/search/_index.md'):
            shutil.copy2(ROOT / name, self.root / name)

    def article(self, slug, extra='', body='Opening paragraph.\n\n<!-- more -->\n\nFull article.', draft=False, kind='post', taxonomies=None):
        path = self.root / 'content' / ('pages' if kind == 'page' else 'posts') / slug / 'index.md'
        path.parent.mkdir(exist_ok=True)
        path.write_text(f'+++\ntitle = "{slug}"\npath = "/{slug}/"\ndate = "2026-01-01T12:00:00+00:00"\ndraft = {str(draft).lower()}\ninclude_in_feeds = {str(kind == "post").lower()}\n[extra]\nkind = "{kind}"\nauthor = "ivan"\n{extra}\n+++\n{body}\n')
        if taxonomies:
            text = path.read_text()
            taxonomy_text = '[taxonomies]\n' + '\n'.join(key + ' = ' + json.dumps(value) for key, value in taxonomies.items())
            path.write_text(text.replace('\n+++\n', '\n' + taxonomy_text + '\n+++\n', 1))
        return path

    def test_draft_scaffold_and_no_overwrite(self):
        path = create_post('useful-article', 'It’s a "title"', self.root)
        self.assertIn('draft = true', path.read_text())
        self.assertEqual(read_content(self.root), [])
        self.assertEqual(len(read_content(self.root, drafts=True)), 1)
        with self.assertRaises(ValueError):
            create_post('useful-article', 'Other', self.root)
        with self.assertRaises(ValueError):
            create_post('../bad', 'Bad', self.root)

    def test_publication_lifecycle(self):
        first = self.article('first', 'source_guid = "http://old.test/?p=12"\nwordpress_id = 12', taxonomies={'category': ['Programming'], 'tag': ['Rust']})
        self.article('about', kind='page')
        draft = self.article('secret-draft', body='SECRET_DRAFT_SENTINEL', draft=True, taxonomies={'category': ['DraftOnly']})
        image = first.parent / 'diagram.svg'
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        first.write_text(first.read_text().replace('Opening paragraph.', 'Opening with **emphasis**, [a link](/about/), and ![Diagram](diagram.svg).'))
        build(root=self.root)
        self.assertTrue((self.root / 'public/first/diagram.svg').is_file())
        self.assertFalse((self.root / 'public/secret-draft').exists())
        self.assertNotIn('SECRET_DRAFT_SENTINEL', (self.root / 'public/index.html').read_text())
        feed = ElementTree.parse(self.root / 'public/rss.xml')
        self.assertEqual(feed.findtext('./channel/item/guid'), 'http://old.test/?p=12')
        self.assertEqual(len(feed.findall('./channel/item')), 1)
        build(base_url='http://127.0.0.1:12345', drafts=True, root=self.root)
        self.assertTrue((self.root / '.build/preview/secret-draft/index.html').is_file())
        # Publish the draft and remove the old article: all derived models must change.
        draft.write_text(draft.read_text().replace('draft = true', 'draft = false'))
        first.unlink()
        image.unlink()
        first.parent.rmdir()
        build(root=self.root)
        self.assertFalse((self.root / 'public/first').exists())
        self.assertFalse((self.root / 'public/category/programming').exists())
        self.assertFalse((self.root / 'data/site.json').exists())
        self.assertIn('secret-draft', (self.root / 'public/archives/index.html').read_text())
        # A broken internal link is a blocking publication failure.
        (self.root / 'public/secret-draft/index.html').write_text('<a href="/missing/">broken</a><div data-pagefind-body>text</div>')
        records = read_content(self.root)
        self.assertTrue(any('missing local target' in item for item in validate(self.root, records, 'https://zderadicka.eu')['failures']))

    def test_reserved_and_static_route_collisions(self):
        path = self.article('collision')
        original = path.read_text()
        for route in ('/archives/', '/search/', '/feed/', '/page/2/', '/category/programming/', '/tag/rust/', '/../bad/'):
            with self.subTest(route=route):
                path.write_text(original.replace('/collision/', route))
                with self.assertRaises(ValueError):
                    read_content(self.root)
        path.write_text(original)
        target = self.root / 'static/collision/index.html'
        target.parent.mkdir()
        target.write_text('redirect')
        with self.assertRaisesRegex(ValueError, 'static asset'):
            read_content(self.root)

    def test_preview_drafts_never_replace_production_output(self):
        self.article('published')
        build(root=self.root)
        production = (self.root / 'public/index.html').read_bytes()
        draft = self.article('draft', body='[Broken link](/missing/)', draft=True)
        with self.assertRaisesRegex(ValueError, 'validation failures'):
            build(base_url='http://127.0.0.1:1111', drafts=True, root=self.root)
        self.assertTrue((self.root / '.build/preview/draft/index.html').is_file())
        self.assertFalse((self.root / 'public/draft').exists())
        self.assertEqual((self.root / 'public/index.html').read_bytes(), production)
        draft.write_text(draft.read_text().replace('[Broken link](/missing/)', 'DRAFT_SENTINEL'))
        output = build(drafts=True, root=self.root)
        self.assertEqual(output, self.root / '.build/preview')
        self.assertIn('DRAFT_SENTINEL', (output / 'draft/index.html').read_text())
        self.assertEqual((self.root / 'public/index.html').read_bytes(), production)

    def test_preview_always_builds_before_serving(self):
        with patch.object(preview, 'ROOT', self.root), patch.object(sys, 'argv', ['preview.py', '--drafts']):
            with patch.object(preview, 'build', return_value=self.root / 'public') as rebuild:
                with patch.object(preview, 'ThreadingHTTPServer') as server:
                    preview.main()
                    rebuild.assert_called_once_with('http://127.0.0.1:1111', True)
                    server.assert_called_once()
            with patch.object(preview, 'build', side_effect=ValueError('Failed build')):
                with patch.object(preview, 'ThreadingHTTPServer') as server:
                    with self.assertRaisesRegex(ValueError, 'Failed build'):
                        preview.main()
                    server.assert_not_called()

    def test_native_pagination_year_archive_and_feed(self):
        for index in range(12):
            article = self.article(f'post-{index:02}', taxonomies={'category': ['Programming'], 'tag': ['Rust']})
            article.write_text(article.read_text().replace('2026-01-01', f'{2023 + index if index < 3 else 2025}-01-{index + 1:02}'))
        self.article('latest')
        self.article('about', kind='page')
        self.article('draft', draft=True, taxonomies={'category': ['DraftOnly'], 'tag': ['DraftTag']})
        # Rendering works without Python preparing models or generated content.
        subprocess.run(['zola', '--root', str(self.root), 'build'], check=True, capture_output=True)
        from bs4 import BeautifulSoup
        first = BeautifulSoup((self.root / 'public/index.html').read_text(), 'html.parser')
        second = BeautifulSoup((self.root / 'public/page/2/index.html').read_text(), 'html.parser')
        self.assertEqual(len(first.select('.post-summary')), 10)
        self.assertEqual(len(second.select('.post-summary')), 3)
        self.assertEqual(first.select_one('.post-summary h2').get_text(), 'latest')
        archive = BeautifulSoup((self.root / 'public/archives/index.html').read_text(), 'html.parser')
        self.assertEqual([h['id'] for h in archive.select('.archive-year h2')], ['2026', '2025', '2024', '2023'])
        self.assertEqual(len(archive.select('.archive-year li')), 13)
        self.assertNotIn('/about/', str(archive.select('.archive-year')))
        self.assertNotIn('/draft/', str(archive))
        for name in ('author', '2025'):
            self.assertFalse((self.root / 'public' / name).exists())
        sidebar = first.select_one('.sidebar')
        self.assertIsNotNone(sidebar.select_one('a[href$="/category/programming/"]'))
        self.assertIsNotNone(sidebar.select_one('a[href$="/tag/rust/"]'))
        self.assertIsNotNone(sidebar.select_one('a[href$="/archives/"]'))
        self.assertFalse(sidebar.select('a[href*="/archives/#"]'))
        self.assertNotIn('DraftOnly', sidebar.get_text())
        self.assertNotIn('DraftTag', sidebar.get_text())
        for route in ('category/programming', 'tag/rust'):
            listing = BeautifulSoup((self.root / 'public' / route / 'page/2/index.html').read_text(), 'html.parser')
            self.assertEqual(len(listing.select('.post-summary')), 2)
            self.assertFalse((self.root / 'public' / route / 'feed').exists())
        feed = ElementTree.parse(self.root / 'public/rss.xml')
        self.assertEqual(len(feed.findall('./channel/item')), 10)
        self.assertEqual(feed.findtext('./channel/item/title'), 'latest')
        self.assertFalse((self.root / 'data/site.json').exists())
        self.assertFalse((self.root / 'content/_generated').exists())

    def test_feed_dates_preserve_publication_instants(self):
        dates = {'positive': ('2026-01-01T00:30:00+02:00', '2025-12-31T22:30:00+00:00'),
                 'negative': ('2026-01-01T23:30:00-05:00', '2026-01-02T04:30:00+00:00'),
                 'naive': ('2026-01-01T12:00:00', '2026-01-01T12:00:00+00:00'),
                 'migrated': ('2026-01-01T12:00:00+02:00', '2026-01-01T09:00:00+00:00')}
        for slug, (stamp, _) in dates.items():
            extra = 'categories = ["Example"]'
            if slug == 'migrated':
                extra += '\nsource_date_gmt = "2026-01-01 09:00:00"'
            article = self.article(slug, extra)
            article.write_text(article.read_text().replace('2026-01-01T12:00:00+00:00', stamp))
        build(root=self.root)
        for route in ('rss.xml', 'feed/index.html'):
            feed = ElementTree.parse(self.root / 'public' / route)
            actual = {item.findtext('title'): parsedate_to_datetime(item.findtext('pubDate'))
                      for item in feed.findall('./channel/item')}
            self.assertEqual(actual, {slug: datetime.fromisoformat(expected)
                                     for slug, (_, expected) in dates.items()})

    def test_rendering_preserves_code_media_and_gists(self):
        body = ('Opening.\n\n<!-- more -->\n\n```python\n'
                'def example():\n    return "<value>"\n```\n\n'
                '![Diagram](diagram.svg)\n\n'
                '<script src="https://gist.github.com/example/123.js"></script>\n')
        article = self.article('code', body=body)
        (article.parent / 'diagram.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        build(root=self.root)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup((self.root / 'public/code/index.html').read_text(), 'html.parser')
        code = soup.select_one('pre.giallo code')
        self.assertIsNotNone(code)
        self.assertIn('    return "<value>"', code.get_text())
        self.assertIsNotNone(soup.select_one('script[src="https://gist.github.com/example/123.js"]'))
        self.assertTrue((self.root / 'public/code/diagram.svg').is_file())
        self.assertFalse(list((self.root / 'public').rglob('123.js')))

    def test_excerpts_keep_images_and_respect_both_more_markers(self):
        from bs4 import BeautifulSoup
        for slug, separator in [('modern', '<!-- more -->'), ('legacy', '<span id="more-123"></span>'), ('short', '')]:
            body = 'Opening **emphasis**.\n\n![Diagram](diagram.svg)\n\n'
            if separator:
                body += separator + '\n\nAFTER_CUTOFF'
            article = self.article(slug, body=body, taxonomies={'category': ['Programming'], 'tag': ['Rust']})
            (article.parent / 'diagram.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        build(root=self.root)
        for route in ('index.html', 'category/programming/index.html', 'tag/rust/index.html'):
            listing = BeautifulSoup((self.root / 'public' / route).read_text(), 'html.parser')
            summaries = listing.select('.entry-summary')
            self.assertEqual(len(summaries), 3)
            for summary in summaries:
                self.assertIsNotNone(summary.img)
                self.assertIsNotNone(summary.strong)
                self.assertNotIn('AFTER_CUTOFF', summary.get_text())
        full = (self.root / 'public/legacy/index.html').read_text()
        self.assertIn('AFTER_CUTOFF', full)
        self.assertIn('id="more-123"', full)

    def test_standalone_pages_stay_out_of_feeds(self):
        page = self.article('about', kind='page')
        page.write_text(page.read_text().replace('include_in_feeds = false', 'include_in_feeds = true'))
        with self.assertRaisesRegex(ValueError, 'include_in_feeds'):
            read_content(self.root)


if __name__ == '__main__':
    unittest.main()

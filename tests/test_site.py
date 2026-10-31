"""Authoring and publication regression tests; no WordPress inputs are needed."""
from contextlib import redirect_stderr
from datetime import datetime
from email.utils import parsedate_to_datetime
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_site import build
from new_post import create_post
import preview
from site_content import ROOT, prepare, read_content
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
        (self.root / 'content/posts').mkdir(parents=True)
        (self.root / 'data').mkdir()
        (self.root / 'data/taxonomy-slugs.json').write_text('{"categories": {}, "tags": {}}')
        for name in ('content/_index.md', 'content/posts/_index.md'):
            shutil.copy2(ROOT / name, self.root / name)

    def article(self, slug, extra='', body='Opening paragraph.\n\n<!-- more -->\n\nFull article.', draft=False, kind='post'):
        path = self.root / 'content/posts' / slug / 'index.md'
        path.parent.mkdir(exist_ok=True)
        path.write_text(f'+++\ntitle = "{slug}"\npath = "/{slug}/"\ndate = "2026-01-01T12:00:00+00:00"\ndraft = {str(draft).lower()}\n[extra]\nkind = "{kind}"\nauthor = "ivan"\n{extra}\n+++\n{body}\n')
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
        first = self.article('first', 'categories = ["Programming"]\ntags = ["Rust"]\nsource_guid = "http://old.test/?p=12"\nwordpress_id = 12')
        self.article('about', kind='page')
        draft = self.article('secret-draft', 'categories = ["DraftOnly"]', body='SECRET_DRAFT_SENTINEL', draft=True)
        image = first.parent / 'diagram.svg'
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        first.write_text(first.read_text().replace('Opening paragraph.', 'Opening with **emphasis**, [a link](/about/), and ![Diagram](diagram.svg).'))
        build(root=self.root)
        model = json.loads((self.root / 'data/site.json').read_text())
        self.assertEqual(len(model['posts']), 1)
        self.assertIn('<strong>emphasis</strong>', model['posts'][0]['excerpt_html'])
        self.assertEqual(model['posts'][0]['image']['src'], '/first/diagram.svg')
        self.assertTrue((self.root / 'public/first/diagram.svg').is_file())
        self.assertFalse((self.root / 'public/secret-draft').exists())
        self.assertNotIn('SECRET_DRAFT_SENTINEL', (self.root / 'public/index.html').read_text())
        feed = ElementTree.parse(self.root / 'public/rss.xml')
        self.assertEqual(feed.findtext('./channel/item/guid'), 'http://old.test/?p=12')
        self.assertEqual(len(feed.findall('./channel/item')), 1)
        self.assertEqual(json.loads((self.root / '.build/legacy-routes.json').read_text()), {'12': '/first/'})
        build(base_url='http://127.0.0.1:12345', drafts=True, root=self.root)
        self.assertTrue((self.root / 'public/secret-draft/index.html').is_file())
        # Publish the draft and remove the old article: all derived models must change.
        draft.write_text(draft.read_text().replace('draft = true', 'draft = false'))
        first.unlink()
        image.unlink()
        first.parent.rmdir()
        build(root=self.root)
        model = json.loads((self.root / 'data/site.json').read_text())
        self.assertEqual([p['title'] for p in model['posts']], ['secret-draft'])
        self.assertFalse((self.root / 'public/first').exists())
        self.assertFalse((self.root / 'public/category/programming').exists())
        self.assertTrue((self.root / 'public/category/draftonly/index.html').is_file())
        self.assertEqual(json.loads((self.root / '.build/legacy-routes.json').read_text()), {})
        # A broken internal link is a blocking publication failure.
        (self.root / 'public/secret-draft/index.html').write_text('<a href="/missing/">broken</a><div data-pagefind-body>text</div>')
        records, model = prepare(self.root)
        self.assertTrue(any('missing local target' in item for item in validate(self.root, records, model, 'https://zderadicka.eu')['failures']))

    def test_archive_and_static_route_collisions(self):
        self.article('example', 'categories = ["Programming"]')
        path = self.article('collision')
        path.write_text(path.read_text().replace('/collision/', '/category/programming/'))
        with self.assertRaisesRegex(ValueError, 'overlaps a generated'):
            prepare(self.root)
        path.unlink()
        target = self.root / 'static/example/index.html'
        target.parent.mkdir()
        target.write_text('redirect')
        with self.assertRaisesRegex(ValueError, 'static asset'):
            prepare(self.root)

    def test_failed_draft_build_cannot_be_reused(self):
        self.article('published')
        base_url = 'http://127.0.0.1:1111'
        build(base_url=base_url, root=self.root)
        self.article('draft', body='[Broken link](/missing/)', draft=True)
        with self.assertRaisesRegex(ValueError, 'validation failures'):
            build(base_url=base_url, drafts=True, root=self.root)
        self.assertTrue((self.root / 'public/draft/index.html').is_file())
        errors = io.StringIO()
        with patch.object(preview, 'ROOT', self.root), patch.object(sys, 'argv', ['preview.py', '--no-build']):
            with redirect_stderr(errors), self.assertRaises(SystemExit) as stopped:
                preview.main()
        self.assertEqual(stopped.exception.code, 2)
        self.assertIn('No existing build', errors.getvalue())
        build(base_url=base_url, root=self.root)
        self.assertFalse((self.root / 'public/draft').exists())
        self.assertEqual(json.loads((self.root / '.build/context.json').read_text()),
                         dict(base_url=base_url, drafts=False))

    def test_numbered_taxonomies_and_authors_keep_paginated_routes(self):
        for index in range(11):
            self.article(f'foo-post-{index}', 'categories = ["foo"]\ntags = ["foo"]')
        other = self.article('other', 'categories = ["foo-2"]\ntags = ["foo-2"]')
        other.write_text(other.read_text().replace('author = "ivan"', 'author = "ivan-2"'))
        build(root=self.root)
        for prefix, slug, numbered in [('category', 'foo', 'foo-2'),
                                       ('tag', 'foo', 'foo-2'),
                                       ('author', 'ivan', 'ivan-2')]:
            with self.subTest(prefix=prefix):
                page = self.root / 'public' / prefix / slug / 'page/2/index.html'
                self.assertIn('foo-post-', page.read_text())
                separate = self.root / 'public' / prefix / numbered / 'index.html'
                self.assertIn('other', separate.read_text())

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
        for route in ('rss.xml', 'feed/index.html', 'category/example/feed/index.html'):
            feed = ElementTree.parse(self.root / 'public' / route)
            actual = {item.findtext('title'): parsedate_to_datetime(item.findtext('pubDate'))
                      for item in feed.findall('./channel/item')}
            self.assertEqual(actual, {slug: datetime.fromisoformat(expected)
                                     for slug, (_, expected) in dates.items()})

    def test_year_pagination_does_not_replace_october_archive(self):
        for index in range(91):
            self.article(f'january-{index}')
        october = self.article('october')
        october.write_text(october.read_text().replace('2026-01-01', '2026-10-01'))
        build(root=self.root)
        yearly = (self.root / 'public/2026/page/10/index.html').read_text()
        monthly = (self.root / 'public/2026/10/index.html').read_text()
        self.assertIn('january-', yearly)
        self.assertIn('october', monthly)

    def test_taxonomy_and_parent_validation(self):
        self.article('example', 'tags = ["C++", "C#"]')
        with self.assertRaisesRegex(ValueError, 'share a slug'):
            prepare(self.root)
        (self.root / 'data/taxonomy-slugs.json').write_text('{"tags":{"C++":"cpp","C#":"csharp"}}')
        prepare(self.root)
        self.article('project', 'parent = "/absent/"', kind='page')
        with self.assertRaisesRegex(ValueError, 'Missing parent'):
            prepare(self.root)

    def test_metadata_and_generated_cleanup(self):
        self.article('example', 'categories = ["Programming"]')
        prepare(self.root)
        stale = self.root / 'content/_generated/stale.md'
        stale.write_text('stale generated route')
        prepare(self.root)
        self.assertFalse(stale.exists())
        path = self.article('bad')
        path.write_text(path.read_text().replace('/bad/', '/../bad/'))
        with self.assertRaises(ValueError):
            prepare(self.root)


if __name__ == '__main__':
    unittest.main()

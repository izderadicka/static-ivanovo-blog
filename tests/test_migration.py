"""Synthetic regression fixtures; run with python3 -m unittest discover -s tests."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import shutil
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from defusedxml.common import DefusedXmlException
from migration_source import attachment_routes, content_slugs, load_config, local_file, normalize, routes, write_json
from migration_convert import convert
from migrate import generate_site, validate

WXR = '''<rss xmlns:wp="http://wordpress.org/export/1.2/"
xmlns:content="http://purl.org/rss/1.0/modules/content/"
xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>
<item><title>Example &amp; title</title><link>http://example.test/example/</link>
<wp:post_id>1</wp:post_id><wp:post_type>post</wp:post_type>
<wp:post_name>example</wp:post_name><guid isPermaLink="false">http://old.example.test/?p=1</guid>
<wp:status>publish</wp:status><wp:post_date>2020-01-01 12:00:00</wp:post_date>
<content:encoded><![CDATA[<p>Hello</p>]]></content:encoded>
<wp:comment><wp:comment_content>SECRET COMMENT</wp:comment_content>
<wp:comment_author_email>secret@example.test</wp:comment_author_email></wp:comment>
</item></channel></rss>'''


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.wxr = self.root / 'source.xml'
        self.wxr.write_text(WXR)
        self.record = normalize(self.wxr)[0]
        self.paths = dict(wxr=self.wxr, uploads=self.root / 'uploads', baseline=self.root / 'baseline',
                          site=self.root / 'site', records=self.root / 'records', reports=self.root / 'reports')
        self.paths['uploads'].mkdir()
        self.paths['baseline'].mkdir()
        self.site_url = 'https://example.test'

    def render(self, body):
        self.record['html'] = body
        return convert(self.record, [self.record], self.paths, self.site_url, {'1': '/example/'})

    def test_comments_are_not_normalized(self):
        data = json.dumps(normalize(self.wxr))
        self.assertNotIn('SECRET COMMENT', data)
        self.assertNotIn('secret@example.test', data)
        self.assertEqual(self.record['comment_count'], 1)

    def test_private_is_excluded_even_with_public_link(self):
        self.wxr.write_text(WXR.replace('<wp:status>publish', '<wp:status>private'))
        records = normalize(self.wxr)
        self.assertFalse(records[0]['eligible'])
        self.assertEqual(routes(records, self.site_url), {})

    def test_xml_entities_and_dtd_are_rejected(self):
        self.wxr.write_text('<!DOCTYPE rss [<!ENTITY x SYSTEM "file:///etc/passwd">]>' + WXR)
        with self.assertRaises(DefusedXmlException):
            normalize(self.wxr)

    def test_duplicate_ids_rejected(self):
        item = WXR.split('<item>')[1].split('</item>')[0]
        self.wxr.write_text(WXR.replace('</channel>', '<item>' + item + '</item></channel>'))
        with self.assertRaises(ValueError):
            normalize(self.wxr)

    def test_route_collisions_and_traversal_rejected(self):
        other = copy.deepcopy(self.record)
        other['id'] = '2'
        with self.assertRaises(ValueError):
            routes([self.record, other], self.site_url)
        self.record['url'] = 'http://example.test/%2e%2e/secret/'
        with self.assertRaises(ValueError):
            routes([self.record], self.site_url)

    def test_asset_traversal_and_symlink_rejected(self):
        for name in ('../secret', '%2e%2e/secret', '/secret'):
            with self.assertRaises(ValueError):
                local_file(self.paths['uploads'], name)
        (self.paths['uploads'] / 'escape').symlink_to(self.root)
        with self.assertRaises(ValueError):
            local_file(self.paths['uploads'], 'escape/source.xml')

    def test_code_entities_whitespace_multiple_blocks_and_fences(self):
        markdown, assets, code, issues = self.render(
            '<pre>\tif x &lt; 2:\n\n  print(&quot;&amp;lt;&quot;)\n```\n</pre>'
            '<pre>next\n</pre>')
        self.assertEqual(code[0]['payload'], '\tif x < 2:\n\n  print("&lt;")\n```\n')
        self.assertIn('````\n' + code[0]['payload'] + '\n````', markdown)
        self.assertIn('```\nnext\n\n```', markdown)
        self.assertFalse(issues)

    def test_code_in_list_retained_as_html(self):
        markdown, _, code, issues = self.render('<ol><li>Run<pre>\t&lt;x&gt; &amp;amp;\n</pre></li></ol>')
        self.assertEqual(code[0]['payload'], '\t<x> &amp;\n')
        from bs4 import BeautifulSoup
        self.assertEqual(BeautifulSoup(markdown, 'html.parser').pre.get_text(), '\t<x> &amp;\n')
        self.assertFalse(issues)

    def test_unicode_prose_and_quotes_stay_readable(self):
        markdown, _, _, issues = self.render(
            '<p>It&#x27;s &#x27;beta&#x27; &quot;obvious&quot; — café, příliš, 日本語 &amp; more.</p>'
            '<p><em>It&#39;s “ready”</em></p>')
        self.assertIn('It\'s \'beta\' "obvious" — café, příliš, 日本語 & more.', markdown)
        self.assertIn('<em>It\'s “ready”</em>', markdown)
        for entity in ('&#x27;', '&#39;', '&quot;', '&amp;'):
            self.assertNotIn(entity, markdown)
        self.assertFalse(issues)

    def test_literal_entities_and_markup_are_not_decoded_twice(self):
        markdown, _, _, issues = self.render('<p>&amp;lt; &lt;tag&gt; *literal* [text] 2_3</p>')
        self.assertIn(r'\&lt; \<tag\> \*literal\* \[text\] 2\_3', markdown)
        self.assertFalse(issues)

    def test_html_attribute_escaping_and_code_quotes_are_preserved(self):
        markdown, _, code, issues = self.render(
            '<a href="https://other.test/?x=1&amp;y=2" title="&quot;quoted&quot;">link</a>'
            '<pre>print(&quot;It&#39;s β&quot;)\n</pre>')
        self.assertIn('x=1&amp;y=2', markdown)
        self.assertEqual(code[0]['payload'], 'print("It\'s β")\n')
        self.assertIn('print("It\'s β")', markdown)
        self.assertFalse(issues)

    def test_descriptive_content_slugs_and_public_paths_are_independent(self):
        self.record['post_name'] = 'higher-rank-trait-bounds'
        self.record['url'] = 'http://example.test/higher-rank/'
        self.assertEqual(content_slugs([self.record]), {'1': 'higher-rank-trait-bounds'})
        self.assertEqual(routes([self.record], self.site_url), {'1': '/higher-rank/'})
        self.record['post_name'] = ''
        self.record['title'] = 'Příliš žluťoučký kůň!'
        self.assertEqual(content_slugs([self.record])['1'], 'příliš-žluťoučký-kůň')

    def test_duplicate_slugs_use_informative_parent_paths(self):
        other = copy.deepcopy(self.record)
        other.update(id='2', url='http://example.test/projects/example/')
        self.assertEqual(content_slugs([other, self.record]), {'1': 'example', '2': 'projects-example'})
        third = copy.deepcopy(other)
        third.update(id='3', post_name='projects-example', url='http://example.test/elsewhere/')
        with self.assertRaises(ValueError):
            content_slugs([self.record, other, third])

    def test_zola_delimiters_are_preserved_as_literal_code(self):
        markdown, _, code, issues = self.render('<pre>{{ dangerous() }} {% value %}</pre>')
        self.assertNotIn('{{', markdown)
        self.assertEqual(code[0]['payload'], '{{ dangerous() }} {% value %}')
        self.assertFalse(issues)

    def test_gists_remain_remote_and_other_scripts_block(self):
        url = 'https://gist.github.com/example/123abc.js'
        markdown, _, code, issues = self.render('<script src="' + url + '"></script>')
        self.assertIn(url, markdown)
        self.assertFalse(code)
        self.assertFalse(any(x['severity'] == 'error' for x in issues))
        for markup in ('<script>alert(1)</script>', '<script src="https://other.test/x.js"></script>',
                       '<script src="' + url + '">alert(1)</script>'):
            self.assertTrue(any(x['severity'] == 'error' for x in self.render(markup)[3]))

    def test_assets_rewrite_without_losing_fragments_and_missing_block(self):
        (self.paths['uploads'] / 'image.png').write_bytes(b'original')
        markdown, assets, _, issues = self.render('<img src="http://example.test/wp-content/uploads/image.png"><a href="http://example.test/example/#part">link</a>')
        self.assertIn('src="/wp-content/uploads/image.png"', markdown)
        self.assertIn('href="/example/#part"', markdown)
        self.assertEqual(assets['image.png'].read_bytes(), b'original')
        self.assertFalse(issues)
        self.assertTrue(any(x['severity'] == 'error' for x in self.render('<img src="/wp-content/uploads/missing.png">')[3]))

    def test_backups_and_executable_assets_block(self):
        _, assets, _, issues = self.render('<img src="/wp-content/uploads/temp.php">')
        self.assertFalse(assets)
        self.assertTrue(any(x['severity'] == 'error' for x in issues))

    def test_config_overlap_and_curated_destinations_block(self):
        config = Path(__file__).resolve().parents[1] / 'migration/config.example.toml'
        for original, replacement in (
            ('migration/work/pilot-candidate', 'content'),
            ('migration/work/pilot-candidate', 'migration/source'),
            ('migration/work/normalized', 'migration/work/pilot-candidate/records'),
        ):
            path = self.root / 'bad.toml'
            path.write_text(config.read_text().replace(original, replacement))
            with self.assertRaises(ValueError):
                load_config(path)

    def test_report_symlink_not_overwritten(self):
        link = self.root / 'link.json'
        link.symlink_to(self.wxr)
        with self.assertRaises(ValueError):
            write_json(link, {})
        self.assertEqual(self.wxr.read_text(), WXR)

    def test_deterministic_output_and_editorial_protection(self):
        config = dict(source={'site_url': self.site_url}, pilot={'ids': ['1']})
        first = generate_site(config, self.paths, [self.record])
        second = generate_site(config, self.paths, [self.record])
        self.assertEqual(first, second)
        self.assertEqual(validate(self.paths), [])
        target = self.paths['site'] / 'content/posts/example/index.md'
        target.write_text('editorial change')
        with self.assertRaises(ValueError):
            generate_site(config, self.paths, [self.record])
        self.assertTrue(validate(self.paths))
        self.assertEqual(target.read_text(), 'editorial change')

    def test_private_cannot_be_selected_for_pilot(self):
        self.record['eligible'] = False
        with self.assertRaises(ValueError):
            generate_site(dict(source={'site_url': self.site_url}, pilot={'ids': ['1']}),
                           self.paths, [self.record])

    def test_nested_and_template_code_keep_language_highlighting(self):
        from bs4 import BeautifulSoup
        markdown, _, code, issues = self.render(
            '<ol><li>Run<pre class="lang:python">def f():\n\n\treturn 1</pre></li></ol>'
            '<pre class="lang:js">const value = "{{ value }}";\n</pre>')
        blocks = BeautifulSoup(markdown, 'html.parser').find_all('pre')
        self.assertEqual([b.get_text() for b in blocks], [c['payload'] for c in code])
        self.assertTrue(all('code-highlight' in b['class'] for b in blocks))
        self.assertTrue(all(b.select('span.k, span.kd, span.kr, span.nf') for b in blocks))
        self.assertFalse(issues)

    def test_automatic_youtube_embed_only_for_standalone_urls(self):
        for standalone in ('https://youtu.be/EGfTJuSiGeE', '<p>https://youtu.be/EGfTJuSiGeE</p>'):
            markdown, _, code, issues = self.render(
                standalone + '\n\nSee https://youtu.be/EGfTJuSiGeE for details.\n'
                '<pre>https://youtu.be/EGfTJuSiGeE</pre>')
            self.assertEqual(markdown.count('<iframe'), 1)
            self.assertIn('https://www.youtube.com/embed/EGfTJuSiGeE', markdown)
            self.assertIn('Watch on YouTube', markdown)
            from bs4 import BeautifulSoup
            self.assertIsNotNone(BeautifulSoup(markdown, 'html.parser').select_one('.embed-fallback a'))
            self.assertIn('See https://youtu.be/EGfTJuSiGeE for details.', markdown)
            self.assertEqual(code[0]['payload'], 'https://youtu.be/EGfTJuSiGeE')
            self.assertFalse(issues)

    def test_responsive_variants_are_vetted_copied_and_lazy_loaded(self):
        (self.paths['uploads'] / 'image.png').write_bytes(b'original')
        (self.paths['uploads'] / 'image-300x200.png').write_bytes(b'variant')
        old = self.paths['baseline'] / 'example'
        old.mkdir()
        (old / 'index.html').write_text('<img src="../wp-content/uploads/image.png" '
            'srcset="../wp-content/uploads/image-300x200.png 300w, ../wp-content/uploads/image.png 900w" '
            'sizes="(max-width: 900px) 100vw, 900px" width="900" height="600" loading="lazy">')
        markdown, assets, _, issues = self.render('<img src="http://example.test/wp-content/uploads/image.png" alt="β image">')
        self.assertIn('/wp-content/uploads/image-300x200.png 300w', markdown)
        self.assertIn('sizes="(max-width: 900px) 100vw, 900px"', markdown)
        self.assertIn('loading="lazy"', markdown)
        self.assertIn('width="900"', markdown)
        self.assertIn('alt="β image"', markdown)
        self.assertEqual(set(assets), {'image.png', 'image-300x200.png'})
        self.assertFalse(issues)

    def test_full_navigation_and_search_models_exclude_private_content(self):
        private = copy.deepcopy(self.record)
        private.update(id='2', status='private', eligible=False, title='PRIVATE TITLE', html='PRIVATE BODY')
        config = dict(source={'site_url': self.site_url}, selection={'scope': 'all'})
        report = generate_site(config, self.paths, [self.record, private])
        data = (self.paths['site'] / 'data/site.json').read_text()
        self.assertNotIn('PRIVATE', data)
        self.assertEqual(len(json.loads(data)['posts']), 1)
        self.assertTrue((self.paths['site'] / 'content/_generated/search.md').exists())
        self.assertTrue(any('/2020/01/' == path for path in report['generated_routes']))

    def test_project_order_uses_wordpress_order_and_stable_ids(self):
        from migration_site import build_site_model
        records = []
        for ident, title, path, parent, order in [
            ('1', 'Projects', '/projects/', '0', '5'),
            ('2', 'Group B', '/projects/b/', '1', '0'),
            ('3', 'Group A', '/projects/a/', '1', '0'),
            ('4', 'Old projects', '/projects/old/', '1', '9999'),
        ]:
            records.append(dict(self.record, id=ident, title=title, url='http://example.test' + path,
                                post_type='page', post_parent=parent, menu_order=order))
        model, _, _ = build_site_model(records, {})
        self.assertEqual([r['title'] for r in model['projects']], ['Group B', 'Group A', 'Old projects'])

    def test_unsafe_taxonomy_route_is_refused_before_writing(self):
        self.record['taxonomies'] = [dict(domain='post_tag', slug='../private', name='Unsafe')]
        config = dict(source={'site_url': self.site_url}, selection={'scope': 'all'})
        with self.assertRaises(ValueError):
            generate_site(config, self.paths, [self.record])
        self.assertFalse(self.paths['site'].exists())

    def test_excerpt_links_survive_without_executable_markup(self):
        from bs4 import BeautifulSoup
        from migration_site import excerpt_markup
        markup = excerpt_markup(BeautifulSoup('<p onclick="bad()"><a href="http://example.test/example/">Read</a> '
            '<code>__get__</code><script>bad()</script></p>', 'html.parser'), 'http://example.test/example/')
        parsed = BeautifulSoup(markup, 'html.parser')
        self.assertEqual(parsed.a['href'], '/example/')
        self.assertEqual(parsed.code.get_text(), '__get__')
        self.assertNotIn('onclick', markup)
        self.assertNotIn('bad()', markup)

    def test_attachment_routes_respect_private_parents_and_reviewed_aliases(self):
        attachment = dict(self.record, id='2', post_type='attachment', status='inherit',
                          eligible=False, post_parent='1', url='http://example.test/example/image/',
                          attachment_url='http://example.test/wp-content/uploads/image.png')
        records = [self.record, attachment]
        mapped = attachment_routes(records, self.site_url, {'/old-image/': '/wp-content/uploads/image.png'})
        self.assertEqual(mapped['/old-image/'], '/wp-content/uploads/image.png')
        self.record['eligible'] = False
        self.assertEqual(attachment_routes(records, self.site_url), {})
        with self.assertRaises(ValueError):
            attachment_routes(records, self.site_url, {'/old-image/': '/wp-content/uploads/image.png'})

    def test_query_routes_keep_other_parameters_and_fragments(self):
        markdown, _, _, issues = self.render('<a href="http://example.test/?p=1&amp;view=full#part">link</a>')
        self.assertIn('href="/example/?view=full#part"', markdown)
        self.assertFalse(issues)

    @unittest.skipUnless(shutil.which('zola'), 'Zola unavailable')
    def test_highlighting_preserves_code_without_a_final_newline(self):
        from bs4 import BeautifulSoup
        payload = 'fn main() { let x = 1; }'
        self.wxr.write_text(WXR.replace('<p>Hello</p>', '<pre class="lang:rust">' + payload + '</pre>'))
        config = dict(source={'site_url': self.site_url}, selection={'scope': 'all'})
        generate_site(config, self.paths, normalize(self.wxr))
        result = subprocess.run(['zola', '--root', str(self.paths['site']), 'build'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        built = self.paths['site'] / 'public/example/index.html'
        code = BeautifulSoup(built.read_text(), 'html.parser').article.pre
        self.assertEqual(code.get_text(), payload)
        self.assertTrue(code.select('span[style*="color:"]'), 'Rust sample has no syntax colors')

    @unittest.skipUnless(shutil.which('zola'), 'Zola unavailable')
    def test_full_build_preserves_code_and_detects_bad_links_and_rendered_changes(self):
        body = ('<p>Unicode β and literal quotes.</p><h2 id="part">Part</h2>'
                '<ul><li>Text before marker<!--more--></li><li>Another item</li></ul>'
                '<p>Call <code>__get__</code> in <code>~/.local/share</code>.</p>'
                '<p><strong>Method <code>__init__</code></strong></p>'
                '<p>Multiline inline <code>a\n\n b</code></p>'
                '<img src="/wp-content/uploads/image.png">'
                '<a href="/example/#part">anchor</a>'
                '<pre class="lang:python">print("hello")\n</pre>'
                '<pre>plain\n</pre><pre>no final newline</pre>'
                '<pre>{{ value }} {% template %}\n</pre>'
                '<ol><li>Run<pre>one\n\n    indented\n</pre></li></ol>')
        self.wxr.write_text(WXR.replace('<p>Hello</p>', body))
        (self.paths['uploads'] / 'image.png').write_bytes(b'original image bytes')
        records = normalize(self.wxr)
        config = dict(source={'site_url': self.site_url}, selection={'scope': 'all'})
        generate_site(config, self.paths, records)
        self.assertIn('Build the full staging site before validation', validate(self.paths))
        result = subprocess.run(['zola', '--root', str(self.paths['site']), 'build'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(validate(self.paths), [])
        from xml.etree import ElementTree
        feed = ElementTree.parse(self.paths['site'] / 'public/rss.xml')
        self.assertEqual(len(feed.findall('channel/item')), 1)
        self.assertEqual(feed.findtext('channel/item/title'), 'Example & title')
        self.assertEqual(feed.findtext('channel/item/guid'), 'http://old.example.test/?p=1')
        self.assertEqual(feed.find('channel/item/guid').get('isPermaLink'), 'false')
        self.assertIn('<pre', feed.find('channel/item').findtext('{http://purl.org/rss/1.0/modules/content/}encoded'))
        sitemap = ElementTree.parse(self.paths['site'] / 'public/sitemap.xml')
        self.assertFalse(any('/feed/' in node.text for node in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')))
        target = self.paths['site'] / 'public/example/index.html'
        built = target.read_text()
        target.write_text(built.replace('href="/example/#part"', 'href="/example/#missing"'))
        self.assertTrue(any('Missing fragment' in x for x in validate(self.paths)))
        target.write_text(built.replace('no final newline', 'tampered code'))
        self.assertTrue(any('Rendered code differs' in x for x in validate(self.paths)))
        target.write_text(built)
        image = self.paths['site'] / 'public/wp-content/uploads/image.png'
        image.write_bytes(b'changed image')
        self.assertTrue(any('Built media differs' in x for x in validate(self.paths)))


if __name__ == '__main__':
    unittest.main()

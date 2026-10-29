#!/usr/bin/env python3
"""Create a draft post with an explicit public URL and colocated media directory."""
import argparse
from datetime import datetime, timezone
import json
import re
import tomllib

from site_content import ROOT, read_content


def create_post(slug, title, root=ROOT):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Use a lowercase, hyphenated article slug')
    directory = root / 'content/posts' / slug
    if directory.exists() or any(r['url'].endswith('/' + slug + '/') for r in read_content(root, drafts=True)):
        raise ValueError('An article already uses that directory or public URL')
    author = tomllib.loads((root / 'zola.toml').read_text()).get('author', 'ivan')
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    body = '\n'.join(['+++', 'title = ' + json.dumps(title, ensure_ascii=False),
                      'path = ' + json.dumps('/' + slug + '/'),
                      'date = ' + json.dumps(stamp), 'draft = true', '[extra]',
                      'kind = "post"', 'author = ' + json.dumps(author),
                      'categories = []', 'tags = []', '+++', '',
                      'Write the opening paragraph here.', '', '<!-- more -->', '',
                      'Continue the article here.', ''])
    directory.mkdir()
    path = directory / 'index.md'
    path.write_text(body, encoding='utf-8')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slug')
    parser.add_argument('--title', required=True)
    args = parser.parse_args()
    try:
        print(create_post(args.slug, args.title))
    except ValueError as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()

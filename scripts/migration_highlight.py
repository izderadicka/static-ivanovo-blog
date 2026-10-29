"""Highlight HTML fallback code without changing its payload."""
import html
import re

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


def highlighted_html(payload, language='', compact=False):
    if language and language != 'text':
        alias = {'apache': 'apacheconf', 'sh': 'bash'}.get(language, language)
        lexer = get_lexer_by_name(alias, stripnl=False, stripall=False, ensurenl=False, tabsize=0)
        markup = highlight(payload, lexer, HtmlFormatter(nowrap=True, style='friendly'))
        if not payload.endswith('\n'):
            markup = markup.removesuffix('\n')
    else:
        markup = html.escape(payload, quote=False)
    # Braces are literal code, never Zola shortcodes, even in nested HTML.
    markup = markup.replace('{', '&#123;')
    lines = markup.splitlines(keepends=True)
    markup = ''.join('<span class="code-line">' + line.removesuffix('\n') + '</span>'
                     + ('\n' if line.endswith('\n') else '') for line in lines)
    if compact:
        markup = markup.replace('\n', '&#10;')
    return ('<pre class="code-highlight" data-language="' + html.escape(language, quote=True)
            + '"><code>' + markup + '</code></pre>')

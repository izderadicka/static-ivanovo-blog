+++
title = "unistego"
path = "/projects/python/unistego/"
date = "2014-01-21T15:48:23"
include_in_feeds = false
[extra]
wordpress_id = 737
kind = "page"
node_key = "737"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/unistego/"
source_guid = "http://zderadicka.eu/?page_id=737"
source_date_gmt = "2014-01-21 14:48:23"
menu_order = 0
parent = "/projects/python/"
+++
unistego is a small library  that supports digital [steganography](http://en.wikipedia.org/wiki/Steganography) in text messages,  hiding secret message into innocent looking text.   This is achieved by using special [Unicode](http://www.unicode.org/standard/WhatIsUnicode.html) characters, which are not normally displayed or look same as another character (homoglyphs).    Key focus of unistego is to provide such mechanism, that'll be resistant to text conversion to great extent. My initial idea was to have some way how to hide message into e-books. Some tests have shown that both strategies mentioned below kept secret message through transformation beween txt, html,  epub, mobi ,fb2  (tested as transformation of e-books in [Calibre](http://calibre-ebook.com/) ebooks manager).

unistego provides (as per now) two strategies (algorithms) to hide information into unicode text:



- "joiners'  -   uses unicode characters 'ZERO WIDTH JOINER' and 'ZERO WIDTH NON_JOINER'   in text - these characters have some meaning only in few alphabets,   in Latin and similar alphabets  these characters are not displayed.   To provide good immunity against transformation of text these characters are used only inside words.
- 'spaces' -  uses unicode characters 'FOUR-PER-EM SPACE' and 'THREE-PER-EM SPACE'  as alternatives to regular 'SPACE' character.    Strategy  uses either 'SPACE' or 'FOUR-PER-EM SPACE'  as spaces between two words ('THREE-PER-EM SPACE' is used as a terminal symbol).



In both cases such Unicode characters were chosen, which are not recognizable in most of common text tools (browsers, text editors,  word processor ...).   Also support for HTML text is provided -  HTML is parsed and extra Unicode characters are inserted only in text, not in markup.  So hidden message can survive transformation from HTML to regular text.

As an option secret message can be compressed (using zlib)  before inclusion into carrier text.

unistego is primarily a library - it has two level of APIs -   high level, described in [README](https://github.com/izderadicka/unistego/blob/master/README.md),   for lower level  API you must go to source for now.

Also there is a simple unistego-tool - command line tool (use unistego-tool  -h  to get help onn options.)


## Download & Install


Source code is available[ on github](https://github.com/izderadicka/unistego).

You can install using pip installer:

`pip install [-e] git+https://github.com/izderadicka/unistego#egg=unistego`

(use -e option to install for editing)

+++
title = "Removing Diacritics Marks from Strings"
path = "/removing-diacritics-marks-from-strings/"
date = "2012-10-24T14:41:47"
include_in_feeds = true
[extra]
wordpress_id = 287
kind = "post"
node_key = "287"
author = "admin"
source_url = "http://zderadicka.eu/removing-diacritics-marks-from-strings/"
source_guid = "http://zderadicka.eu/?p=287"
source_date_gmt = "2012-10-24 13:41:47"
[taxonomies]
category = ["Programming"]
tag = ["diacritics", "python", "unicode"]
+++
Many Latin alphabets (like my native Czech) contain characters with diacritical marks (or can be called accent marks). For some application in computers (like searching, cross systems compatible file names etc.) we would like to remove diacritics and translate  to string containing just ASCII  characters.   Common approach for this is to use **UNICODE character decomposition**.

It utilizes fact, that unicode has two ways how to represent characters with diacritics - for instance character **á** (LATIN SMALL LETTER A WITH ACUTE) normaly has code 225,  but this character can be decomposed into two unicode characters   code 97 (LATIN SMALL LETTER A) and character code 769 (COMBINING ACUTE ACCENT).   This process will work for majority of common 'special' Latin characters, however there are still few left, for which unicode does not have decomposition defined - these include characters like **ø**  (LATIN SMALL LETTER O WITH STROKE)  used in Norwegian language or **ł** (LATIN SMALL LETTER L WITH STROKE) used in Polish language.  A special handling is needed for these characters - basically a transcription table to map these into some basic Latin characters (it could be 1 to many mapping - for instance æ (LATIN SMALL LETTER AE) should map to 'ae').

Characters decomposition is defined in unicode standard and all common computer languages contains libraries which contain unicode definitions and can decompose characters.  Below Ishow how this can be done in python.<span id="more-287"></span>

Python contains module **unicodedata**, which holds all key information from unicode standard. This module can be used to get metadata about individual characters - like name, category,   to decompose a character or to normalize whole unicode string.

For our solution we first need to define mapping (transcription) of non-decomposable characters to basic Latin characters (ASCII characters with code \<128):


```python
nd_charmap = {
        u'\N{Latin capital letter AE}': 'AE',
        u'\N{Latin small letter ae}': 'ae',
        u'\N{Latin capital letter Eth}': 'D', #
        u'\N{Latin small letter eth}': 'd', #
        u'\N{Latin capital letter O with stroke}': 'O', #
        u'\N{Latin small letter o with stroke}': 'o',  #
        u'\N{Latin capital letter Thorn}': 'Th',
        u'\N{Latin small letter thorn}': 'th',
        u'\N{Latin small letter sharp s}': 's',#
        u'\N{Latin capital letter D with stroke}': 'D',#
        u'\N{Latin small letter d with stroke}': 'd',#
        u'\N{Latin capital letter H with stroke}': 'H',
        u'\N{Latin small letter h with stroke}': 'h',
        u'\N{Latin small letter dotless i}': 'i',
        u'\N{Latin small letter kra}': 'k',#
        u'\N{Latin capital letter L with stroke}': 'L',
        u'\N{Latin small letter l with stroke}': 'l',
        u'\N{Latin capital letter Eng}': 'N', #
        u'\N{Latin small letter eng}': 'n', #
        u'\N{Latin capital ligature OE}': 'Oe',
        u'\N{Latin small ligature oe}': 'oe',
        u'\N{Latin capital letter T with stroke}': 'T', #
        u'\N{Latin small letter t with stroke}': 't',#
```


This map contains only most common characters - there is much more of similar characters in the unicode standard. The key quetion is how to map these characters - I prefer mapping based on look of the character (glyphs), which I think is more natural for people, who do not know that language (rather then more official transcriptions, which are base more on actual pronunciation of the character  (ø -\> oe, but people outside Norway will probably never figure it out)).

With this mapping we can write this function to remove diacritics:


```python
def remove_dia(text):
    "Removes diacritics from the string"
    if not text:
        return text
    uni = None
    if isinstance(text, unicode):
        uni = text
    else :
        encoding=sys.getfilesystemencoding()
        uni =unicode(text, encoding, 'ignore')
    s = unicodedata.normalize('NFKD', uni)
    b=[]
    for ch in s:
        if  unicodedata.category(ch)!= 'Mn':
            if nd_charmap.has_key(ch):
                b.append(nd_charmap[ch])
            elif ord(ch)<128:
                b.append(ch)
            else:
                b.append(' ')
    return ''.join(b)
```


The key trick in this function is to normalize string to NFKD form (line  11), when all characters that have some decomposition are decomposed. Then we iterate over normalized string and leave out all characters with category Mn - 'Mark, Nonspacing', that is category, where all combining diacritical marks resides (line 14).   Then for non-composed characters we check if we have special mapping and  replace all remaining non-ascii characters with space.

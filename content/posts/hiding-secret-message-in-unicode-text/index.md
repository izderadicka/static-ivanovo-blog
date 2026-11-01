+++
title = "Hiding Secret Message in Unicode Text "
path = "/hiding-secret-message-in-unicode-text/"
date = "2014-01-23T11:55:31"
include_in_feeds = true
[extra]
wordpress_id = 741
kind = "post"
node_key = "741"
author = "admin"
source_url = "http://zderadicka.eu/hiding-secret-message-in-unicode-text/"
source_guid = "http://zderadicka.eu/?p=741"
source_date_gmt = "2014-01-23 10:55:31"
[taxonomies]
category = ["Programming", "Security"]
tag = ["python", "security", "Steganography"]
+++
An art of hiding secret message into another innocent looking message is called [steganography](http://en.wikipedia.org/wiki/Steganography) and it is an old discipline, where techniques like invisible ink, micro dots have been used.   With rise of digital technologies new possibilities for stenography  appeared and attracted interest of computer scientists and fans.     Common approach is to hide secret information into multimedia files - pictures,  music,  videos ....  Main advantages here are omnipresence of media today,  significant size of media file,   so there is enough space for additional information and the nature of the media format, which often enables to hide information in very clever way( if you change last bit of color information for a pixel in an image it is unidentifiable  by human eye).   But we can also hide secret messages in regular text, especially if we are using Unicode text encoding (which is now very common).

<span id="more-741"></span>

I was attracted to  stenography   through reading about [digital watermarks](http://en.wikipedia.org/wiki/Digital_watermark) in e-books.  Digital watermarks are short hidden messages,   that are used to identify source of the data in which they are hidden.   In e-books for instance it is used to identify, where e-book was purchased  (watermark consists of identification of merchant plus unique identification of transaction, in which e-book was bought).   Such watermarks are supposed to help in investigation of cases of digital piracy.    I was wondering how such  watermarks could be resilient to e-books conversion.   Can they survive conversions between several formats ideally even to such simple format as plain text ?

Looking bit around I found that there already exist some approaches, mainly using Unicode.  These methods can be categorized into following categories:


<ul>
<li>**Using **<a href="http://en.wikipedia.org/wiki/Homoglyph">**homoglyphs**
</a>Homoglyphs in Unicode are characters, which look (almost) identical, but have different code.   It is achieved by mixing character from Latin alphabet with   characters from Greek or Cyrillic alphabets.  Message is encoded as presence of either regular Latin character or its homoglyph (something like this - normal character = bit 0,  alternative homoglyph bit 1).  Nice example of such approach [is here (on-line javascript implementation)](http://www.irongeek.com/i.php?page=security/unicode-steganography-homoglyph-encoder).   Success of this approach depends mainly on fonts used to display carrier message.  While the message can look completely innocent in one font,   in another font it looks weird (as per picture below , which shows text with hidden message constructed with  above mentioned tool and displayed in 'Courier 10 Pitch' font), because that font can miss particular characters or they look different from normal characters:
<a href="/wp-content/uploads/text.png"><img alt="text" class="alignnone size-full wp-image-744" decoding="async" height="37" loading="eager" sizes="(max-width: 811px) 100vw, 811px" src="/wp-content/uploads/text.png" srcset="/wp-content/uploads/text.png 811w, /wp-content/uploads/text-300x13.png 300w" width="811"/></a></li>
<li>**Using unprintable,  zero-width  characters**
Unicode contains certain characters, that are not displayed like ZERO WIDTH SPACE, ZERO WIDTH NON-JOINER, ZERO WIDTH JOINER, WORD JOINER.   These characters can be inserted into unicode text to hide some information there.</li>
<li><strong>Using spaces and tabs at end of lines, paragraphs, empty lines
</strong>Adding or omitting space character at the end of line/paragraph  can be used to encode some information into a text.   This is particularly stealthy method,  because in normal text  you can often see some spaces at the  end of paragraphs, so it can look quite innocent even at closer look, but such formating is very fragile and will not survive conversions.  Java implementation for this method can be found at [Snow homepage](http://www.darkside.com.au/snow/index.html).</li>
</ul>


As I noted previously I was particularly interested to find how secret message can survive transformation of the text - for this purpose I created small python library <a href="/projects/python/unistego/" title="unistego">unistego</a>,   which supports either plain text or html text and provides two simple methods - called strategies (first method is using zero width joiner and non-joiner,   second is using alternative homoglyph space character).   These methods were designed by two main criteria :



1. Rendering of text with hidden message
Viewing text with hidden message  in most common tools  should not differ from viewing original clean text.   I've tested in several tools (browser, e-book reader,  text editors).  From all these only LibreOffice/OpenOffice Writer has been able to show some hidden characters (  zero width space and zero width joiners were displayed as special gray editing marks).
1. Persistence of characters during transformation



For testing transformation I used [Calibre](http://calibre-ebook.com/) e-book management software.   Here I was able to retain secret message in the e-book during  conversions between following formats:

TXT -\> EPUB -\> MOBI -\> FB2 -\> TXT
HTML  -\> EPUB -\> MOBI -\> FB2 -\> TXT

PDF format showed as more problematic -   for no strategy secret message survived conversion to and from PDF (joiners were replaces by zero width space,  not sure what exactly happened to alternative spaces, but it did not work either).   But I believe that some other strategy, carefully designed with PDF in mind, can survive transformation to and from PDF format.

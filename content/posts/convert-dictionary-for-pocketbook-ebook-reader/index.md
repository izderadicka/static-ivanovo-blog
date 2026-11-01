+++
title = "Convert Dictionary for PocketBook eBook Reader"
path = "/convert-dictionary-for-pocketbook-ebook-reader/"
date = "2014-05-02T16:41:04"
include_in_feeds = true
[extra]
wordpress_id = 796
kind = "post"
node_key = "796"
author = "admin"
source_url = "http://zderadicka.eu/convert-dictionary-for-pocketbook-ebook-reader/"
source_guid = "http://zderadicka.eu/?p=796"
source_date_gmt = "2014-05-02 15:41:04"
[taxonomies]
category = ["Tools"]
tag = ["ebooks"]
+++
I'm great fan of ebooks and recently I changed my old Hanlin to new reader - PocketBook 626.   [PocketBook](http://www.pocketbook-int.com) is an European company, which is distributing  PocketBook readers, the actual development of devices is done by Ukrainian company [Obreey Products](http://obreey-products.com/en/). Ukrainian and Russian programmers have been always very active in ebooks technology ([FB2](http://en.wikipedia.org/wiki/FictionBook) format,  [CoolReader](http://coolreader.org/e-index.htm),  [FBReader](http://fbreader.org/), [OpenInkPot](http://morgue.openinkpot.org/) (opensource FW for ebook) and more), so no wonder they have been able to produce quite a nice device.   I personally do prefer it to Kindle   because of wider format support (especially for support of [epub](http://en.wikipedia.org/wiki/EPUB) format) and for broader possibilities how to customize the device  (price wise they are basically similar to Kindle).

One of first tasks was to get there more useful language dictionaries (there are some built in, but can get better ones). Many high quality free dictionaries are available in [stardict](http://www.stardict.org/) format (for instance [here](http://cs.cihar.com/software/slovnik/) for Czech language dictionaries;  other [sites](http://dicts.info/uddl.php) are available, which offer also other formats of dictionaries).<span id="more-796"></span>

Actually it's quite big mess in dictionary formats out there.  There are many private formats (actually each ebook vendor tends to use its own format) and few (if any) public standards.  Already mentioned stardict was fairly popular private format (however stardict application is abandoned, you can use it successor [Goldendict](http://goldendict.org), which supports stardict format). Stardict dictionary is usually composed of 3 files .ifo, .dict (or dict.dz - compressed definition) and .idx. (if .ifo is missing it can be easily [recreated](http://www.mobileread.com/forums/showthread.php?p=2797244) \- it's text file).

One of standard formats is [XDXF](https://sourceforge.net/projects/xdxf/), which is basically XML with terms/keys and definitions. XDXF site also contains many dictionaries in this format. Here is a small sample of one entry in XDXF file  (text can contain some basic html formating - like bold, italics ...):


```html
<ar><k>Example</k>
(n.) One or a portion taken to show the character or quality of the whole; a sample; a specimen.</ar>
```


Detailed description of the XDXF format is [here](https://github.com/soshial/xdxf_makedict/blob/master/format_standard/xdxf_description.md).

In order to work efficiently dictionaries usually need two data structures -   terms definitions (like one above) and indexes - which enables to quickly find right definition ( I guess most implementations use some kind of binary tree to search efficiently). It depends on particular format how these two are represented ( stardict has definitions in .dict   file, index in .idx file).  Definitions are usually compressed somehow to save space (stardict uses dictzip).

You cannot rely only file extensions to determine dictionary format - it can be deceiving ( for instance Bookeen is also using .dict and .idx - but format is different - .idx is actually sqlite3 database). To be sure look into files with hexadecimal editor/viewer.

PocketBook uses custom format dictionary format, to which we must convert required dictionary, before uploading it to the device. It has extension .dic and combines definitions and index in one file.    The only tool that can convert to this format is private PocketBook's tool called DictionaryConverter ( links are below), which runs only on windows ( or under wine on Linux). It needs XDXF dictionary as an input and produces .dic file.

In order to get XDXF dictionary from existing dictionaries, we might need some other tool/converter, here are few I've tried:



- [linguae tool](http://linguae.stalikez.info/dwnld.php) - GUI tool written in python, worked well for me to convert from startdict format to XDXF. Site is in French, but tool has English interface too.
- [makedict](https://github.com/soshial/xdxf_makedict) - command like tool - official converter to XDXF format, written in C (so you might need to compile it locally).  However for me previous tool worked better - see below.
- [pyglossary](https://sourceforge.net/projects/pyglossary/) -  GUI tool written in python, cannot convert to XDXF (but can from XDXF), however can convert between many formats.
- [penelope](https://github.com/pettarin/penelope) - command line tool written in python, useful for converting Bookeen or Kobe dictionaries ( cannot convert to XDXF, but can convert to stardict, which can be used as intermediary format). Requires [dictzip](http://linuxcommand.org/man_pages/dictzip1.html).



So general approach for PocketBook dictionary is - get required dictionary in some format (ideally in XDXF), if not XDXF use some tool to convert to this format. Use DictionaryConverter tool to convert to .dic and copy this file to your PocketBook. Here are detailed steps, which worked for me:


<ol>
<li>We first need to convert dictionary into [XDXF format](http://xdxf.sourceforge.net/) (XML format for dictionaries exchange). I used  [linguae tool](http://linguae.stalikez.info/dwnld.php),   a GUI tool in python, working fine in Linux ( I also tried makedict tool, but it did not work well, because it does not support sametypesequence=**g** format of entries in dictionary - have to be m and then the formating was ugly).
One small note to stardict format -   it may have compress dict file (.dict.dz) - some conversion tools do not support it - uncompress with dictzip or just rename it to .dict.gz and then ungzip.</li>
<li>Get PocketBook [DictionaryConverter (newer version)](http://www.mobileread.com/forums/attachment.php?attachmentid=42342&d=1262456131) or [DictionaryConverter](http://www.mobileread.com/forums/attachment.php?attachmentid=40885&d=1260265451) (older version I used originally)  (or here [DictionaryConverter](/wp-content/uploads/DictionaryConverter.zip) with cs language definition)</li>
<li>In Dictionary converter you might need additional definitions of "from" language"  -  English, German, Russian (and Czech in the third file) are already available. For other language: copy en directory to other directory, rename it to appropriate language code ( cz, es ... two letters language code). Edit 3 files there (if necessary) :
<code>collates.txt</code> -   the collation (order of search/results) - defines all characters that are considered equal for ordering (can keep english as default for Latin alphabets)
<code>keyboard.txt</code> -  I think it's not used for new firmware (you can switch to predefined national keyboard) - so just leave it as it is.
<code>morphems.txt</code> - it's used to define same words in different forms,  If you used English base edit it(leave first two rows defining  consonants and vowels, eventually modify for your language, but it is not essential ), or  you can leave it empty if you do not know how to use it.</li>
<li>Run<code> wine converter.exe &lt;path&#95;to&#95;&#95;dict.xdxf&gt; &lt;lang&#95;code&gt;&#10;wine</code> - Windows emulator - use only in linux, in Win you can run directly
then path to <code>dict.xdxf:</code> dictionary created in previous step (e.g. "../czech-cizi/dict.xdxf")
<code>lang&#95;code</code> -  language code (name of dictionary with language definition -   e.g. cs )
The program is quite particular about well formed XML input - it crashes if file is ill formatted - look for program messages, fix XML and try again.</li>
<li>Copy resulting <code>.dic</code> file (will be in same folder as dict.xdxf) to PocketBook - <code>system/dictionaries</code> folder (in Windows you might need to change File Explorer settings to see <code>system</code> folder - View tab / Options/ View tab / Advanced Settings - uncheck Hide protected operating system file)</li>
</ol>


As sample here is [Czech Foreign Words dictionary (Slovnik Cizich Slov)](http://uloz.to/xaxsh4Dx/czech-cizi-dic), or [Spanish dictionary](http://www.ulozto.net/xXx48FBQ/es-es-dic), both created by this process.

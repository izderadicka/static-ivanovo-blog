+++
title = "Parsing PDF for Fun And Profit (indeed in Python)"
path = "/parsing-pdf-for-fun-and-profit-indeed-in-python/"
date = "2016-02-27T08:52:49"
include_in_feeds = true
[extra]
wordpress_id = 1251
kind = "post"
node_key = "1251"
author = "admin"
source_url = "http://zderadicka.eu/parsing-pdf-for-fun-and-profit-indeed-in-python/"
source_guid = "http://zderadicka.eu/?p=1251"
source_date_gmt = "2016-02-27 07:52:49"
[taxonomies]
category = ["Programming"]
tag = ["PDF", "python"]
+++
PDF documents are ubiquitous in today's world. Apart of common use cases of printing, viewing etc. we need sometimes do something specific with them- like convert tehm to other formats or extract textual content.  Extracting text from PDF document can be (surprisingly) hard task due to the purpose and design of PDF documents.  PDF is intended to represent exact visual representation of document 's pages down to the smallest details. And internal representation of document text is following this goal.  Rather the storing text in some logical units (lines, paragraphs, columns, tables ...), text is represented as series of commands, which print characters (can be a single character, word, part of line, ...) at exact position on the page with given font, font size, color, etc.   In order to reconstruct original text logical structure program  has to scan  all these commands and join together texts, which were probably forming same line or same paragraph.  This task can be pretty demanding and ambiguous -  mutual position of text boxes can be interpreted in various ways ( is this space between words too large because they are in different columns or line is justified to both ends?).

So the task of text extraction looks quite discouraging to try, luckily some smart guys have tried it already and left us with libraries that are doing pretty good job and we can leverage them. Some time ago I've created tool called[ PDF Checker](/projects/python/pdf-checker/), which does some analysis of PDF document content (presence, absence of some phrases,  paragraphs numbering, footers format etc.). I used there excellent Python [PDFMiner](http://www.unixuser.org/~euske/python/pdfminer/) library.   PDFMiner is a grea tool and it is quite flexible, but being all written in Python it's rather slow.   Recently I've been looking for some alternatives,  which have Python bindings and provide functionality similar to PDFMiner.  In this article I describe some results of this search, particularly my experiences with [libpoppler](https://poppler.freedesktop.org/). <span id="more-1251"></span>


## Requirements


In order to analyze  in detail text of PDF document I require to:



- get number of pages in PDF document and for each page its size
- extract text from the page, ideally grouped to lines and paragraphs (boxes)
- get bounding boxes of text items (down to individual characters) to analyze text based on it's position on the page - header/footer, indentation, columns etc.
- get font name, size and color, background color  - to identify headers, highlights etc.





## PDFMiner library


[PDFMiner](http://www.unixuser.org/~euske/python/pdfminer/) library was my first attempt, so generally most of requirements are derived from its interface.  The only things which are really missing there are font and background colours.  Here is an example how to dump text content of PDF file together with its position on the page and format:


```python
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox,LTChar, LTFigure
import sys

class PdfMinerWrapper(object):
    """
    Usage:
    with PdfMinerWrapper('2009t.pdf') as doc:
        for page in doc:
           #do something with the page
    """
    def __init__(self, pdf_doc, pdf_pwd=""):
        self.pdf_doc = pdf_doc
        self.pdf_pwd = pdf_pwd

    def __enter__(self):
        #open the pdf file
        self.fp = open(self.pdf_doc, 'rb')
        # create a parser object associated with the file object
        parser = PDFParser(self.fp)
        # create a PDFDocument object that stores the document structure
        doc = PDFDocument(parser, password=self.pdf_pwd)
        # connect the parser and document objects
        parser.set_document(doc)
        self.doc=doc
        return self
    
    def _parse_pages(self):
        rsrcmgr = PDFResourceManager()
        laparams = LAParams(char_margin=3.5, all_texts = True)
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
    
        for page in PDFPage.create_pages(self.doc):
            interpreter.process_page(page)
            # receive the LTPage object for this page
            layout = device.get_result()
            # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
            yield layout
    def __iter__(self): 
        return iter(self._parse_pages())
    
    def __exit__(self, _type, value, traceback):
        self.fp.close()
            
def main():
    with PdfMinerWrapper(sys.argv[1]) as doc:
        for page in doc:     
            print 'Page no.', page.pageid, 'Size',  (page.height, page.width)      
            for tbox in page:
                if not isinstance(tbox, LTTextBox):
                    continue
                print ' '*1, 'Block', 'bbox=(%0.2f, %0.2f, %0.2f, %0.2f)'% tbox.bbox
                for obj in tbox:
                    print ' '*2, obj.get_text().encode('UTF-8')[:-1], '(%0.2f, %0.2f, %0.2f, %0.2f)'% tbox.bbox
                    for c in obj:
                        if not isinstance(c, LTChar):
                            continue
                        print c.get_text().encode('UTF-8'), '(%0.2f, %0.2f, %0.2f, %0.2f)'% c.bbox, c.fontname, c.size,
                    print
                    
                

if __name__=='__main__':
    main()
```


As you can see with a very simple wrapper class around PDFMiner  library we can easily iterate PDF document text down to individual characters, each level provides exact position information, lowest level provides also font information.

PDFMiner is very flexible, you can set few parameters to control layout analysis and thus fine tune text parsing to your need. But as already said PDFMiner is quite slow, does not provide font colour information and also does not support python 3.


##  libpoppler with GObject Introspection interface


[Poppler](https://poppler.freedesktop.org/) is a PDF rendering and parsing library based on the [xpdf-3.0](http://www.foolabs.com/xpdf/) code base. It's now hosted as part of freedesktop.org and is actively maintained. libpoppler is used in many opensource PDF tools (Evince, Okular, GIMP, ...) and provides rich functionality for both parsing and rendering.

Poppler package  contains [GObject Introspection](https://wiki.gnome.org/action/show/Projects/GObjectIntrospection?action=show&redirect=GObjectIntrospection) binding, which means it can be used from scripting languages like Python or Javascript.  However there is [significant issue with introspection](https://bugs.freedesktop.org/show_bug.cgi?id=77790) for one function, which is used for getting positions of text on the page - so workaround has to be used in this area.

Below is code that dumps PDF text in a similar way to script with PDFMiner:


```python
from gi.repository import Poppler, GLib
import ctypes
import sys
import os.path
lib_poppler = ctypes.cdll.LoadLibrary("libpoppler-glib.so.8")

ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p
ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]
PyCapsule_GetPointer = ctypes.pythonapi.PyCapsule_GetPointer

class Poppler_Rectangle(ctypes.Structure):
    _fields_ = [ ("x1", ctypes.c_double), ("y1", ctypes.c_double), ("x2", ctypes.c_double), ("y2", ctypes.c_double) ]
LP_Poppler_Rectangle = ctypes.POINTER(Poppler_Rectangle)
poppler_page_get_text_layout = ctypes.CFUNCTYPE(ctypes.c_int, 
                                                ctypes.c_void_p, 
                                                ctypes.POINTER(LP_Poppler_Rectangle), 
                                                ctypes.POINTER(ctypes.c_uint)
                                                )(lib_poppler.poppler_page_get_text_layout)

def get_page_layout(page):
    assert isinstance(page, Poppler.Page)
    capsule = page.__gpointer__
    page_addr = PyCapsule_GetPointer(capsule, None)
    rectangles = LP_Poppler_Rectangle()
    n_rectangles = ctypes.c_uint(0)
    has_text = poppler_page_get_text_layout(page_addr, ctypes.byref(rectangles), ctypes.byref(n_rectangles))
    try:
        result = []
        if has_text:
            assert n_rectangles.value > 0, "n_rectangles.value > 0: {}".format(n_rectangles.value)
            assert rectangles, "rectangles: {}".format(rectangles)
            for i in range(n_rectangles.value):
                r = rectangles[i]
                result.append((r.x1, r.y1, r.x2, r.y2))
        return result
    finally:
        if rectangles:
            GLib.free(ctypes.addressof(rectangles.contents))

def main():
    
    print 'Version:', Poppler.get_version()
    path=sys.argv[1]
    if not os.path.isabs(path):
        path=os.path.join(os.getcwd(), path)
    d=Poppler.Document.new_from_file('file:'+path)
    n=d.get_n_pages()
    for pg_no in range(n):
        p=d.get_page(pg_no)
        print 'Page %d' % (pg_no+1), 'size ', p.get_size()
        text=p.get_text().decode('UTF-8')
        locs=get_page_layout(p)
        fonts=p.get_text_attributes()
        offset=0
        cfont=0
        for line in text.splitlines(True):
            print ' ', line.encode('UTF-8'),
            n=len(line)
            for i in range(n):
                if line[i]==u'\n':
                    continue
                font=fonts[cfont]
                while font.start_index > i+offset or font.end_index < i+offset:
                    cfont+=1
                    if cfont>= len(fonts):
                        font=None
                        break
                    font=fonts[cfont]
                
                bb=locs[offset+i]
                print line[i].encode('UTF-8'), '(%0.2f, %0.2f, %0.2f, %0.2f)' % bb,
                if font:
                    print font.font_name, font.font_size, 'r=%d g=%d, b=%d'%(font.color.red, font.color.green, font.color.blue),
            offset+=n
            print       
        print
        #p.free_text_attributes(fonts)

if __name__=='__main__':
    main()
```


Comparing to PDFMiner solution it doesn't provide aggregation on text box or text line level - lines should be reconstructed from page text.  But it provides color (but not background colour) of the font for individual characters.


## libpoppler with custom Python binding


Recently I've learned more about [Cython ](http://cython.org/)so I decided to give it a try and create [my own interface](https://github.com/izderadicka/pdfparser) to libpoppler. Actually it was not so difficult and quite quickly I was able to create  Python binding, which I can use easily as the replacement for PDFminer in my project.   The most notable difference is reversed orientation of y-axis ( PDFminer has 0 at page bottom, here it is at page top).  Below is the sample code for dumping PDF text (with position and font information):


```python
import pdfparser.poppler as pdf
import sys

d=pdf.Document(sys.argv[1])

print 'No of pages', d.no_of_pages
for p in d:
    print 'Page', p.page_no, 'size =', p.size
    for f in p:
        print ' '*1,'Flow'
        for b in f:
            print ' '*2,'Block', 'bbox=', b.bbox.as_tuple()
            for l in b:
                print ' '*3, l.text.encode('UTF-8'), '(%0.2f, %0.2f, %0.2f, %0.2f)'% l.bbox.as_tuple()
                #assert l.char_fonts.comp_ratio < 1.0
                for i in range(len(l.text)):
                    print l.text[i].encode('UTF-8'), '(%0.2f, %0.2f, %0.2f, %0.2f)'% l.char_bboxes[i].as_tuple(),\
                        l.char_fonts[i].name, l.char_fonts[i].size, l.char_fonts[i].color,
                print
```


As you can clearly see the source code is the shortest, yet still provides all necessary data, including font colour (but not background colour).  Apart of being significantly faster ( see below for detailed benchmarks),  it seems to be more reliable then PDFMiner (it solved few issues where PDFminer behaved strangely).


## Benchmarks


I've done simple benchmarks of these three scripts, time is measured by time linux utility as mean of 3 runs (after initial run to exclude possible caching effects), output is directed to /dev/null to exclude terminal printing time. Benchmarks runs on my notebook with Ubuntu 14.04 64 bit, Core i5 CPU @ 2.70GHz and 16GB memory:


<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table cellpadding="4" cellspacing="0" width="100%"><colgroup> <col width="64*"/> <col width="64*"/> <col width="64*"/> <col width="64*"/> </colgroup>
<tbody>
<tr valign="top">
<td width="25%"></td>
<td width="25%">**libppopler with cython**</td>
<td width="25%">**libpoppler with GI binding**</td>
<td width="25%">**pdfminer**</td>
</tr>
<tr valign="top">
<td width="25%">tiny document (half page)</td>
<td width="25%">0.033s</td>
<td width="25%">0.098s</td>
<td width="25%">0.121s</td>
</tr>
<tr valign="top">
<td width="25%">small document (5 pages)</td>
<td width="25%">0.141s</td>
<td width="25%">0.499s</td>
<td width="25%">0.810s</td>
</tr>
<tr valign="top">
<td width="25%">medium document (55 pages)</td>
<td width="25%">1.166s</td>
<td width="25%">4.860s</td>
<td width="25%">10.524s</td>
</tr>
<tr valign="top">
<td width="25%">large document (436 pages)</td>
<td width="25%">10.581s</td>
<td width="25%">34.621s</td>
<td width="25%">108.095s</td>
</tr>
</tbody>
</table></div>


As you can see custom libpoppler binding with Cython is about 3x faster then GObject introspection interface and  10x times faster then PDFMiner (for large documents).


## Conclusions


Custom interface to libpoppler is the clear winner in all aspects - performance, code simplicity / pythonic interface and reliability.  I'll be using it in my further projects.

My Python libpoppler binding is [freely available on github](https://github.com/izderadicka/pdfparser) under GPL v3 license ( as libpoppler is GPL licensed too) and you are invited to try it.  I'd like to hear your feedback.

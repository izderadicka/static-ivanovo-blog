+++
title = "PDF Checker"
path = "/projects/python/pdf-checker/"
date = "2014-09-28T08:57:49"
include_in_feeds = false
[extra]
wordpress_id = 875
kind = "page"
node_key = "875"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/pdf-checker/"
source_guid = "http://zderadicka.eu/?page_id=875"
source_date_gmt = "2014-09-28 07:57:49"
menu_order = 0
parent = "/projects/python/"
+++
Organizations or teams producing manually many PDF documents might want to apply some quality checks before releasing documents.  PDF checker enables to apply some basic automatic  checks including searching for text presence (or lack of text), page numbering  check, headings/paragraphs numbering and much more.  Application is written in python and provides both CLI and web interface.


## How it works?


Application is using <a href="http://www.unixuser.org/~euske/python/pdfminer/">pdfminer</a> library to extract text from PDF documents -  text is separated to individual lines (as recognized by pdfminer, which actually reconstructs lines from characters position on page) and each line is also supplemented by page number, it's position on the page (top left point and bounding box of the line) and also some information about font used (name, variant, size).

Lines are then feed into checking algorithms (implemented as plugins),  which check for issues (like finding some unwanted word). Issues are collected and then displayed together with their position in the document.


## Features




<ul>
<li>User friendly web interface with integrated PDF viewer</li>
<li>One click error highlight - Click on the error and PDF viewer highlights it to you</li>
<li>CLI interface to use from scripts</li>
<li>Flexible -  new checks can be very easily added as plugins (see below)</li>
<li>Easy to deploy</li>
</ul>




## Screenshots




<div class="gallery" data-gallery="" id="metaslider_885"><figure><a href="/wp-content/uploads/upload.png"><img alt="" decoding="async" height="842" loading="eager" src="/wp-content/uploads/upload.png" width="1284"/></a><figcaption>Upload screen</figcaption></figure><figure><a href="/wp-content/uploads/erro1.png"><img alt="" decoding="async" height="842" loading="lazy" src="/wp-content/uploads/erro1.png" width="1284"/></a><figcaption>Highlighting  issue with TBD phrase </figcaption></figure><figure><a href="/wp-content/uploads/error2.png"><img alt="" decoding="async" height="842" loading="lazy" src="/wp-content/uploads/error2-1284x842.png" width="1284"/></a><figcaption>Highlighting incorrect sections numbering </figcaption></figure><figure><a href="/wp-content/uploads/error3.png"><img alt="" decoding="async" height="842" loading="lazy" src="/wp-content/uploads/error3-1282x841.png" width="1284"/></a><figcaption>Highlighting incorrect page numbering</figcaption></figure><figure><a href="/wp-content/uploads/cli.png"><img alt="" decoding="async" height="842" loading="lazy" src="/wp-content/uploads/cli.png" width="1284"/></a><figcaption>Command line interface</figcaption></figure></div>




## Writing Plugin


Implementing a new check is very easy.   Create new module in `plugins` directory - here sample dummy plugin (that looks for 'Dummy' word in document):


```python
import re
from common import CheckStrategy, Problem

class DummyCheck(CheckStrategy):
    name="Sample Dummy Check"
    help="Checks plugin tutorial"
    
    def __init__(self,):
        super(DummyCheck, self).__init__()
        
    def feed(self, line):
        for m in re.finditer('Dummy',line.text):
            bbox=line.get_bbox(m.start(), m.end())
            p=Problem('Found Dummy', line)
            p.bbox=bbox
            self.results.add_problem(p)

```


Plugin is a class extending `CheckStrategy` base class.  New plugin must have class property `name`, with unique name of your check. Optionally it can have `help` and `optional` properties.

If you are overwriting `__init__` method do not forget to call super's `__init__` .

Check is done by overriding `feed` method.  This method will receive a `line` of text as it is retrieved from PDF document.   Parameter `line` is of type `TextLine`, it has property `text`, which is string containing text of the line.  `TextLine` has other useful properties - like `page_no` (page number),  `top` and `left` ( relative position (in percent)  of line beginning ), `bbox` (bounding box of text line in page coordinates).   And some useful methods - like get\_bbox (which gets bounding box for a substring of the line) or size\_at or font\_at (which gets information about font size or font name for character at given index.)

If any problem is found, it should be added to `self.results` collection,  either via `add_problem` method (requiring `Problem` instance as an input)  or just `add` method (which takes description of problem and line as its parameters). If results cannot be calculated on the fly, you can collect some information within `feed` method  then and override `prepare_results method`, which is called at the end, when all document is processed.

That is all - check plugins are automatically loaded and used in the program.  However sometime you might need to initialize check with some parameters, before using it.   In this case you can supply function `create_instance` in plugin module code, which  provides appropriately initiated instance of your check:


```python
def create_instance():
    i= ExistingCheckClass('some init params')
    i.change_name('New Name')
    i.change_help('New help')
    return i
```


You can change name and help for this check, if reusing existing check with different parameters.


## Download and install


Code is available under <a href="http://www.gnu.org/copyleft/gpl.html">GPL v3 license</a>.

Code can be downloaded from <a href="https://github.com/izderadicka/pdf-checker">github</a>. You''l need to write your own checking plugins to make it useful - because included ones are quite specific for my case.

For installation instructions check <a href="https://github.com/izderadicka/pdf-checker/blob/master/README.md">README</a> file.

+++
title = "Downloader Python3"
path = "/projects/python/downloader-python3/"
date = "2012-09-23T11:43:23"
include_in_feeds = false
[extra]
wordpress_id = 94
kind = "page"
node_key = "94"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/downloader-python3/"
source_guid = "http://zderadicka.eu/?page_id=94"
source_date_gmt = "2012-09-23 10:43:23"
menu_order = 0
parent = "/projects/python/"
+++
<strong>Downloader</strong> is a small utility and framework intended for help download many files from a certain site in an unobtrusive manner. Written in Python 3 for Linux platform - requires some python programming skills to use.



<div class="tabset" data-tabs="" id="tabs_94_0">



<section class="tab-panel" id="tabs-94-0-0">



## Description



The program is build for this use case:
<em>One needs to download many files form a site. Files are referenced on site in a list or table, that is paginated ( hundreds of pages). Actual download links might be indirectly referred from that pages or even require some algorithm to be constructed.  The  downloading program should behave in an unobtrusive manner - do not overload the site and basically be undistinguishable from a regular user who is browsing site.</em>

The tool is basically a framework, which consist of a basic program, which provides key actions and plugins, which are specific for given site and which do parse site pages and provide links for files to be downloaded. Also tool is designed to be able to run a long time (weeks, months) and resume if it has been interrupted in meanwhile ( not actually resuming individual files now, but rather resume from the page when it was parsing links last time).

Interface of program is command line.

Basic flow of program:


<ol>
<li>Log into site</li>
<li>Download first page</li>
<li>Parse all relevant links on the page, plus their metadata ( e.g. relevant information related to link - name, author, date etc.)</li>
<li>Process the link - is any further browsing and parsing is needed to get final link and its metadata</li>
<li>Enqueue links and meta for download - downloads will then run in separate threads</li>
<li>Parse page for link to next page</li>
<li>Load next page and continue on 2.</li>
<li>End if there are no further pages</li>
</ol>




</section>




<section class="tab-panel" id="tabs-94-0-1">



## How To Use



Program is to be used from command line :


```
Usage: downloader.py plugin options directory_to_store

Options:
  -h, --help            show this help message and exit
  --proxy=PROXY         HTTP proxy to use, otherwise system wise setting will
  --no-proxy            Do not use proxy, even if set in system
  -r, --resume          Resumes form from last run - starts on last unfinished
                        page and restores queue of unfinished downloads
  -s STOP_AFTER, --stop-after=STOP_AFTER
                        Stop approximatelly after x minutes
  -d, --debug           Debug logging
  -l LOG, --log=LOG     Log file
```


Each plugin can have its own options.
Do not forget that it has to be run from python3,  to run with sample plug-in provided run this:


```
python3 downloader.py manybooks -d -r ~/tmp/manybooks
```




</section>




<section class="tab-panel" id="tabs-94-0-2">



## How To Write Plugin



To use downloader you need to write your own plugin for site you're interested in.  Skill needed:


<ul>
<li>Python 3</li>
<li>Knowledge of <a href="http://www.crummy.com/software/BeautifulSoup/bs4/doc/">BeautifulSoup HTML parsing library</a></li>
</ul>


There is a sample plugin for site manybooks so you can look at it.

General approach would be :


### 1\) Looks at the site of your interest


Look at the HTML code how it is structured - look where are links and what information around there you can use as metadata. The invaluable help when looking into HTML can be provided by <a href="https://getfirebug.com/">Firebug</a> Firefox plugin. Look how pagination is done and how to get a link to next page.

Download a page for offline testing with plugin ( HTML Only file - no need for related media).


### 2\) Write Plugin


In plugins directory create new file - use manybooks.py as a prototype.

Set correct urls to <strong>BASE_URL</strong> and <strong>START_URL</strong> and start with methods <strong>next_link</strong> and <strong>next_page_ur</strong>l - these are core of site parsing.  Use test cases - see below - to test your code.

If site requires login then implement <strong>require_login</strong> and <strong>login</strong> methods.

If you cannot get clear download link from initial pages implement method <strong>postprocess_link</strong>, where you can download and parse any intermediate page(s) and do any further processing to get final link and metadata. If for any reasons link should not be downloaded , this method can raise  <strong>raise SkipLink</strong> exception.

Then implement function <strong>save_file</strong>, which will save final link to disk - use client.save\_file method to load and save data. save\_file function has access to special parametrs context, which is worker object running this function.  If for any reasons function needs to wait for a while (download limits etc.) it should use context.sleeper.sleep(x) to sleep for x seconds.

Finally you can fine tune downloader parameters on<strong> lines 15-30</strong>, which will govern the HTTP requests behaviour - delay between requests and concurrency.

If you want control plugin behaviour from command line you can define its <strong>OPTIONS</strong> on line 42 and use then options global variable in code.

Here is complete sample plugin with comments:


```python
import logging
import re
import os.path
from httputils import LinksSpider
from optparse import Option


# Some basic constants for particular site
# client settings for links parsing
REPEATS=5 # how many times to retry after HTTP or connection error
MEAN_WAIT=6 # average time to wait before next request - in seconds
MAX_WAIT=18 # maximum time to wait - if random wait if greater it is reduced to this maximum

# clients settings for files downloading
# same meaning as above, but for files downloading
REPEATS2=5
MEAN_WAIT2=1
MAX_WAIT2=2

# maximum number of files links in queue, when reached parsing of new links
# blocks, until a link is downloaded and can push to queue again 
MAX_QUEUE_SIZE=50 #0 means unlimited
DOWN_THREADS=2 # number of threads for download tasks

#Base URL to use for relative links processing
BASE_URL = 'http://manybooks.net'
# URL to start with
START_URL='http://manybooks.net/language.php?code=en&s=1'

# Set by program - a directory where downloaded files should be stored
BASE_DIR=''

#command line options for this plugin
# available the from options variable as options.name
OPTIONS=[Option('--store_path', type='string', help='Template for path where file is stored. '+
                'following keys available {title} {author} {id}'),
        ]
options=None # will be filled with parsed options 

#Create MySpider class - to get all links form one page and also to get link to next page
class MySpider(LinksSpider):
    
    #Assure that you are logged into site and any cookies set
    # self.client is available HTTPClient to load any page needed
    def login(self):
        pg=self.client.load_page(BASE_URL)
        
    # Do we require to login
    # page - is parsed page as BeutifulSoup object
    # return true is yes
    def require_login(self, page):
        return not page.find('span', 'googlenav') is None
    
    # function to parse available links on a page
    # page - is parsed page as BeutifulSoup object
    # must be generator or return iterator returning (link, metadata) tuple       
    def next_link(self, page):
        table=page.find('div', 'table')
        if table:
            cells=table.find_all('div', 'grid_5')
            for cell in cells:
                try:
                    metadata={}
                    metadata['author']=str(list(cell.strings)[-1]).strip()
                    link=cell.find('a')
                    if link: 
                        metadata['title']=str(link.string).strip()
                        link_url=link['href']
                        m=re.match(r'/titles/(.*).html', link_url)
                        if m:
                            metadata['id']=m.group(1)
                        if not link_url:
                            continue
                    else:
                        continue
                    sub=cell.find('em')
                    if sub:
                        metadata['subtitle']=str(sub.string).strip()
                    # Is generator !
                    yield BASE_URL+link_url, metadata
                except:
                    logging.exception('error parsing book data')
                    continue
                    
       
    # Parse page to find URL for next page
    # page - is parsed page as BeutifulSoup object
    # returns url or false if there is no further page
    def next_page_url(self,page):
        try:
            pager=page.find('span', 'googlenav')
            current_page=pager.find('strong', recursive=False)
            next_url=current_page.find_next_sibling('a')
            
            if next_url and next_url.get('href'): 
                next_url=str(next_url['href'])
                # for testing can stop on page 5
                #if next_url and next_url.find('s=6')>=0: return
                logging.debug('Has next page %s' % next_url)
                return BASE_URL+next_url
        except:
            logging.exception('Error while parsing page for next page')
    
    # Postprocess links found on page and get final link and metadata
    # can get another page   via self.client and do some more parsing
    # or anything else needed
    # link, metadata is tuple returned by next_link    
    # must return (link, metadata) tuple 
    # if for any reason link should not be downloaded method should  raise SkipLink
    def postprocess_link(self, link, metadata):
        if not metadata.get( 'author'):
            metadata['author']='Unknown Author'
        if not metadata.get( 'title'):
            metadata['title']='Unknown Title'
        return link, metadata

       
def _meta_to_filename(base_dir,metadata, ext):
    templ="{author}/{title}/{author} - {title}[{id}]"
    if options.store_path:
        templ=options.store_path
    while templ.startswith(os.sep):
        templ=templ[1:]
    p=templ.format(**metadata) +ext
    return os.path.join(base_dir,p)

# function to save  file from found link
# client is   HTTPClient object to load and save file
# link is a link to file
# metadata is a dictionary of metadata as returned by MySpider.next_link
# base_dir is directory to save file
# context - get access to worker running this function 
#           context.sleeper.sleep - can be used to sleep for x seconds
def save_file(client,link, metadata, base_dir, context=None):
    filename=_meta_to_filename(base_dir, metadata, '.epub')
    data={'book':'1:epub:.epub:epub', 'tid': metadata['id']}
    client.save_file(BASE_URL+'/_scripts/send.php', filename, data,refer_url=link)
    meta=repr(metadata)
    with open(filename+'.meta', 'w') as f: 
        f.write(meta)  
    logging.debug('Saved file %s'% filename)
```




### 3\) Test plugin


Surely you will need some iterations to get working correctly.  There is some support within code for building test cases.

You can import <strong>httputils.TestSpider </strong>and use it as mixed-in class - thus you should be able to test MySpider class on files stored locally.

See below test code for sample plugin:


```python
import unittest
from plugins.manybooks import MySpider
import httputils

class TestSpider( httputils.TestSpider, MySpider):
    pass

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testLinks(self):
        spider=TestSpider('../../test_data/manybooks.html')
        links=list(spider)
        for l,m in links: print(l,m)
        self.assertEqual(len(links), 20)

    def testNextPageURL(self):
        spider=TestSpider('../../test_data/manybooks.html')
        url=spider.next_page_url(spider.page)

        self.assertEqual(url, 'http://manybooks.net/language.php?code=en&s=2')

        spider=TestSpider('../../test_data/manybooks5.html')
        url=spider.next_page_url(spider.page)

        self.assertTrue(url)
```


After offline test you can test your plugin from within downloader.  <strong>-d</strong> option will pring logging messages so be sure to use <strong>logging</strong> module to log all important things going on in your plugin.



</section>




<section class="tab-panel" id="tabs-94-0-3">



## Download



All code can be downloaded and forked from GitHub:


### <a href="https://github.com/izderadicka/downloader-py3">https://github.com/izderadicka/downloader-py3</a>


All code is provided under <a href="http://www.gnu.org/copyleft/gpl.html">GPL v3 license</a>.



</section>




</div>

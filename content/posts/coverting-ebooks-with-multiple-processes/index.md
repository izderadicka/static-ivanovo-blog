+++
title = "Coverting Ebooks with Multiple Processes "
path = "/coverting-ebooks-with-multiple-processes/"
date = "2012-10-24T15:09:28"
include_in_feeds = true
[extra]
wordpress_id = 304
kind = "post"
node_key = "304"
author = "admin"
source_url = "http://zderadicka.eu/coverting-ebooks-with-multiple-processes/"
source_guid = "http://zderadicka.eu/?p=304"
source_date_gmt = "2012-10-24 14:09:28"
categories = ["Programming"]
tags = ["ebook", "python"]
+++
Recently I've been converting a batch of ebooks into epub and mobi formats.  I used python tools, parts of my project <a href="/projects/python/mybookshelf-ebooks-library/" title="MyBookshelf – EBooks Library">MyBookShelf</a>, which uses calibre and LibreOffice for all the hard work.   The conversion tool enables to run several conversion in parallel - in separate processes.  I wondered how the conversion will speed up with adding more processes.   I ran it  on my notebook with core i5 processor - two physical cores, each core can run two physical threads, 8GB memory. Graph below shows results for conversion of about 10 books into both formats.

<a href="/wp-content/uploads/Untitled-1.png" rel="attachment wp-att-305"><img alt="" class="alignnone wp-image-305" decoding="async" height="252" loading="eager" sizes="(max-width: 504px) 100vw, 504px" src="/wp-content/uploads/Untitled-1.png" srcset="/wp-content/uploads/Untitled-1.png 504w, /wp-content/uploads/Untitled-1-300x150.png 300w" title="Untitled 1" width="504"/></a>

Interesting thing for me is that only notable speed up is between 1 and 2 processes.   Not very much gain with running 3 or 4 -  looks like full utilization of HW threads is held back by I/O or memory speed limits?

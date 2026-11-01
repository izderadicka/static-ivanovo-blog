+++
title = "MyBookshelf2 - Ebooks Management and Sharing"
path = "/projects/python/mybookshelf2-ebooks-management-and-sharing/"
date = "2016-10-03T09:24:17"
include_in_feeds = false
[extra]
wordpress_id = 1466
kind = "page"
node_key = "1466"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/mybookshelf2-ebooks-management-and-sharing/"
source_guid = "http://zderadicka.eu/?page_id=1466"
source_date_gmt = "2016-10-03 08:24:17"
menu_order = 0
parent = "/projects/python/"
+++
**Mybookshelf2** is next generation solution for sharing and managing ebooks for personal or community purposes. It's fully web based written in Python and Javascript. Basically it is a complete rewrite of my old project [Mybookshelf](/projects/python/mybookshelf-ebooks-library/) (with completely new technologies)

The key focus is on:



- enabling different files for an ebook - event same formats multiple times (that was one of my key issues with Calibre, because it enables only one file per format).
- Easy way to convert ebook to needed format (event from doc files) from selected file. Mass conversion of all ebooks of given author, all ebooks in series, bookshelf.
- Easy way to upload file to new or existing ebook (use metadata in file, auto-completes to add authors, series ...) .
- Accessible from any device, responsive design (at least for read - Ebooks readers usually have fairly basic web browsers, so simple pages should be available for ebooks listing and download in such devices).
- Easy and intuitive organization of ebooks using 'bookshelves' ( a list of books) -  you can have as many bookshelves as needed - ( like Want to read,  Top 100 books, Recommended to me, ...)





## Video Demo


Basic usage of MBS2 - list, search, add ebooks, convert ebooks:



<div class="video-embed"><iframe allowfullscreen="" height="315" loading="lazy" src="https://www.youtube.com/embed/VP0beQ-13V0" title="YouTube video" width="560"></iframe></div>



<p class="embed-fallback"><a href="https://www.youtube.com/watch?v=VP0beQ-13V0&feature=youtu.be">Watch on YouTube</a></p>



New features added in current 'beta' version (bookshelves, merge, mass conversion):



<div class="video-embed"><iframe allowfullscreen="" height="315" loading="lazy" src="https://www.youtube.com/embed/OZI9_iPmr0I" title="YouTube video" width="560"></iframe></div>



<p class="embed-fallback"><a href="https://youtu.be/OZI9_iPmr0I">Watch on YouTube</a></p>




## Source Code


Project is currently in beta status - code is available here [at github](https://github.com/izderadicka/mybookshelf2).
Application can be easily installed and tried with help of the [Docker](https://www.docker.com/) \- see [instructions for deployment](https://github.com/izderadicka/mybookshelf2/blob/master/deploy/README.md).

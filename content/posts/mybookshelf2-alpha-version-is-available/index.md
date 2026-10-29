+++
title = "Mybookshelf2 Alpha Version is available"
path = "/mybookshelf2-alpha-version-is-available/"
date = "2016-11-01T10:53:50"
include_in_feeds = true
[extra]
wordpress_id = 1486
kind = "post"
node_key = "1486"
author = "admin"
source_url = "http://zderadicka.eu/mybookshelf2-alpha-version-is-available/"
source_guid = "http://zderadicka.eu/?p=1486"
source_date_gmt = "2016-11-01 09:53:50"
categories = ["Announcement", "Programming"]
+++
<a href="/projects/python/mybookshelf2-ebooks-management-and-sharing/">Mybookshelf2</a> enters the stage, when code can be considered of alpha quality.  Basic functionality is there, so it could be tried and I plan to move my ebooks collection to it soon.  MBS2 is packed with new technologies and comparing to previous version (<a href="/projects/python/mybookshelf-ebooks-library/">Mybookshelf</a>) it can be considered a completely new application.

So what's new?  Concerning functionality not much,  but a lot happened internally. For me it's more about testing and playing with new technologies then managing ebooks (which is still important of course).  Maybe some of currently used technologies are bit of overkill (like using <a href="/wamp-is-websocket-on-steroids/">WAMP protocol</a>), but nevertheless they play important part in the application.<span id="more-1486"></span>

All server side  code is written in Python, for this project I decided to use Python 3.5 without backwards compatibility. Python 3.5 is stable enough now and it's syntax extensions for <a href="https://docs.python.org/3/library/asyncio.html">asyncio</a> (which are used in the project) are really nice. Front end is using <a href="http://aurelia.io/">Aurelia</a> Javascript framework, which is leveraging  latest JS achievements (ECMAScript 2016).

Below is block schema of Mybookshelf2 application:
<a href="/wp-content/uploads/MBS2.png"><img alt="mbs2" class="alignnone size-full wp-image-1504" decoding="async" height="483" loading="eager" sizes="(max-width: 794px) 100vw, 794px" src="/wp-content/uploads/MBS2.png" srcset="/wp-content/uploads/MBS2.png 794w, /wp-content/uploads/MBS2-300x182.png 300w" width="794"/></a>

Although the application looks bit complex to deploy you can easily try it with Docker,   <a href="https://github.com/izderadicka/mybookshelf2/tree/master/deploy">docker scripts</a> are available with application <a href="https://github.com/izderadicka/mybookshelf2">source code on github</a>.

You can also check <a href="/projects/python/mybookshelf2-ebooks-management-and-sharing/">its page on this web</a> short demo video.

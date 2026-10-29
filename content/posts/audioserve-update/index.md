+++
title = "Audioserve Update"
path = "/audioserve-update/"
date = "2018-11-19T09:11:32"
include_in_feeds = true
[extra]
wordpress_id = 1967
kind = "post"
node_key = "1967"
author = "admin"
source_url = "http://zderadicka.eu/audioserve-update/"
source_guid = "http://zderadicka.eu/?p=1967"
source_date_gmt = "2018-11-19 08:11:32"
categories = ["Announcement", "Programming"]
tags = ["Audiobook"]
+++
Some updates have been done on both <a href="/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/">audioserve</a> server (now in version 0.6.0) and Android client (now in version 0.7.0):<span id="more-1967"></span>


<ul>
<li>on server collection directory structure can be cached in memory for fast search - use option -<code>-search-cache</code></li>
<li>search results also contains folder path (both Android and Web client)</li>
<li>Web client -  cached parts of audio in player are displayed as a green bar</li>
<li>Android client has now bookmarks (in addition to automatically maintained recently listened) - bookmark  button is revealed by swipe left gesture on the item</li>
<li>Advanced playback options - speed and skip silence - pull up the playback controls to see</li>
</ul>


Just for comparison -   see memory requirements of audioserve vs airsonic:


```sh
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
ivan      2352  0.1 22.2 3115212 845704 ?      Sl   Oct23  65:42 java ...
ivan     13277  0.0  0.5 124108 22136 ?        Sl   Nov04   0:18 /opt/audioserve/audioserve ...
```


25x less virtual memory,  38x less resident memory.  audioserve is really lightweight!

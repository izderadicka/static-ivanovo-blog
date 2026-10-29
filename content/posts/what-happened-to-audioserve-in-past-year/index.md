+++
title = "What happened to audioserve in past year"
path = "/what-happened-to-audioserve-in-past-year/"
date = "2021-01-23T14:48:06"
include_in_feeds = true
[extra]
wordpress_id = 2273
kind = "post"
node_key = "2273"
author = "admin"
source_url = "http://zderadicka.eu/what-happened-to-audioserve-in-past-year/"
source_guid = "http://zderadicka.eu/?p=2273"
source_date_gmt = "2021-01-23 13:48:06"
categories = ["Programming"]
tags = ["audio streaming", "Audiobook"]
+++
Not much, but definitely it's not dead.  Actually I'm quite happy with current functionality and do not need more (actually there are couple of things that would be nice to have like shared bookmarks and read/finished audiobook attribute, but these will probably require to go beyond it's simplistic design) and I'm using it every day.  But some coding was done during past year and some small improvements were implemented.




<span id="more-2273"></span>




Main changes on server Rust code were not focused on features but on updating to latest dependent libraries. Asynchronous world in Rust is rushing up, so it was necessary to catch up.  Actually I have done two major updates - first at beginning of  2020 to use new futures and tokio 0.2 (plus hyper 0.13) and recently to update to tokio 1.0 (plus hyper 0.14). So audioserve is  now stuffed with latest and greatest asynchronous code available in whole galaxy :-) This effort not only updated dependencies but in many places I fixed incorrect or sub-optimal code - so hopefully  code is now bit better (especially error handling was moved to anyhow/thiserror and made more consistent).






Concerning features, just few were added:






<ul><li>possibility to set  base-dir - for cases when you are behind reverse proxy and need to add some root path before audioserve our path.</li><li>Enhanced logging of authentication and access failures - with remote ip (even if audioserve is behind reverse proxy)</li><li>Build in web client was enhanced with possibility to use space and arrow keys to control playback and login dialog is now correctly indicating failures. </li></ul>






On Android client I started with dark theme,   I do have some version in separate branch, running it on my mobile, but it still need some more changes. Cannot find strength to finish it, Android development sucks.






For code and changes check <a href="https://github.com/izderadicka/audioserve">audioserve on github</a>.

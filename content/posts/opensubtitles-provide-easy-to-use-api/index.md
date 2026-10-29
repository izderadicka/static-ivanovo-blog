+++
title = "OpenSubtitles provide easy to use API"
path = "/opensubtitles-provide-easy-to-use-api/"
date = "2015-05-09T08:34:19"
include_in_feeds = true
[extra]
wordpress_id = 1020
kind = "post"
node_key = "1020"
author = "admin"
source_url = "http://zderadicka.eu/opensubtitles-provide-easy-to-use-api/"
source_guid = "http://zderadicka.eu/?p=1020"
source_date_gmt = "2015-05-09 07:34:19"
categories = ["Programming"]
tags = ["python", "video subtitles"]
+++
When working on <a href="https://github.com/izderadicka/btclient">btclient</a>, I was interested in possibility of downloading a subtitles for a video file, that is played. This seems to be common option in many player.  I've found that <a href="http://www.opensubtitles.org">opensubtitles.org</a> provides <a href="http://trac.opensubtitles.org/projects/opensubtitles/wiki/XMLRPC">XML-RPC remote API</a>,  which is very easy to use. With help of python `xmlrpclib` module, it's really a matter of minutes to create a simple working client.<span id="more-1020"></span>

The real trick then consists in finding right subtitles, which are synchronized with video file.  Opensubtitles provides here useful help - so called `moviehash` \-  this hash is calculated as (file size) + (checksum of first 64kB of file) + (checksum of last 64kB of the file).  Hash is easy and quick to calculate and can be used to search subtitles.  The moviehash is also being uploaded by video players, which can update moviehash when finishing to play video file with certain subtitles, thus giving evidence that this subtitles matched given video file.

But not always subtitles is found by moviehash,  then  other search options are available: by tag (one of tags if filename) or full text query.  However then subtitles returned may not by synchronized - and it's  then at discretion  of user (or advanced client program) to choose right one.  One of easy to use heuristics could be to use for keywords -  like: if movie file name contains BluRay or BRRip or BDRip  then subtitles file name should contain also one of these strings ( based on an observation that BlueRay rips usually have same timing).

Moviehash can be easily calculated even in streaming clients ( like <a href="https://github.com/izderadicka/btclient">btclient</a> ), if client supports seeking. First and last 64kB are  seeked and read before video is played.

My implementation of  opensubtitles.org client, in python, is available <a href="https://github.com/izderadicka/btclient/blob/master/src/opensubtitle.py">here</a>. Couple of implementation notes:


<ul>
<li>default xmlrpclib transport does not support HTTP proxy - but this is easily fixed by using transport based on urllib2</li>
<li>opensubtitles.org servers are not very stable, often overloaded and returning 500 error  for searches - so  some retries are needed to get  subtitles more reliably -  internally client has possibility of retries in <code>download&#95;if&#95;not&#95;exists</code> function</li>
<li>moviehash is calculated from file-like objects (to enable calculation from streams)</li>
</ul>

+++
title = "Next Audioserve Version"
path = "/next-audioserve-version/"
date = "2018-12-14T16:04:58"
include_in_feeds = true
[extra]
wordpress_id = 1975
kind = "post"
node_key = "1975"
author = "admin"
source_url = "http://zderadicka.eu/next-audioserve-version/"
source_guid = "http://zderadicka.eu/?p=1975"
source_date_gmt = "2018-12-14 15:04:58"
[taxonomies]
category = ["Announcement"]
tag = ["audio book", "audio streaming"]
+++
As I'm using audioserve for almost a year, I'm becoming quite keen about it - it's exactly what I wanted - simple, lightweight and works as I needed. With it listening to audiobooks is just a simple pleasure. Recently I updated audioserve server with couple more features, which might not be essential, but can be useful: **multiple transcoding formats**  ( meaning target formats) and **transcoding cache**.<span id="more-1975"></span>

Originally audioserve supported only opus codec and ogg container (which I think is still best choice) so I decided to refactor code to make it simple to use any other appropriate audio format and container (codec and container must be supported by ffmpeg indeed).  And with this refactoring I added also support for ogg in webm container, mp3 and  aac in ADTS container (as they have support in [Media Source Extensions ](https://developer.mozilla.org/en-US/docs/Web/API/Media_Source_Extensions_API)(MSE) in modern browsers, while ogg container has not). MSE can be used to create sophisticated web clients. There is one interesting gotcha in our transcoding - result of transcoding is directly send through pipe to HTTP response, stream cannot be than sought so no further updates done to container header, which is problem for many containers - for instance MP4 container cannot be used at all, WebM/Matroska  is missing audio duration, which causes problem in seeking during playback.

Transcoding cache saves successfully transcoded files in <a href="https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)">LRU cache</a> on disk. You can limit size of cache in respect of overall size and number of files. Cache can be beneficial, if you are often jumping between files  or several users are listening to same audiobooks. But if just one user is listening to audiobooks in rather linear fashion (chapter by chapter, book by book), there is no benefit in using the cache.  That's why transcoding cache is optional feature in audioserve and you need to translate it with the feature `transcoding-cache` explicitly enabled.

Above mentioned new features are available in [version 0.7.1](https://github.com/izderadicka/audioserve/releases/tag/v0.7.1) and LRU file cache is also available as standalone [library simple-file-cache](https://github.com/izderadicka/simple-file-cache).

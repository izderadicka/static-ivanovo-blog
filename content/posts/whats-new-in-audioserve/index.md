+++
title = "What's new in audioserve"
path = "/whats-new-in-audioserve/"
date = "2022-09-11T12:05:04"
include_in_feeds = true
[extra]
wordpress_id = 2316
kind = "post"
node_key = "2316"
author = "admin"
source_url = "http://zderadicka.eu/whats-new-in-audioserve/"
source_guid = "http://zderadicka.eu/?p=2316"
source_date_gmt = "2022-09-11 11:05:04"
categories = ["Announcement"]
tags = ["audio streaming", "audioserve"]
+++
Unfortunately I did not have much time to update my blog. But I'm not dead and neither audioserve is - actually last half of year or so I focused on building <a href="https://github.com/izderadicka/audioserve-web">new client</a>. As of now new client is ready for production (version 0.3.3 +) and server has some new functionality too, mainly to support new client.<br/><br/>There is now <a href="https://audioserve.zderadicka.eu">online demo</a> automatically built from master branch (shared secret is mypass).




<span id="more-2316"></span>




Main idea behind new client was to implement same caching possibilities as older Android client had.  I felt this is really key feature to assure smoothness of listening experience and resilience to short term network unavailability and possibility to listen when offline.






Key technology for that is <strong>Service Worker and  Cache Storage</strong> \- this enables to cache ahead audio files and also store content of whole folder for off-line playback (provided that relevant api responses for that folder are in cache too - these are cached also via Service Worker into custom network-first cache). 






It took me some time to play around with Service Worker, I wanted to build functionality from scratch to learn more about it and I also bit suspected that prepared solutions (like <a href="https://developer.chrome.com/docs/workbox/">Workbox</a>) would not work for may use case  -  I did have quite particular requirements for audio files caching.  Some interesting problems I met:






<ul><li> You cannot rely on Service Worker life time, especially Firefox is quite  aggressive on killing Service Worker, if client pages are not active.<br/>This caused problems, if there is a queue of longer files to be preloaded. I solved this with periodic polling of service worker while it is preloading files.</li><li>Regular Cache and Cache Storage filled via Service Worker can interfere in  quite complex ways.  Better to set Cache-Control to no-store for resources that are managed by custom cache.</li><li>Do not cache error responses -  custom cache can cache everything, so do not cache errors like 401 (lesson learned :-). However 404s can be different story - see later discussion.</li></ul>






Another notable functionality in web client are <strong>folder icons</strong>.  I'm not much of fan of too visual applications (text information is enough for my navigation), neither I do have consistent cover images in my collection, but it's kind of standard for such an application so I added it in. It brought couple of interesting aspect:






<ul><li>I had to build scaling and caching service in audioserve server, so that icons are served efficiently. Initially icon is created from cover image stored in folder - it's scaled to given size (configurable with 128px default) and then stored in cache (on file system, not memory, linux does good job on caching frequently used files, if there is enough memory). Next time same icon is served from cache.</li><li>This opened another yet unsolved problem - how to get cover image for single file audiobooks - .m4b files.  So I extended media-info sub crate to extract cover from .m4b (where it is represented as another stream of video type and MJPEG codec).</li><li>On client side I implemented efficient loading of folder icons within subfolders list - using `<code>IntersectionObserver</code> as recommended by PWA guidelines.  Interestingly provided third party solution for Svelte <a href="https://github.com/maciekgrzybek/svelte-inview/issues/22#issuecomment-1216832064">did not fit well</a>.  First reason is mentioned in the link,  second reason came from need to be able to quickly cancel download of icon, that left view.</li><li>It also brought interesting issue of 404 responses caching -   in my collection I do have quite a lot of folders without cover image - so 404 responses are returned for their icons.  But since collection content is rather static, it would  make sense, in this case, to cache them. I looked over internet articles and general opinion is that it make sense to cache them, if there is good reason for it.  However practice is bit different - I had enabled cache via Cache-Control header on 404 response, but only Chrome supports it, Firefox <a href="https://bugzilla.mozilla.org/show_bug.cgi?id=1787538">is not caching 404s</a>, even when it has proper header.<br/>(Indeed the proper solution would be to provide information from the server - if subfolder has icon or not)</li></ul>






I also had couple of issues with Chrome browser  where I discovered some bugs  - while <a href="https://bugs.chromium.org/p/chromium/issues/detail?id=1337536">first one</a> with `MediaSession` implementation is still pending, <a href="https://bugs.chromium.org/p/chromium/issues/detail?id=1350730#c_ts1659964158">second one - regression in range input</a> was to my surprise resolved very quickly.






So this is where audioserve is now, near future plans are (mostly now driven by users feedback by<a href="https://github.com/izderadicka/audioserve/issues"> github issues</a>):






<ul><li>Add finished and last modified information to files (server) and appropriate support in web client </li><li>Solve icons 404s - just for fun, I'd like to play with 404 cache in client, but proper solution will also require change in collections cache on server.</li></ul>






For long term ideas, I was thinking about:






<ul><li>Improve Rust binding to libavformat and libavcodec so I can implement transcoding in Rust and have more control over it.</li><li>Use Web Audio API - something that will implement custom player and will interact better with server, especially for transcoded streams.</li><li>The two activities above may lead to DASH support of something like this - adaptable bandwidth and more reliable playback. Will see. </li></ul>






So that all for now - if you are using audioserve and have some ideas or problems please share them via <a href="https://github.com/izderadicka/audioserve/issues">GitHub issues</a>.

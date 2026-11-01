+++
title = "Are you dead?"
path = "/are-you-dead/"
date = "2021-10-29T18:46:17"
include_in_feeds = true
[extra]
wordpress_id = 2287
kind = "post"
node_key = "2287"
author = "admin"
source_url = "http://zderadicka.eu/are-you-dead/"
source_guid = "http://zderadicka.eu/?p=2287"
source_date_gmt = "2021-10-29 17:46:17"
[taxonomies]
category = ["Programming"]
tag = ["audio streaming", "audioserve", "Rust"]
+++
Not yet. However I did not publish much in last 9 month or so due to several reasons- and covid was not the least significant one.  I started couple of interesting things, but was lazy and demotivated to sum them up even in small article. I also changed my job few months back, which kept me quite busy, but positive impact was I'm waking up from lethargy caused by covid and past job. 






So I'll try to quickly summarize past year or so in here, it'll be nothing special, just to have things accounted:




<span id="more-2287"></span>




## Audioserve






Audioserve is still my favorite hobby project. I'm using it every day to listen to audiobooks and I'm mostly happy with it's functionality (and friend of mine voluntarily migrated from iOS to Android to be able to use it :-)






Until recently there has not been much progress, in released versions there are  just couple of new things:






<ul><li>**Android **client -  finally there is "**dark theme**" working. I'm using it and more or less happy with it (especially on OLED displays dark themes make sense). However I think Android client (as it's written now) reaches it zenith.  I was not able to update some dependencies to newer versions, because  they will break the code. I think it'll need complete rewrite, but I do not have time neither will to do it now. So I hope it'll survive future versions of Android.<br/>It still has many positive things, mainly the aggressive caching, but it sucks on UX side - user interface will need complete rewamp.</li><li>  On server side I just fixed couple of bugs mainly focused on** **<a href="https://github.com/izderadicka/audioserve/issues/46">**security**</a>.</li><li>Most interesting work on server was adding rate liming of incoming request inspired by [Leaky Bucket algorithm](https://en.wikipedia.org/wiki/Leaky_bucket) (used for instance in nginx] and implemented it in [this crate](https://github.com/izderadicka/audioserve/tree/master/crates/leaky-cauldron).</li><li>Also interesting was adding async zip folder download ([this crate](https://github.com/izderadicka/audioserve/tree/master/crates/async-zip))</li><li>Web client received also couple of bug fixes plus support for **playback speed** button.</li></ul>






But recently I've got new impulse and quite a lot of new functionality is prepared in master branch,  I'll just need bit more time to test, document, polish and release.  Here are the things you can look forward:






<ul><li>New collections cache, based on [sled](https://github.com/spacejam/sled) - fast Rust native key-value store.  It enables fast response for folders with many audio files and it is enabler for other cool functionality below ( it sounds as simple stuff but it was major effort in refactoring audioserve to use this new cache).</li><li>More reliable playback positions tracking.</li><li>Faster propagation of collection directory changes (add, delete, rename) into cache - especially useful for search.</li><li>Backup of playback positions - you will never loose your playback positions if you back them up regularly.</li><li>Marking folders as read/finished - this was<span style="text-decoration: underline;"> very much wanted functionality</span>.  Just listen to folder to it's end and it is automatically marked as finished (unless you start to listen to it again, then it's unmarked). (Web client only for now)</li><li>Audio files tags metadata are displayed.   If you read previous  articles you know I'm very skeptical about tags, they are especially messy for audiobooks. But with new cache it's easy to read them, so we can at least show them, so you see this mess with your own eyes. (Web client now only)</li><li>Regular API (REST) for playback position.   We did have very special custom protocol over WebSocket, which is efficient, but not much convenient. So new API is more easy to use for custom client. </li></ul>






Speaking about clients, you probably noticed that I'm not very good at UX and UI - I try to elude the fact by babbling about simplistic interfaces etc., but sad truth is my client solutions just did not stand to recent standards.  So I was quite excited when KodeStar started his [audiosilo project](https://github.com/KodeStar/audiosilo) for new web client for audioserve.  UI looks quite nice,  though functionality is still missing, but hopefully it'll improve over time.






## Rust






Apart of audioserve I worked on few minor Rust things:






<ul><li>working on few small exercises, just to confirm that [performance matters](/performance-should-matter/) as I noted a year ago</li><li>Playing around with P2P:<ul><li>My [very dumb client](https://github.com/izderadicka/crevise) using UDP and noise encryption </li><li>I also [played with libp2p](https://github.com/izderadicka/p2pmsg) and tried to use its different protocols </li></ul></li><li>Implemented [PROXY protocol for tokio](https://github.com/izderadicka/tokio-proxy-protocol) </li><li>I've created [small but interesting library](https://github.com/izderadicka/dstream) for debouncing (based on message key)  async tokio stream. As part of effort I explored code coverage statistics based on current rustc features and github actions.</li></ul>






## Java






And since I professionally got again back to Java I've created very simple demo for micro services based on Spring Boot and their deployment to Kubernetes / Openshift.  Code is not worth to present, but it is still around on my github repo.

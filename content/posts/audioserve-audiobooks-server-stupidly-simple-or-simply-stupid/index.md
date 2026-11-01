+++
title = "Audioserve Audiobooks Server - Stupidly Simple or Simply Stupid?"
path = "/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/"
date = "2018-01-20T20:20:24"
include_in_feeds = true
[extra]
wordpress_id = 1833
kind = "post"
node_key = "1833"
author = "admin"
source_url = "http://zderadicka.eu/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/"
source_guid = "http://zderadicka.eu/?p=1833"
source_date_gmt = "2018-01-20 19:20:24"
[taxonomies]
category = ["Programming", "Tools"]
tag = ["audio streaming", "Audiobook"]
+++
If you read some of my previous articles you know that I'm quite fond of audiobooks.   In past I was [looking for good media server](/media-server-for-music-and-audio-books/), which supports audiobooks  and ended with  [airsonic ](https://github.com/airsonic/airsonic)(a subsonic clone).   The problem with majority of media servers is that they rely totally on audio tags, which are often messed in audiobooks. Also many of "advanced" functionalities are not applicable to audiobooks (random play, shuffle tracks, moods, etc.)  I'm bit of old school so I rely more on reasonable directory structure and do not want to mess with tags for every audiobook I download. I also think that for personal collection I do not need likes, favorites, sharing and similar stuff,  as I can easily remember which books are good and which I have listened or want to listen, but I do need few things, which are usually missing - like bookmarks. Interesting function is to continue listen on a device, when I left  on previous device, but since I basically listen only on my mobile phone, it does not seems to be critical. So ideal audiobooks server actually requires much less functionality than today's media servers provide.  As I'm progressing with Rust language I decided two weeks ago to create simple audio streaming server adhering to KISS principle - Keep It Simple, Stupid, - Result of this exercise is an  application that provides minimum viable functionalities for streaming and listening of audiobooks - it's called [Audioserve](https://github.com/izderadicka/audioserve).  In this article I'll show it's basic design and demo current application in a video.<span id="more-1833"></span>


### Required functionality





- Support for common audio formats, especially mp3, opus (I think [opus is a great format for audio books](/opus-audio-codec-for-audio-books-and-more/)), m4b, m4a ...
- HTTP audio streaming
- SSL/TLS support
- Some simple authentication mechanism, no need for users etc., as this is a personal server, but something to prevent unauthorized access
- Provide transcoding to opus to save bandwith and to support more formats
- Browse audiobooks as they are stored  - e.g. in their directory structure, order alphabetically according to file/dictionary names
- Support some additional metadata on folder level - cover image and audiobook/author description
- Some simple search
- Prefer audiobooks split to chapters, but should be able also to play long files (several hours)
- Play whole book - automatically start next chapter after current chapter is finished
- Quick and convenient seek -  quickly find required part in audio file - even for large files
- Remember last position, to  continue with it listening later, optionally bookmarks to different positions in different audiobooks
- Simple web based client,  possibly native mobile (Android) client for better cashing, off-line playback
- Possibility to cache ahead chapters or even whole books - so one can survive connectivity  loss or even  listen off-line
- Small, lean and fast





### Implementation


Audioserve is implemeted in [Rust language](https://www.rust-lang.org), it's using the [hyper](https://github.com/hyperium/hyper) library for HTTP support, but no complex framework to make it lean. Audioserve provides very simple JSON API to browse the collection and functions to serve audio files directly or transcoded (external [ffmpeg](https://www.ffmpeg.org/) utility is required).  Authentication is achieved through shared secret phrase. Audioserve also contains bundled web client for modern browsers (latest Firefox or Chrome).

From above requirements reliable caching  now implemented only in Android client. In web clients it depends now solely on HTML5 media player, Firefox seems to provide better caching then Chrome. Reliable caching will require deep dive into advanced browser APIs ( Service Workers and/or Media Source Extensions), for which I did not have time yet.  Also generic bookmarks are  available only in Android client (thought it  should not be difficult to implement in Web), only one last played position is remembered.


### Demo




<div class="video-embed"><iframe allowfullscreen="" height="315" loading="lazy" src="https://www.youtube.com/embed/7wUI22b1Jbg" title="YouTube video" width="560"></iframe></div>



<p class="embed-fallback"><a href="https://youtu.be/7wUI22b1Jbg">Watch on YouTube</a></p>



UPDATE: And also now Android client is now available  you can check [in this article](/audioserve-android-client-early-beta-is-available/).


### Installation


Easiest way how to try Audioserve is to use provided Dockerfile and run [Docker](https://www.docker.com/) container. See README in[ Audioserve repository](https://github.com/izderadicka/audioserve).

For time being for can also check [online live demo](/audioserve-demo-on-heroku/).

Currently Audioserve is tested only on Linux.

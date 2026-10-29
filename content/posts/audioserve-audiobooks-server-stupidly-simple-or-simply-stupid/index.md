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
categories = ["Programming", "Tools"]
tags = ["audio streaming", "Audiobook"]
+++
If you read some of my previous articles you know that I'm quite fond of audiobooks.   In past I was <a href="/media-server-for-music-and-audio-books/">looking for good media server</a>, which supports audiobooks  and ended with  <a href="https://github.com/airsonic/airsonic">airsonic </a>(a subsonic clone).   The problem with majority of media servers is that they rely totally on audio tags, which are often messed in audiobooks. Also many of "advanced" functionalities are not applicable to audiobooks (random play, shuffle tracks, moods, etc.)  I'm bit of old school so I rely more on reasonable directory structure and do not want to mess with tags for every audiobook I download. I also think that for personal collection I do not need likes, favorites, sharing and similar stuff,  as I can easily remember which books are good and which I have listened or want to listen, but I do need few things, which are usually missing - like bookmarks. Interesting function is to continue listen on a device, when I left  on previous device, but since I basically listen only on my mobile phone, it does not seems to be critical. So ideal audiobooks server actually requires much less functionality than today's media servers provide.  As I'm progressing with Rust language I decided two weeks ago to create simple audio streaming server adhering to KISS principle - Keep It Simple, Stupid, - Result of this exercise is an  application that provides minimum viable functionalities for streaming and listening of audiobooks - it's called <a href="https://github.com/izderadicka/audioserve">Audioserve</a>.  In this article I'll show it's basic design and demo current application in a video.<span id="more-1833"></span>


### Required functionality




<ul>
<li>Support for common audio formats, especially mp3, opus (I think <a href="/opus-audio-codec-for-audio-books-and-more/">opus is a great format for audio books</a>), m4b, m4a ...</li>
<li>HTTP audio streaming</li>
<li>SSL/TLS support</li>
<li>Some simple authentication mechanism, no need for users etc., as this is a personal server, but something to prevent unauthorized access</li>
<li>Provide transcoding to opus to save bandwith and to support more formats</li>
<li>Browse audiobooks as they are stored  - e.g. in their directory structure, order alphabetically according to file/dictionary names</li>
<li>Support some additional metadata on folder level - cover image and audiobook/author description</li>
<li>Some simple search</li>
<li>Prefer audiobooks split to chapters, but should be able also to play long files (several hours)</li>
<li>Play whole book - automatically start next chapter after current chapter is finished</li>
<li>Quick and convenient seek -  quickly find required part in audio file - even for large files</li>
<li>Remember last position, to  continue with it listening later, optionally bookmarks to different positions in different audiobooks</li>
<li>Simple web based client,  possibly native mobile (Android) client for better cashing, off-line playback</li>
<li>Possibility to cache ahead chapters or even whole books - so one can survive connectivity  loss or even  listen off-line</li>
<li>Small, lean and fast</li>
</ul>




### Implementation


Audioserve is implemeted in <a href="https://www.rust-lang.org">Rust language</a>, it's using the <a href="https://github.com/hyperium/hyper">hyper</a> library for HTTP support, but no complex framework to make it lean. Audioserve provides very simple JSON API to browse the collection and functions to serve audio files directly or transcoded (external <a href="https://www.ffmpeg.org/">ffmpeg</a> utility is required).  Authentication is achieved through shared secret phrase. Audioserve also contains bundled web client for modern browsers (latest Firefox or Chrome).

From above requirements reliable caching  now implemented only in Android client. In web clients it depends now solely on HTML5 media player, Firefox seems to provide better caching then Chrome. Reliable caching will require deep dive into advanced browser APIs ( Service Workers and/or Media Source Extensions), for which I did not have time yet.  Also generic bookmarks are  available only in Android client (thought it  should not be difficult to implement in Web), only one last played position is remembered.


### Demo




<div class="video-embed"><iframe allowfullscreen="" height="315" loading="lazy" src="https://www.youtube.com/embed/7wUI22b1Jbg" title="YouTube video" width="560"></iframe></div>



<p class="embed-fallback"><a href="https://youtu.be/7wUI22b1Jbg">Watch on YouTube</a></p>



UPDATE: And also now Android client is now available  you can check <a href="/audioserve-android-client-early-beta-is-available/">in this article</a>.


### Installation


Easiest way how to try Audioserve is to use provided Dockerfile and run <a href="https://www.docker.com/">Docker</a> container. See README in<a href="https://github.com/izderadicka/audioserve"> Audioserve repository</a>.

For time being for can also check <a href="/audioserve-demo-on-heroku/">online live demo</a>.

Currently Audioserve is tested only on Linux.

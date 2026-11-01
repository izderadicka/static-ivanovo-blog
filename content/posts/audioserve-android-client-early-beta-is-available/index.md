+++
title = "audioserve Android Client Early Beta Is Available"
path = "/audioserve-android-client-early-beta-is-available/"
date = "2018-04-28T16:14:09"
include_in_feeds = true
[extra]
wordpress_id = 1876
kind = "post"
node_key = "1876"
author = "admin"
source_url = "http://zderadicka.eu/audioserve-android-client-early-beta-is-available/"
source_guid = "http://zderadicka.eu/?p=1876"
source_date_gmt = "2018-04-28 15:14:09"
[taxonomies]
category = ["Announcement"]
tag = ["audio book", "audio streaming"]
+++
So finally there is something. I'm using it myself now to listen to audiobooks and it have almost all functionality I wanted it to have. It might be still bit unstable and few things is not well behaving (keep up long time in paused state, navigation between notifications and activities is still bit messy and few more issues), but generally it works.<span id="more-1876"></span> It was a tedious endeavor as I had to learn the Android platform (it was my first real Android app) and in basically took significantly more time then whole server and web client - see [previous article](/stupidly-complex-or-completely-stupid-android-development/) for some general comments about Android development.

Should support Android from API version 21 (Lollipop) till latest Oreo (API version 27). Tested on Nougat and Oreo.

As whole [audioserve](https://github.com/izderadicka/audioserve) it tries to stick to KISS principles - so it's up to you to decide if it is [Stupidly Simple or Simply Stupid](/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/).

Here is video demo:



<div class="video-embed"><iframe allowfullscreen="" height="315" loading="lazy" src="https://www.youtube.com/embed/EGfTJuSiGeE" title="YouTube video" width="560"></iframe></div>



<p class="embed-fallback"><a href="https://youtu.be/EGfTJuSiGeE">Watch on YouTube</a></p>



To check the code and download .apk file go to its[ github repo](https://github.com/izderadicka/audioserve-android) (apk files are in releases).  You test you will need audioserver server - which you can download from other github repo (easiest way to try server is in docker, but compilation is also pretty straightforward in Linux)

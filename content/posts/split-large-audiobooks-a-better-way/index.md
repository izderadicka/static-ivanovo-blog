+++
title = "Split Large Audiobooks - A Better Way"
path = "/split-large-audiobooks-a-better-way/"
date = "2019-01-17T21:11:21"
include_in_feeds = true
[extra]
wordpress_id = 1998
kind = "post"
node_key = "1998"
author = "admin"
source_url = "http://zderadicka.eu/split-large-audiobooks-a-better-way/"
source_guid = "http://zderadicka.eu/?p=1998"
source_date_gmt = "2019-01-17 20:11:21"
[taxonomies]
category = ["Digital Media", "Programming"]
+++
In [previous article](/splitting-large-audio-books/) I presented bash script to split large audiobook file into smaller parts. It worked well for me, but has one limitation - if chapters information was not available in the metadata, then file was split into parts of exact size, which was clearly sub-optimal, as split can fall into middle of a word.  So I created new script (this time in Python as logic was bit more complicated, more then I'm conformant to implement in bash), which first detects silent spots in the audiobook and splits file there. Additionally you can also supply external CSV file, which defines  mapping  to chapters (It's easy to create this file, just require a bit of patience and good tool like [audacity](https://www.audacityteam.org/) to capture the exact positions of chapter ends). I tested my tool on tens of large single file audiobooks and it seems to work fine. You can check this script in [its github repo](https://github.com/izderadicka/split_audiobook).

+++
title = "Beautiful Code History Visualization with Gource"
path = "/beautiful-code-history-visualization-with-gource/"
date = "2015-06-14T09:59:58"
include_in_feeds = true
[extra]
wordpress_id = 1042
kind = "post"
node_key = "1042"
author = "admin"
source_url = "http://zderadicka.eu/beautiful-code-history-visualization-with-gource/"
source_guid = "http://zderadicka.eu/?p=1042"
source_date_gmt = "2015-06-14 08:59:58"
categories = ["Programming"]
tags = ["version control", "visualization"]
+++
<a href="https://code.google.com/p/gource/">Gource</a> tool offers very nice and appealing visualization  of SW project history. Gource works with all major version control systems - git, svn, etc.  can be easily installed from Ubuntu repos and is fairly easy to use.<span id="more-1042"></span>

Here is visualization of my <a href="https://github.com/izderadicka/btclient">btclient</a> project (videos works best in Firefox):



<video controls="" preload="metadata"><source src="/wp-content/uploads/gource.mp4" type="video/mp4"/></video>



Generated with this command:


```sh
gource --file-idle-time 0 -s 1 --auto-skip-seconds 1 --stop-at-end --title BTClient --output-ppm-stream - -r 25 ~/workspace/btstream/.git/ | ffmpeg -y -r 25  -f image2pipe -vcodec ppm -i -  -vcodec libx264 -preset medium -vprofile baseline -level 3.0 -pix_fmt yuv420p gource.mp4
```


 

And here visualization of more complex project - <a href="http://www.libtorrent.org/">libtorrent</a>:



<video controls="" preload="metadata"><source src="/wp-content/uploads/gource2.mp4" type="video/mp4"/></video>



Generated with this command:


```sh
gource -s 0.01 --file-idle-time 0  --hide filenames --date-format "%B %Y" --stop-at-end --title libtorrent --output-ppm-stream - -r 25 libtorrent-fixed/.svn/ | ffmpeg -y -r 25  -f image2pipe -vcodec ppm -i -  -vcodec libx264 -preset medium  -vprofile baseline -level 3.0 -pix_fmt yuv420p  gource2.mp4
```

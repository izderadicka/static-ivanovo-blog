+++
title = "Video Streaming from File Sharing Servers"
path = "/video-streaming-from-file-sharing-servers/"
date = "2015-05-10T12:56:00"
include_in_feeds = true
[extra]
wordpress_id = 1024
kind = "post"
node_key = "1024"
author = "admin"
source_url = "http://zderadicka.eu/video-streaming-from-file-sharing-servers/"
source_guid = "http://zderadicka.eu/?p=1024"
source_date_gmt = "2015-05-10 11:56:00"
[taxonomies]
category = ["Programming"]
tag = ["python", "video streaming"]
+++
As I've written [video files can be streamed via Bit Torrent protocol](/streaming-video-file-from-bittorrent-p2p-network/). Although responsiveness (time to start, time to seek) is notably worst that in specialized solutions, it is still usable for normal user, with a bit of patience.

Video files are also provided by file sharing servers,  but in many cases download rate is limited, so it's not enough to stream video file. However it's often possible  to open several requests for same file, and combine download rate - this method is quite common in download managers. And if we add possibility to stream downloaded content to video player, we can achieve satisfactory results, possibly similar as or better then streaming via Bit Torrent.<span id="more-1024"></span>

Inspired by my previous work on [btclient](https://github.com/izderadicka/btclient) (video streaming via Bit Torrent protocol), I extended it to stream video also from HTTP source,  with possibility of several concurrent connections.  Video file is divided to pieces (2MB, similarly to BT) and pieces are downloaded by concurrent connections as needed.

In order to enable seeking, pieces are scheduled in priority queue (heap),  with a piece at current playing point and next few following  pieces having highest priority (similar to piece deadline in libtorrent - priority set concept explained in previous article ). Otherwise pieces are downloaded sequentially.

General principle of client operation is:



- Start first connection, begin with resolving given URL to final link to video file (we use plugins to enable  easy adaptation of  client for different services)
- Get first block to get file size, calculate number of pieces
- Start  next x connections (again starting with resolving URL - each connection is basically independent client/user agent from point of view of the server) , each one taking  a piece at time  from priority queue and downloading it
- Combine pieces together
- Server them via HTTP server on local computer
- If seeking is initiated via HTTP request, and a piece mapped for given seek offset is not already downloaded,  piece is added to  priority queue with highest priority,  and following 5 pieces with decreasing priority (but still higher then normal priority).



The concept was tested on uloz.to file sharing service,  together with some of my previous work on [decoding audio captchas](/decoding-audio-captchas-in-python/) ( to help here to resolve video file link) I was able to start to playback of  HD content after app. 40 seconds,  and live play  relatively reliably video files encoded with byte rate up to 800kB/s, streaming them from 4 concurrent connections (having download rate about 1000kB/s).

+++
title = "Streaming video file from BitTorrent P2P network"
path = "/streaming-video-file-from-bittorrent-p2p-network/"
date = "2014-10-05T10:40:36"
include_in_feeds = true
[extra]
wordpress_id = 898
kind = "post"
node_key = "898"
author = "admin"
source_url = "http://zderadicka.eu/streaming-video-file-from-bittorrent-p2p-network/"
source_guid = "http://zderadicka.eu/?p=898"
source_date_gmt = "2014-10-05 09:40:36"
categories = ["Programming"]
tags = ["BitTorrent", "python"]
+++
Although <a href="http://en.wikipedia.org/wiki/BitTorrent">BitTorrent </a>(BT) protocol was not designed for media streaming, in practice it can be used, with certain extent, to stream a video file from P2P network. Key trick is to force sequential download in BT client (normally BT client selects first pieces, that are least available in swarm,  which contributes to better distribution of the file, sequential download is playing against it, so it is not enabled in regular BT clients).

But if we force BT client to download sequentially, cache incoming pieces and have enough incoming bandwidth from peers, we can stream incoming video directly into video player.  Indeed it's a poor man streaming, because it lacks any advanced features like stream synchronization, stream seeking etc., but in many cases it works just good enough.<span id="more-898"></span>

There is also project <a href="http://labs.bittorrent.com/experiments/bittorrent-live.html">BitTorrent Live </a> where BT protocol inventor Bram Cohen comes with enhancement of BT protocol to enable media streaming.  This project started at 2011, but it seems to be bit stalled now. (for curious here is link to <a href="https://www.scribd.com/doc/132418122/Bittorrent-Live-Patent">US patent  for BitTorrent Live - P2P Live Streaming</a>).

There has been also some academic research in this area (<a href="http://www.bth.se/fou/forskinfo.nsf/0/ccdac2d8c76d6fc2c12575d00048cdb2/$file/2008-sncnw-bittorrent-final-version.pdf">paper1</a> , <a href="http://www.researchgate.net/publication/224694116_BiToS_Enhancing_BitTorrent_for_Supporting_Streaming_Applications">paper2</a> ), proposing improvement to BT protocol to help with video streaming, focusing mainly on modifications to piece selection mechanism in client, where pieces are split into 3 sets:


<ul>
<li> pieces before current play point in file are either not downloaded or are seeded if they were downloaded before</li>
<li>a small set of pieces including and immediately after  current play point (priority set) - are downloaded with highest priority and utilizing preferably high speed peers</li>
<li>remaining pieces (after priority set) - are downloaded with normal priority, sequentially or even can use regular rarest fist piece selection.</li>
</ul>


I've tested couple of available applications available, which work with standard BT protocol, but use sequential download and piece prioritization to stream video file:

<a href="http://acestream.org/">acestream </a> \- is not open source, so I did not spent too much time with it but it generally works,

<a href="https://github.com/steeve/plugin.video.pulsar">Pulsar</a> \- open source, streaming client is written in Go language, using bindings to libtorrent and it is integrated in <a href="http://kodi.tv/">Kodi</a> media centrer software as video plugin,  it is successor of <a href="http://forum.xbmc.org/showthread.php?tid=174736">XBMCTorrent </a>
<a href="https://github.com/mafintosh/peerflix">peerflix</a> \- streaming Bittorrent client, written in Javascript, running under <a href="https://nodejs.org/">Node.js</a>,   used also in popular Popcorntime application. peerflix client seemed to be fastest to start play, provided also best seek responses.

All these clients are working in similar fashion -  there is separate BT client process, that uses sequential mode to download torrent and as pieces are downloaded it streams them via HTTP protocol to  video player. Playback starts, when 'enough' data is cached - in XBMCTorrent it was 1% of torrent size.

As I noted all solutions somehow works,  but they are bit heavy-weighted,  I'd  tried something simple on my own and created simple streaming <a href="https://github.com/izderadicka/btclient">BTClient</a> in Python .  It uses excellent <a href="http://sourceforge.net/projects/libtorrent/">libtorrent</a> library, which enables to do sequential downloads and advanced pieces prioritization.  BTClient is a command line utility - it can open either torrent file, or open link to torrent file or magnetic link.  It then reads torrent metadata, selects largest video file in the torrent and starts it's sequential download. After it caches about 1% of the file it starts video player (mplayer or VLC) and streams video to it via HTTP (or stdin, but seek is not supported then) . While playing BTClient shares torrent and provides uploads to other peers. Seeking in the video file is supported.


#### Screenshot


<a href="/wp-content/uploads/scr.png"><img alt="scr" class="alignnone size-full wp-image-901" decoding="async" height="644" loading="eager" sizes="(max-width: 1151px) 100vw, 1151px" src="/wp-content/uploads/scr.png" srcset="/wp-content/uploads/scr.png 1151w, /wp-content/uploads/scr-300x167.png 300w, /wp-content/uploads/scr-1024x572.png 1024w" width="1151"/></a>


#### Implementation notes:


libtorrent provides several ways, how to influence pieces selection:


<ul>
<li>sequential download -  this can be set for whole torrent</li>
<li>pieces prioritization -  priority can be set to individual pieces - from 0 (piece is not downloaded) to 7 (highest priority)</li>
<li>piece deadline -  when piece is prioritized, it means only that it  starts with priority, but it does not mean that it'll be finished before non-prioritized pieces.  If piece is downloaded from slow peers, it can easily end after non-prioritized pieces. If  setting piece a deadline ( a time in future, when piece should be finished), libtorrent downloads piece's blocks from fastest peers to meet the deadline.</li>
</ul>


BTClient leverages all above methods to achieve responsive video streaming:


<ul>
<li>only pieces for video file are downloaded (other files pieces are set to priority 0)</li>
<li>sequential download is set for the torrent</li>
<li>pieces before last seek point have priority set to 0 (so they will not be started, if have not been started  or downloaded already)</li>
<li>piece at last seek/read point and it's 5 successors have highest priority and deadline set</li>
<li>remaining pieces are downloaded with normal priority</li>
<li>get tail of the file at beginning -   it helps with quick video player start  (because both mplayer and VLC look at be video file ending before they start to play it).  It is also used to search for subtitles (opensubtitles are using file hash from first and last 64kB of the file for search)</li>
</ul>




#### Possible improvements:




<ul>
<li>Player control (to pause if there are no data to send - DBus ?)</li>
<li>MPlayer OSD?</li>
<li>Use Mplayer in slave mode via API?</li>
<li>Custom player via gstreamer (this can provide much closer integration between BT client pieces prioritization and playback)</li>
<li>GTK3 GUI?</li>
</ul>

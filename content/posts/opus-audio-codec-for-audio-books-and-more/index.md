+++
title = "Opus Audio Codec for Audio Books And More"
path = "/opus-audio-codec-for-audio-books-and-more/"
date = "2015-10-25T21:19:42"
include_in_feeds = true
[extra]
wordpress_id = 1120
kind = "post"
node_key = "1120"
author = "admin"
source_url = "http://zderadicka.eu/opus-audio-codec-for-audio-books-and-more/"
source_guid = "http://zderadicka.eu/?p=1120"
source_date_gmt = "2015-10-25 20:19:42"
categories = ["Tools"]
tags = ["audio book", "opus codec"]
+++
<a href="https://www.opus-codec.org/">Opus</a> is a relatively new lossy audio codec from<a href="https://www.xiph.org/"> Xiph Foundation,</a> successor to Vorbis and Speex codecs.  It provides very good quality for low bandwidth (\<=32kbps) streams with speech, but also provides high quality for broader bandwidth (\>64kbps) and more demanding data like music etc.  So it can be one-off solution for any digital audio encoding.  According to <a href="http://www.opus-codec.org/comparison/">some tests</a> presented on it's site, it's comparable with HE AAC for higher bandwidth, higher quality data,  while it additionally  provides better results for lower bandwidth, speech data  this is something <a href="http://www.iis.fraunhofer.de/en/ff/amm/prod/digirundfunk/digirundf/xheaac.html">xHE ACC</a> is addressing too, however I have not seen available codec yet.).  And what is most appealing on Opus is that it's free, without patents and it's open source.  (While majority of common audio codecs e.g MP3, AAC are restricted by patents and are subject to paying loyalties , I think <a href="https://www.fraunhofer.de/en.html">Fraunhofer</a> holds basic patents, but situations is quite complex and differs per country).

Based on positives reviews, I though that Opus could be ideal codec for audio books, where it can provide good quality at low bit rates. At least for me, I really do not need top quality for audio books  (say mp3 320kbps), while the book takes gigabytes of space, but on the other hand,  I do appreciate good quality and with low quality audios I have problems to understand them and I cannot really enjoy the book.

So how can Opus help and is it ready for everyday use?<span id="more-1120"></span>

On Linux I can encode audio to Opus inside <a href="https://xiph.org/ogg/">Ogg</a> container (in file with .opus extension - as per <a href="https://wiki.xiph.org/MIME_Types_and_File_Extensions#.opus_-_audio.2Fogg">recommended content type for opus audio</a>) with <a href="https://www.ffmpeg.org">FFmpeg</a>  ( not every distro has ffmpeg compiled with libopus,  however you can easily use <a href="http://johnvansickle.com/ffmpeg/">static builds</a>).  I've created this script to be able to convert whole directories (even recursively) efficiently (runs concurrently one conversion per core):


<script src="https://gist.github.com/izderadicka/0f66a9ee1a2594be1fd27792bbc0a18c.js"></script>


 

I converted several audio books (mp3 96kbps or 128kbps, stereo) with opus parameters defaulted in the above script - resulting Opus 32kbps stereo( also tried 24kbps stereo, difference between 24kbps and 32kbps was basically not significant, just choose 32kbps to be safe). I also  compared (listening on headphones (relatively good ones, Jabra) and external speakers (also fairly good, Yamaha) ) opus version to mp3 version and degradation in quality was small, fully acceptable for speech, bit more audible on musical parts of recordings  ,  (128kbps mp3 sounds bit better in headphones, for 96kbps difference was minimal).  The difference in size is however remarkable - opus is 3-4 times smaller and as I do not expect audiophile experiences from  audiobook listening, achieved quality is sufficient for me, audiobooks are pleasantly listenable. . As I do listen mostly on my mobile, where books audio file are streamed from my home server over Internet,  so spared bandwidth is very much appreciated. If high quality is essential I believe 64kbps opus can provide it , while still offering significant size reduction.

Encoding quality parameter plays significant role - I encoded at highest quality -  10, which is quite slow. However with lower quality - 8, which is about twice faster, notable degradation in quality was audible. 24kbps with quality 10 sounded better then 32kbps with quality 8.

Support for Opus in Linux (Ubuntu 14.04) is good - I can play it basically in any player (including default audio player Rhythmbox), however I hit some issues with Android (which is now device I use mostly for listening music and audio books).  On Android Opus in ogg container was supported only by VLC player (I believe couple more can play it, but I have only VLC installed).  Natively Android does support Opus, but only in matroska (.mkv) container (from 5.0+ as stated <a href="http://developer.android.com/guide/appendix/media-formats.html">here</a>).  Solution could be to use always matroska container,  but I still  prefer ogg, because it's more common container for Opus.  Since I use Libresonic (see also my <a href="/media-server-for-music-and-audio-books/">previous article</a>) to stream audio books to my mobile I can use transcoding.

Transcoding can be pretty basic, since both containers support Opus, so it's just about copying audio stream from one container to the other, which can be very fast. However there is still a small issue: if conversion is piped to output, resulting mkv container does not contain duration and stream size in header,  so resulting file is not seekable on  Android. Target of transcoding has to be fully searchable (e,g, file) so that ffmpeg can write duration and size to file  after conversion.  Solution was to create small transcoding script, which uses a temporary file:


```sh
#!/bin/bash
if [[ -f "$1"  ]]; then 
    TMPFILE=`mktemp`
    ffmpeg -y -v error -i "$1" -map 0:0 -c:a copy -f matroska $TMPFILE
    cat $TMPFILE
    rm $TMPFILE
else
    echo "Need audio file as param" >&2
fi
```


To improve performance and decrease disk usage we can use tmpfs for temporary files (if we have enough memory):


```sh
# put this into /etc.fstab
tmpfs /tmp tmpfs nodev,nosuid 0 0
```


Final note - I also tried webm container, which should be generally equivalent to mkv (with some limitations),  but for webm seeking in file was not working on android.

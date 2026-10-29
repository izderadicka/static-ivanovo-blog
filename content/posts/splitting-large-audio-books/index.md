+++
title = "Splitting Large Audio Books"
path = "/splitting-large-audio-books/"
date = "2017-10-21T14:49:13"
include_in_feeds = true
[extra]
wordpress_id = 1771
kind = "post"
node_key = "1771"
author = "admin"
source_url = "http://zderadicka.eu/splitting-large-audio-books/"
source_guid = "http://zderadicka.eu/?p=1771"
source_date_gmt = "2017-10-21 13:49:13"
categories = ["Digital Media", "Programming"]
tags = ["audio book", "ffmpeg"]
+++
I'm big fan of audio books.   During past years I've been using setup described <a href="/media-server-for-music-and-audio-books/">in this article</a> (libresonic server, android client, audio encoded with opus codec) for audio books listening.  It works well  for me , but it's best with audio books split to chapters or to parts not longer then 1 hour. However some audio books come in  one large file (m4b format, or  aax proprietary file  from <a href="https://www.audible.com/">Audible</a>).  To listen to such audio books conveniently I need to split them. Luckily with <a href="https://www.ffmpeg.org/">ffmpeg</a> tool and a bit of bash scripting it is not difficult. <span id="more-1771"></span>


## Audio Books Formats


Basically audio books can use any of available format for digital audio, however following formats are most common:

<strong>mp3</strong> \- good old MPEG layer 3 is still predominant format for digital audio.  Audio book is usually a directory that contains mp3  files, usually one file per chapter, sometimes split arbitrary to several pieces of same duration. Metadata are in ID3 tags and cover image in either as image file in the directory or as ID3 tag in files.   As this is very informal layout indeed,  it's usage differs for user to user, company to company. Especially ID3 tags are big mess (as intended originally for music, so they have to be re-purposed for audio books)

<strong>m4b</strong> (or <strong>m4a</strong>) -  This is <a href="https://en.wikipedia.org/wiki/MPEG-4_Part_14">MPEG 4</a> container with audio encoded with <a href="https://en.wikipedia.org/wiki/Advanced_Audio_Coding">AAC</a> codec.  This format is used by iTunes (m4b is basically equivalent to m4a, b it there just to stress that it is audio book).  Often m4a/m4b is one big file with chapters information in metadata - chapter name, starts and end - and supportive players (like <a href="https://www.videolan.org/vlc/index.html">VLC</a>) can show list of chapters and let you skip directly to selected chapter. File also contains metadata tags and cover is usually encoded as additional video stream containing just a jpeg image.

<strong>aax</strong> \- this is proprietary format of Audible (Amazon company and biggest player in commercial audio books in English language). Basically it's very similar to m4b - it's MPEG 4 container with AAC LC encoded audio. The main difference is <a href="https://en.wikipedia.org/wiki/Digital_rights_management">DRM</a> protection - the audio stream is encrypted with 4 bytes key, specific for customer who bought the file.  This means that in regular player like VLC you can see metadata, even can start playback, but will not hear anything (and will see lots of decoding error in terminal output). I would say this DRM protection is rather symbolical now, decryption key can be relatively easily recovered.

Other formats like Vorbis, Opus, WMA  are also possible for audio books but much more rare.


## Why Opus?


I tried opus for audio books several years ago. My experiences are summarized in<a href="/opus-audio-codec-for-audio-books-and-more/"> this article</a> and  so far are quite positive. I can see more and more support for opus around and with advancement of <a href="https://en.wikipedia.org/wiki/AOMedia_Video_1">AV1 video codec</a>, where opus is supposed to be it's primarily audio companion, opus will became one of main audio codecs of the future, I believe.

Opus provides very good compression for speech, while retaining good quality.  From my experiences I can use 32kbps or 48kbps bitrates for encoding , while maintaining very good quality of the audio and assuring comfortable listening of the audio books (I'm not such zealous audiophile, I've seen a guy claiming he cannot listen to audio book encoded below 192 kbps in MP3, which I consider rather excessive, if you look into details of audio books for Audible, they are encoded with AAC LC 64kbps with sample rate 22050 Hz - which is fairly comparable to opus 32kpbs with 24kHz sample rate concerning audio quality).

So main opus advantage for me is lower bitrate, which is especially appreciated when streaming audio book to mobile over Internet - it assures continuous playback even in areas with lower data speed and of course can have notable impact on mobile bills. And as I'm no media company, it's enough for me to store in quality suitable for my listening and thus I can also save space on my home server.

Another advantage is that opus is open source,  royalty and patent free, so it can be easily used in any project and we all like open open source, right?


## The Script


There is now better, more advanced Python script script <a href="https://github.com/izderadicka/split_audiobook">here</a>.

I've created bash script to split big audio books into smaller files encoded with opus audio (script is using ffmpeg and ffprobe):


<script src="https://gist.github.com/izderadicka/0efc16bd150d70b7c504ab15f95c11ab.js"></script>



Usage is pretty straightforward ( run with -h to see help). It can split large m4b/m4a files  into smaller files by chapters (if they are defined in metadata) or to files of fixed duration ( half an hour by default). Split files are stored in subdirectory with same name as the original file. Most time consuming is transcoding of audio - so it's done in parallel (number of processes is number of cores). Cover image is also extracted to that directory (if possible). It works also for mp3 and aax (if you provide activation bytes) files.

If you need to convert individual mp3 files without splitting check <a href="https://gist.github.com/izderadicka/0f66a9ee1a2594be1fd27792bbc0a18c">this script</a>.

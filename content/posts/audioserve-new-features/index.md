+++
title = "Audioserve new features"
path = "/audioserve-new-features/"
date = "2019-09-18T14:37:29"
include_in_feeds = true
[extra]
wordpress_id = 2008
kind = "post"
node_key = "2008"
author = "admin"
source_url = "http://zderadicka.eu/audioserve-new-features/"
source_guid = "http://zderadicka.eu/?p=2008"
source_date_gmt = "2019-09-18 13:37:29"
categories = ["Announcement", "Programming"]
tags = ["audio book", "audio streaming"]
+++
I have been working on some new features in <a href="https://github.com/izderadicka/audioserve">audioserve</a> and they are now available in latest releases. In this article I'd like to talk little bit about them and probably later also provide new demo videos, as there has been many changes from last demos.

Summary of new features:


<ul>
<li>Single file audiobooks (m4b) support</li>
<li>Alternative subfolders sorting (recent, alphabetical) and most recent folders list</li>
<li>Folders download in web client</li>
<li>Easier deployment with smaller docker image or static binary</li>
<li>Server config file</li>
<li>Playback sharing/synchronization between clients</li>
</ul>


See below for details.

<span id="more-2008"></span>

First and probably most interesting change was support for single file audiobooks with chapters.  As I have written in <a href="/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/">original article</a>, I prefer audiobooks, which are split into individual chapters, it just makes things easier.  But it's just my preference and many people think differently (including major companies like Audible or Apple) - m4b format is very popular and often one can also see one huge mp3 file for an audiobook. Now we have better support for these - if file contains metadata about chapters, then this file is presented as a "folder" and its chapters as "files" within this folder - so basically you see it as  if this book was split into chapters (by some <a href="/split-large-audiobooks-a-better-way/">utility like this</a>). This split is only virtual, file stays untouched on the disk, but you can see chapters, skip between them etc. Even transcoding works on chapter level here.

But what if big file does not contain metadata about chapters? Then we offer possibility to create parts with same duration (configurable), which are something like chapters. Obviously this approach is not ideal as splits can be in middle of words ( whereas if using <a href="/split-large-audiobooks-a-better-way/">this utility</a> one can at least make splits in silence moments), so this functionality is not optimal. To provide exact split to chapters you can create external chapters metada file quite easily - create simple CSV file with 3 columns - chapter title, start time, end time, name it exactly same as audio file plus  add .chapters suffix and put in same folder beside the file. And you will then have chapters as you want them to be.

Other new feature is list of recently modified folders (according to system `mtime` of folders). It can be useful to see your latest additions to the collection (but frankly spoken it's not as useful as I expected, as `mtime` is also modified on parent folder, whenever you change something in it, so you have many recent entries, some of them less relevant, creation time (birth time)  is not available on many file systems, so this was best alternative I found).  I also added possibility to order subfolders  according to `mtime` (recent first), which I think is bit more useful - you can see most recent books for an author etc.

Also there is now possibility to download whole folder in web client ( as tar archive). Tar was chosen for it's easy structure and universal support. Compression of already compressed audio does not make much difference,  so I though plain old tar would do just fine.

Another work has been done on deployment - I finally managed to make completely static build - so now you can just download binary and run it on any decent modern 64bits linux ( do not forget that you need there also ffmpeg executable - for which you can also <a href="https://johnvansickle.com/ffmpeg/">download fully static build</a>). Or if you know Docker there is <a href="https://cloud.docker.com/u/izderadicka/repository/docker/izderadicka/audioserve">docker image</a>, now improved and smaller (~75MB with ffmpeg already in - consider that fully static build of ffmpeg has 65MB, so it's not that bad), which you can use to test audioserve almost immediately.

Also configuration of the server was improved. As there is now many command line arguments I added support for configuration file (in YAML format) to capture all your local settings (you can easily create your configuration file with `--print-config` option - just set all needed options, then use it to create a default config file for you).

And last but not least there is first version of playback position sharing between clients. It's bit raw, but generally works. I do not use this functionality much, as I listen almost exclusively on Android client, so did not have much time to test it in real live, so I'm interested in any feedback. As audioserve is a simple personal server, it does not have users. Everybody knowing shared secret can use it. For purpose of playback position sharing it introduces notion of the "group" - all devices with same group name will share and see latest playback positions between them. API for playback position is implemented as simple text messages via websocket.

This is approximately how playback  synchronization (or it should be called rather playback continuation) works, either:

a) Click play on an opened file (file must be already in progress, paused), if there is newer position from other device, then dialog pops up offering you to got to that position, or continue with current file. If there are no more recent positions, playback will just continue.

b) or,  in folder choose to show most recent positions ( icon of triangle with circle arrows in web client, or in Android in 3 dot menu  item "Check remote positions".

Playback position on other device must be at least 10 secs from current position to be considered different.

This functionality is not about parallel playback on several devices - it's about pausing playback on one device and continue on the other device.

Some work has been done on Android client  - a list of above mentioned recent folders and subfolders  ordering  is also there and support for playback positions sharing too ( in recently listened  list you will see latest remote position, if it is newer than positions on this client, it also checks for more recent positions, when you start playback in the application, or you can do this check manually in options menu).

Plus sleep timer was made more visible/usable as I'm using it very often ( you can start it from top bar menu with just one click, using your latest settings and there is a floating button to extend or cancel sleep timer).

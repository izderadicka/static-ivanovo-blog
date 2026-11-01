+++
title = "Nice Solution for Recording Screencasts on Linux"
path = "/nice-solution-for-recording-screencasts-on-linux/"
date = "2012-11-01T12:26:12"
include_in_feeds = true
[extra]
wordpress_id = 317
kind = "post"
node_key = "317"
author = "admin"
source_url = "http://zderadicka.eu/nice-solution-for-recording-screencasts-on-linux/"
source_guid = "http://zderadicka.eu/?p=317"
source_date_gmt = "2012-11-01 11:26:12"
[taxonomies]
category = ["Tools"]
tag = ["linux", "video"]
+++
<a href="/wp-content/uploads/camera.jpeg" rel="attachment wp-att-329"><img alt="" class="alignleft wp-image-329" decoding="async" height="98" loading="eager" src="/wp-content/uploads/camera.jpeg" style="margin-right:15px" title="camera" width="67"/></a>Recently I needed to record some screen-cast from Linux desktop.  In past I was using[ gtk-recordmydesktop](http://recordmydesktop.sourceforge.net/about.php), which basically worked well, but I thought  maybe there is something better.   And I have found this combination of two tools <span style="text-decoration: underline;">very useful</span> \-   [Kazam](https://launchpad.net/kazam) (screencaster) and [OpenShot](http://www.openshotvideo.com/) (video editing) . Kazam is easy to use with all basic functions that are needed  (screen area definition, multi-display support, audio source selection) and it supports output into two common formats (MP4, WebM).  When screen-cast is finished Kazam gives you opportunity to open it directly with a video editor - here OpenShot can be used to cut your screen-cast video, add titles etc. and  finalize screen-cast video.  <span id="more-317"></span>
**Kazam screenshot**
<a href="/wp-content/uploads/kazam.png" rel="lightbox[recording1]"><img alt="" class="alignnone size-medium wp-image-320" decoding="async" height="145" loading="lazy" sizes="(max-width: 300px) 100vw, 300px" src="/wp-content/uploads/kazam-300x145.png" srcset="/wp-content/uploads/kazam-300x145.png 300w, /wp-content/uploads/kazam.png 725w" title="kazam" width="300"/></a>

 

**OpenShot screenshot**
<a href="/wp-content/uploads/openshot.png" rel="lightbox[recording2]"><img alt="" class="alignnone size-medium wp-image-321" decoding="async" height="182" loading="lazy" sizes="(max-width: 300px) 100vw, 300px" src="/wp-content/uploads/openshot-300x182.png" srcset="/wp-content/uploads/openshot-300x182.png 300w, /wp-content/uploads/openshot-1024x622.png 1024w, /wp-content/uploads/openshot.png 1440w" title="openshot" width="300"/></a>

 

One more trick can make your screen-cast more appealing -   if you want to highlight  mouse clicks - there is this setting in mouse preferences -  "Show position of pointer when Control key is pressed" -  you can use it to highlight important mouse clicks (clicking mouse and pressing Ctrl together).

<a href="/wp-content/uploads/mouse.png" rel="lightbox[recording3]"><img alt="" class="alignnone size-medium wp-image-324" decoding="async" height="197" loading="lazy" sizes="(max-width: 300px) 100vw, 300px" src="/wp-content/uploads/mouse-300x197.png" srcset="/wp-content/uploads/mouse-300x197.png 300w, /wp-content/uploads/mouse.png 746w" title="mouse" width="300"/></a>

Also I noted that MP4 recorded screen-casts cause some issues when being edited in OpenShot (enormous memory consumption - probably related to this [bug](https://bugs.launchpad.net/ubuntu/+source/openshot/+bug/927755)) - WebM seemed to be OK.

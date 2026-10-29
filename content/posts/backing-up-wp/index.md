+++
title = "Backing Up WP"
path = "/backing-up-wp/"
date = "2012-09-22T20:11:10"
include_in_feeds = true
[extra]
wordpress_id = 100
kind = "post"
node_key = "100"
author = "admin"
source_url = "http://zderadicka.eu/backing-up-wp/"
source_guid = "http://zderadicka.eu/?p=100"
source_date_gmt = "2012-09-22 19:11:10"
categories = ["Admin"]
tags = ["backup", "wordpress"]
+++
<a href="/wp-content/uploads/thumbup.jpeg"><img alt="" class="alignleft size-thumbnail wp-image-101" decoding="async" height="150" loading="eager" sizes="(max-width: 150px) 100vw, 150px" src="/wp-content/uploads/thumbup-150x150.jpeg" srcset="/wp-content/uploads/thumbup-150x150.jpeg 150w, /wp-content/uploads/thumbup.jpeg 225w" title="thumbup" width="150"/></a>When I was starting this site I was looking for a reliable solution to backup the site. I have been looking bit around and found this excellent plugin for WordPress:
<a href="http://wordpress.org/extend/plugins/backwpup/"><strong>BackWPup</strong></a>

This plugin is absolutely awesome, with many features, just mentioning few key ones:


<ul>
<li>You can create backup job, where you can define what tables and what files will be backed up - thus you can basically backup all site, or selectively just critical data</li>
<li>You can store backup file to many locations: locally, to remote server or to many popular cloud services (Amazon S3, DropBox ...) - so the backup  available even when site is completely down.</li>
<li>You can schedule backups with any periodicity  (cron like scheduler) - you can also  run it manually</li>
<li>It works well even in limited hosting environments</li>
</ul>

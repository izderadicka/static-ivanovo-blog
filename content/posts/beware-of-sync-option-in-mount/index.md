+++
title = "Beware of sync option in mount"
path = "/beware-of-sync-option-in-mount/"
date = "2017-10-01T10:22:16"
include_in_feeds = true
[extra]
wordpress_id = 1730
kind = "post"
node_key = "1730"
author = "admin"
source_url = "http://zderadicka.eu/beware-of-sync-option-in-mount/"
source_guid = "http://zderadicka.eu/?p=1730"
source_date_gmt = "2017-10-01 09:22:16"
categories = ["Admin"]
tags = ["linux", "mount", "usb disc"]
+++
By default mount is using async option, which means that  write operations do not wait for final confirmation from the device - they are stored in disc cache and writes are done latter, optimized by disc firmware.  However you can set sync option manually (`  -o sync `), then write operations are synchronous, meaning each block write has to wait for confirmation that it's physically written to the  disc and there is no optimization available.  This can significantly slow down write speed, of which I convinced myself just recently - I backuped  some data to external 2.5" USB 3.0 HD - <strong>slowdown</strong> in this case was almost <strong>1000x</strong>  -  (70kb/s vs 60MB/s   measured by`  rsync --progress `).  How it happened that disc was mounted with sync option? I actually use <a href="https://usbmount.alioth.debian.org/">usbmount</a> to auto-mount disks and it has sync as default mount option (fortunately can be changed in it's configuration). So conclusion is - don't use sync  option unless you know exactly what you are doing and if write speed is suspiciously slow check mount options.

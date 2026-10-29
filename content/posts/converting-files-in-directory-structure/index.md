+++
title = "Converting files in directory structure"
path = "/converting-files-in-directory-structure/"
date = "2013-08-16T07:43:44"
include_in_feeds = true
[extra]
wordpress_id = 608
kind = "post"
node_key = "608"
author = "admin"
source_url = "http://zderadicka.eu/converting-files-in-directory-structure/"
source_guid = "http://zderadicka.eu/?p=608"
source_date_gmt = "2013-08-16 06:43:44"
categories = ["Admin"]
tags = ["bash", "linux"]
+++
Often I needed to convert a set of files (audio files to different format,  text files to different encoding, ...)  in some directory structure and save results to a  new destination while retaining directory structure.   In order to walk through directory structure we can use `find` command,   but if we are to create output in new place, subdirectories have to be created, which is where `find` command line gets bit complicated (especially if we have to consider spaces in files/directories names).   So here is an example for converting text files encoding:


```sh
find . -name "*.txt" -exec bash -c 'mkdir -p "/dest-dir/`dirname "{}"`"; iconv -f utf-8 -t windows-1250 -o "/dest-dir/{}" "{}"' \;
```

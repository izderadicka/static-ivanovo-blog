+++
title = "Simple statistics from nginx access logs"
path = "/simple-statistics-from-nginx-access-logs/"
date = "2014-11-13T09:13:17"
include_in_feeds = true
[extra]
wordpress_id = 942
kind = "post"
node_key = "942"
author = "admin"
source_url = "http://zderadicka.eu/simple-statistics-from-nginx-access-logs/"
source_guid = "http://zderadicka.eu/?p=942"
source_date_gmt = "2014-11-13 08:13:17"
[taxonomies]
category = ["Admin"]
tag = ["bash", "web server logs"]
+++
I required some simple statistics (selected page visits per day)  from web-server logs.   I looked at some web log analyzer packages like [AWStats,](http://www.awstats.org/) but it looked to me like as an overkill in my case - I'd probably spent more time to trying make it work then putting together some small script. So here it is - a simple bash script that will take all available access logs (by default on Debian nginx is using logrotate to rotate logs daily and keeps 52 daily logs, old logs are gzipped) and calculate page visits for certain request pattern:<span id="more-942"></span>


```sh
#!/bin/bash

BASE_FILE=/var/log/nginx/access.log
OUTPUT=/tmp/pdf-checker-tmp/stats.txt

echo -e "DATE\tVOLUME" > $OUTPUT

COUNT=52

for ((i=1;i<=$COUNT;++i)) 
do 

FILE=$BASE_FILE.$i

if [ -f $FILE ] ; then
#echo "Uncompressed file $FILE"
LISTER="cat $FILE"
elif [ -f $FILE.gz ] ; then
#echo "Compressed file $FILE.gz"
LISTER="gunzip -c $FILE.gz"
fi
if [ -n "$LISTER" ] ; then
DATE=`$LISTER | head -1 | grep -oP "\d{1,2}/\w{3}/\d{4}"`
#echo "From date $DATE"
VOL=`$LISTER | awk -F\" '($2 ~ "POST /upload "){print $2}' | wc -l` 
echo -e "$DATE\t$VOL" >> $OUTPUT
fi
done

```


This script illustrates power of shell programming. Script is scheduled in cron to run daily after log rotate job and the output file is stored in web server directory for static files.

Sample of script output:


```sh
DATE	VOLUME
12/Nov/2014	62
11/Nov/2014	55
10/Nov/2014	62
09/Nov/2014	0
08/Nov/2014	0
07/Nov/2014	60
06/Nov/2014	70
```

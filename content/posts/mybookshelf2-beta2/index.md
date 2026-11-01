+++
title = "MyBookshelf2 Beta2"
path = "/mybookshelf2-beta2/"
date = "2017-11-07T09:38:22"
include_in_feeds = true
[extra]
wordpress_id = 1784
kind = "post"
node_key = "1784"
author = "admin"
source_url = "http://zderadicka.eu/mybookshelf2-beta2/"
source_guid = "http://zderadicka.eu/?p=1784"
source_date_gmt = "2017-11-07 08:38:22"
[taxonomies]
category = ["Uncategorized"]
+++
[MyBookshelf2](/projects/python/mybookshelf2-ebooks-management-and-sharing/) \- ebooks management and sharing solution moved to next version - Beta 2 - apart of few small fixes, the main change is an internal revamp to make it compatible with latest [Asexor ](/run-and-monitor-tasks-via-websocket-with-asexor/)and thus removing dependence on[ Crossbar.io](https://crossbar.io/) and [Autobahn library](https://crossbar.io/autobahn/).  It makes deployment of MyBookshelf2 easier and removes components that did not add much value to the solution, just made it bit overcomplicated.  Some effort was given to provide easy implementation in [Docker](https://www.docker.com/) \- now there is a script that will guide you through two pre-configured scenarios - development (local code, monitoring of code changes) and stage (code in a volume, JS client built and packed, app server running behind [nginx](https://www.nginx.com/) proxy with SSL termination, nginx serving static content).

Check latest code on [github](https://github.com/izderadicka/mybookshelf2). To give it a try just clone repo and run init.sh script in deploy directory (assuming you have [Docker](https://www.docker.com/) installed).

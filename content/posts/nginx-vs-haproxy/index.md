+++
title = "nginx vs haproxy "
path = "/nginx-vs-haproxy/"
date = "2013-11-28T10:37:01"
include_in_feeds = true
[extra]
wordpress_id = 680
kind = "post"
node_key = "680"
author = "admin"
source_url = "http://zderadicka.eu/nginx-vs-haproxy/"
source_guid = "http://zderadicka.eu/?p=680"
source_date_gmt = "2013-11-28 09:37:01"
[taxonomies]
category = ["Admin"]
tag = ["load balancer", "proxy"]
+++
I have been using [haproxy](http://haproxy.1wt.eu/) as front-end reverse proxy and load balancer for one project for several years and I've been very happy with it's stability and performance (although actual load  was always very moderate).   In another (more recent) project I decide to try [nginx](http://nginx.org/en/) in a similar role (but actually I needed also to serve some static files, which was actual reason to try nginx).<span id="more-680"></span>

In nginx I appreciated clean and easy to understood configuration file (although HAProxy config file is not difficult,  somehow nginx config  seems to me more convenient, also config documentation easier to navigate in) .

SSL termination is very easy to set up in nginx (but new development version 1.5 of HAProxy also have   SSL termination now,   but version we used  still does not have it - so we used [stunnel](https://www.stunnel.org/index.html) to terminate SSL, however stunnel had to be patched to support  X-Forwarded-Proto, which is easy to set in nginx).

In my recent scenario I used nginx for both static content serving and as reverse/proxy   -   this is quite convenient for small /mid size projects, because HAproxy is not serving static content.  nginx can also provide some caching of backend responses(which I hope I can also leverage to some extent). I believe such caching  is not possible in HAproxy.

On the other hand advanced load balancing features( dynamic configuration,   status page,  advanced load balancing algorithms,   session affinity (via special cookies),   backend servers status polling etc.)    are either only in commercial version of nginx or not available yet.   So HAproxy still has notable advantages, when it is about load balancing only.

Both my projects do no have huge traffic, so  I cannot comment on performance from my direct experiences -   from what I read nginx and HAproxy should be comparable in performance, both are based on event based asynchronous processing.

Conclusion - nginx can be nice and convenient solution, especially when one can leverage more of it's functions together,   but HAproxy can offer more when one looks for advanced load balancing.

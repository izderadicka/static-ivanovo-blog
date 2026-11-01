+++
title = "Audioserve demo on Heroku"
path = "/audioserve-demo-on-heroku/"
date = "2019-01-04T17:41:17"
include_in_feeds = true
[extra]
wordpress_id = 1982
kind = "post"
node_key = "1982"
author = "admin"
source_url = "http://zderadicka.eu/audioserve-demo-on-heroku/"
source_guid = "http://zderadicka.eu/?p=1982"
source_date_gmt = "2019-01-04 16:41:17"
[taxonomies]
category = ["Uncategorized"]
+++
I've used free account on Heroku to load there audioserve live demo (with few of my favorite audio books from [librivox](https://librivox.org/)). It's fairly easy to implement a docker image on Heroku (just needed to assure that it uses PORT env. variable to bind HTTP listener to this port and to assure that container can run under arbitrary non-root user). See links below if you want to test.<span id="more-1982"></span>

Now new demo site[ https://audioserve.zderadicka.eu/](https://audioserve.zderadicka.eu/)   - shared secret is mypass.

(Still works but use above link  <a href="https://audioserve.herokuapp.com/" rel="noopener noreferrer" target="_blank">https://audioserve.herokuapp.com/</a>   shared secret is mypass)

You  can also test Android application here (with one "small" issue that you cannot hear audio:-): [https://appetize.io/app/khce2vxmx4trna7xu5q73y011g?device=pixel4&scale=100&orientation=portrait&osVersion=10.0&deviceColor=black](https://appetize.io/app/khce2vxmx4trna7xu5q73y011g?device=pixel4&scale=100&orientation=portrait&osVersion=10.0&deviceColor=black)
set above mentioned server link and share secret in settings.

Bear in mind that both links are for demo purposes only (based on free accounts) so please do not use them extensively. If monthly are consumed they will not work for rest of period.

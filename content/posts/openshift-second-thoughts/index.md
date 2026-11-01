+++
title = "Openshift - Second Thoughts"
path = "/openshift-second-thoughts/"
date = "2016-01-16T17:52:19"
include_in_feeds = true
[extra]
wordpress_id = 1218
kind = "post"
node_key = "1218"
author = "admin"
source_url = "http://zderadicka.eu/openshift-second-thoughts/"
source_guid = "http://zderadicka.eu/?p=1218"
source_date_gmt = "2016-01-16 16:52:19"
[taxonomies]
category = ["Admin", "Programming"]
tag = ["PaaS"]
+++
[Openshift](https://www.openshift.com) Online still remains one of most generous Paas offerings on the market. With 3 free containers it's really good bargain. Recently I've modified  couple of my older applications to run in Openshift ([myplaces](/projects/python/myplaces/) and [iching](/ocaml-ocsigen-i-ching-and-web-applications/)) to run in Openshift.

Previously I've created pretty standard and simple Flask application and deployed it on Openshift. The process was pretty straightforward as described [in this article](/openshift-experiencies/). However now situation was different, because both applications are special.<span id="more-1218"></span>

myplaces is python application in Django, but it requires additional process as backend computational server.  Web process communicates with backend server via [ZMQ](http://zeromq.org/) sockets. Also application requires [web socket](https://en.wikipedia.org/wiki/WebSocket) communication with [socketio](http://socket.io/) messaging ( to update import status), so it cannot run in classical WSGI sever ( rather it runs in [gevent](http://www.gevent.org/) sever).  So I have to use [custom catridge for python](https://github.com/gsterjov/openshift-advanced-python-cartridge).

iching application is written in [OCAML](https://ocaml.org/) and [Ocsigen](http://ocsigen.org/), which not very common technology, so it also required custom cartridge ( I used [this one](https://bitbucket.org/jpathy/ocaml-openshift), but had to [modify it slightly](https://github.com/izderadicka/ocaml-openshift2)).

Generally experience was far from smooth, with quite a few peculiar issues, to name few:


<ul>
<li>python pip install  was not working by default because Openshift is using different repositories ( I have to redirect explicitly to official pypi repos).</li>
<li>start, stop action hooks did not work for python app ( but they do for OCAML one).</li>
<li>Took me some time to realize where to run Django specific tasks like <code>manage.py migrate</code></li>
<li>Deployment behaves differently when it runs as git hook or as enc<code> rhc app deploy</code> command or within ssh shell. (For instance I could not really get lxml installed as part of regular deploy process, but it installed without any problems in ssh shell. For OCAML compilation there were  significant differences between git initiated deployment and deployment via rhc tool - finally I had to use rhc tool to make things work).</li>
<li>Installing of missing development libraries (libpcre in my case) was rather tedious - basically you have to supply script to download source and compile it.</li>
<li>Environment variables like PATH, LD_LIBRARY_PATH, PKG_CONFIG_PATH etc. must be set correctly in all environments - which was not always the case - so I had to fix manually ( for instance custom python cartridge had incorrect LD_LIBRARY_PATH in ssh shell, which caused error when running python).</li>
</ul>


Finally I got both applications running on Openshift, but comparing with Docker (I also made [Docker ](https://www.docker.com/)containers for both applications) it was much harder effort. Probably if I've learned more about Openshift platform, it could have been easier,  but considering that their [future versions](https://www.openshift.org) are abandoning  current model and moving towards Docker containers, it would not worth do dig deeper into Openshift Online technologies, because they are already past now and Docker seems to be the future.

Curious reader can look at source code (with Openshift and  Docker integration) of both applications here: [myplaces](https://github.com/izderadicka/myplaces), [iching](https://github.com/izderadicka/iching).

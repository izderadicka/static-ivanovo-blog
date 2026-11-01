+++
title = "Eclipse Help Browser And Proxy"
path = "/eclipse-help-browser-and-proxy/"
date = "2014-04-09T11:07:29"
include_in_feeds = true
[extra]
wordpress_id = 777
kind = "post"
node_key = "777"
author = "admin"
source_url = "http://zderadicka.eu/eclipse-help-browser-and-proxy/"
source_guid = "http://zderadicka.eu/?p=777"
source_date_gmt = "2014-04-09 10:07:29"
[taxonomies]
category = ["Programming", "Tools"]
tag = ["eclipse", "proxy"]
+++
It's quite pathetic, that HTTP proxies settings are causing problems again and again in various applications - like <a href="/ubuntuone-client-behind-proxy/" title="UbuntuOne client behind proxy">UbuntuOne</a>,  pip ...  Maybe it is just problem for Ubuntu/Linux platforms where proxy settings are in separate places (dconf keys for desktop,  `http_proxy`, `HTTP_PROXY`, `no_proxy` environment variables).

This time it was [Eclipse IDE](http://eclipse.org). Problem here is like this -  Eclipse has proxy settings in Preferences/ General / Network connections - however these settings are not applied to Help Browser (started via Help/Help Contents) -  this browser is using system settings (I believe from dconf key system.proxy in my case),  but not in consistent way -  while browser is fine with subnet entry in system.proxy.ignore-hosts  like 127.0.0.1/8, Eclipse help browser is not,  it just requires server part of url - e.g. just 127.0.0.1).

Also Native option for proxy settings in Eclipse (which are used for updates, plugins install) seems not to work on Linux.

I spent some time to fix this,  another victim to inconsistent proxy handling.

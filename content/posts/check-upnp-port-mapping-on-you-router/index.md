+++
title = "Check UPnP port mapping on you router"
path = "/check-upnp-port-mapping-on-you-router/"
date = "2015-06-02T14:53:47"
include_in_feeds = true
[extra]
wordpress_id = 1034
kind = "post"
node_key = "1034"
author = "admin"
source_url = "http://zderadicka.eu/check-upnp-port-mapping-on-you-router/"
source_guid = "http://zderadicka.eu/?p=1034"
source_date_gmt = "2015-06-02 13:53:47"
categories = ["Admin"]
tags = ["network", "router", "UPnP"]
+++
Most modern SOHO routers (like my Asus) support <a href="http://en.wikipedia.org/wiki/Internet_Gateway_Device_Protocol">UPnP IGDP</a>  or <a href="http://en.wikipedia.org/wiki/NAT_Port_Mapping_Protocol">NAT-PMP</a> protocols to enable hosts on local network to open and map incomming (from WAN) port on router.  While these two are different protocols with different origins, they both serve same purpose, so often they are enabled by a single option in your router configuration ( like in my Asus - there is only one option 'Enable UPnP',  but in fact it enables both protocols).

This automatic incomming port port management is very convenient, however it can cause some security problems  in your local network.  Because normaly  neither UPnP nor NAT-PMP is authenticated, all local subnet is basically trusted, it means that any program can open incomming port, as it needs (including  malware programs).  More detailed description about potential UPnP issues is for instance <a href="http://www.howtogeek.com/122487/htg-explains-is-upnp-a-security-risk/">here.</a><span id="more-1034"></span>

So if you after all decide to enable UPnP on router ( because your children need it for their online games and torrents :-),  how can you check which ports are really opened?  Normaly router ( at least my Asus) - shows only manual mappings - but there is nifty small utility called <a href="https://github.com/kaklakariada/portmapper">PortMapper</a>, written in Java, which can discover router on loacal subnet and show all UPnP and NAT-PMP port mappings, currently opened on your router.  Packed as jar it can be downloaded and run in few minutes.

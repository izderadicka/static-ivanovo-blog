+++
title = "MyPlaces are live!"
path = "/myplaces-are-live/"
date = "2014-01-03T13:19:36"
include_in_feeds = true
[extra]
wordpress_id = 699
kind = "post"
node_key = "699"
author = "admin"
source_url = "http://zderadicka.eu/myplaces-are-live/"
source_guid = "http://zderadicka.eu/?p=699"
source_date_gmt = "2014-01-03 12:19:36"
categories = ["Announcement", "Programming"]
tags = ["Digital Map", "gis", "POIs", "python"]
+++
I put  <a href="/projects/python/myplaces/" title="MyPlaces">MyPlaces</a> live on Internet for a pilot run - it's a new project of mine, I've been playing with it in spare time for last few months.   Live site is at <a href="http://myplaces.zderadicka.eu">http://myplaces.zderadicka.eu</a>.<span id="more-699"></span> (retry couple times if you get 503 error because container might be down)

MyPlaces is a multifaceted project from my perspective:


<ul>
<li>As great fan of  maps and geography I'd like to learn more about GIS and map creation/presentation technologies,   I really enjoyed my experiences with QGIS (as described<a href="/playing-with-maps-qgis-postgis-osm/" title="Playing with maps (QGIS, PostGIS, OSM)"> in this post</a>) and wanted to try something other(web oriented) on my own leveraging existing FOSS technologies.</li>
<li>Wanted to try  new approach to building web applications -  create single page application, where client communicates with server via RESTful API.  Results of my effort in this area are presented separately in <a href="/projects/python/rest2backbone/" title="rest2backbone">rest2backbone</a> module (more about it also <a href="/web-clients-are-getting-thick/" title="Web Clients Are Getting Thick">in this post</a>), which is used in MyPlaces.</li>
<li>Since mobiles starting to be  prevailing devices to access web I wanted to try web application that will look good on mobile, learn bit more about responsive design etc.</li>
<li>Use <a href="/voronoi-diagrams/" title="Voronoi Diagrams">Voronoi diagram</a> to present a set of points on map (not sure why exactly this one was important  - but I was quite fascinated by it, when I discover it some time ago - the simplicity of definition, which gives such nice visual representation, which feels very 'natural').</li>
<li>Using <a href="http://zeromq.org/">ZMQ</a> for interprocess communication.  ZMQ is very nice library and it enables to distribute a task into several processes very easily - some details about how to use ZMQ to create background workers is <a href="/long-running-taks-in-web-appdjango/" title="Long Running Taks in Web App/Django">in this post</a>.</li>
</ul>


This all ended up in current version of MyPlaces, which provides some core functionality to manage and present  Places (POIs = Points of Interest) on the map.   It is all built on Open Source technologies  and uses <a href="http://www.openstreetmap.org">OpenStreetMap</a> services and data for maps so its a small counterweight to dominance of Google Maps in this area.

One of focuses of the first version is support for getting existing collections of places/POIs on-line easily and quickly -   for this purpose MyPlaces provides flexible import function, where  we can use either a generic spreadsheet and import any list of places we already have (spreadsheet should be saved as CSV format and if contains reasonable address details, import process will use geocoding to find locations on the map) or GPX format, which is supported by many navigation tools, so we can export POIs files from them and import to MyPlaces.

Here is demo video of CSV import :



<video controls="" preload="metadata"><source src="/wp-content/uploads/myplaces_import3.mp4" type="video/mp4"/></video>

+++
title = "MyPlaces"
path = "/projects/python/myplaces/"
date = "2014-01-02T15:55:58"
include_in_feeds = false
[extra]
wordpress_id = 692
kind = "page"
node_key = "692"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/myplaces/"
source_guid = "http://zderadicka.eu/?page_id=692"
source_date_gmt = "2014-01-02 14:55:58"
menu_order = 0
parent = "/projects/python/"
+++
MyPlaces is a project that enables to present collections of places (POIs - Points of Interest) on a map.   Project utilizes open map services and data from <a href="http://www.openstreetmap.org">OpenStreetMap</a> project  and builds upon them.   MyPlaces themselves are written in Python leveraging many available open source  packages and libraries.  Postgresql and Postgis are used to store and access data..  This project is a result on my explorations into world of GIS and online maps technologies.

<strong>Current MyPlaces version is running as a free service at <a href="http://myplaces.zderadicka.eu">http://myplaces.zderadicka.eu</a>. </strong>(retry couple times if you get 503 error because container might be down)<strong>
</strong>


## Features


MyPlaces can now:


<ul>
<li>Import Places/POIs from different formats (currently CSV, GPX, GEOJSON)</li>
<li>Export collection to various formats (currently same as import formats)</li>
<li>Browse various collections of places,   provide searches (including some spatial searches)</li>
<li>Visualize places on maps - with various options (clustered, non-clustered, two OSM based base layers)</li>
<li>Edit and maintain collections easily anywhere</li>
<li>MyPlaces are specially designed to provide meaningful access on mobile devices.</li>
<li>All things around to make it a service on Internet - (user accounts,  access control etc.)</li>
<li>Some very special features - like<a href="/voronoi-diagrams/" title="Voronoi Diagrams"> Voronoi diagrams</a> visualization.</li>
<li>Designed for horizontal scalability (can very easily split back-end services into several nodes)</li>
</ul>




## Demos




### Video of basic features of  MyPlaces (mobile layout):




<video controls="" preload="metadata"><source src="/wp-content/uploads/myplaces.mp4" type="video/mp4"/><source src="/wp-content/uploads/myplaces.webm" type="video/webm"/></video>



 

 


<a id="import_video"></a>
### Video of flexible CSV import:




<video controls="" preload="metadata"><source src="/wp-content/uploads/myplaces_import3.mp4" type="video/mp4"/><source src="/wp-content/uploads/myplaces_import3.webm" type="video/webm"/></video>



 


## Download and Source


All source code is <a href="https://github.com/izderadicka/myplaces">available at github</a>.  Check details there for download and installation.
(under BSD license)

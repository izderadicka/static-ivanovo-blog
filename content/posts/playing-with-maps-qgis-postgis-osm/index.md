+++
title = "Playing with maps (QGIS, PostGIS, OSM)"
path = "/playing-with-maps-qgis-postgis-osm/"
date = "2013-06-07T09:53:35"
include_in_feeds = true
[extra]
wordpress_id = 546
kind = "post"
node_key = "546"
author = "admin"
source_url = "http://zderadicka.eu/playing-with-maps-qgis-postgis-osm/"
source_guid = "http://zderadicka.eu/?p=546"
source_date_gmt = "2013-06-07 08:53:35"
categories = ["Tools"]
tags = ["gis", "maps"]
+++
<img alt="" class="alignleft size-full wp-image-549" decoding="async" height="143" loading="eager" src="/wp-content/uploads/map.png" title="map" width="256"/>I do like maps.   Recently  I was looking at some digital maps and  got into more details and found several nice open source tools about which I'd like to write in this article.  As in any area open source provides interesting alternatives to work with digital maps and geographical data and what is also very interesting there are now free sources of  good quality geographical  data, which  can be used freely by everybody to create their own maps.   In this article I'm explaining how use data from Open Street Maps (OSM) project  for creating maps in QGIS and how to use PostGIS to store geographic informations and have  fun playing around with their different features of map data and tools. This tutorial is focused on linux (debian based - ubuntu 12.04 resp. mint in my case) desktop and assumes some basic knowledge of  your linux desktop administration.<span id="more-546"></span>


## Ingredients


Linux desktop  preferred :-) This tutorial is written for  for Ubuntu 12.o4 and its derivatives.

<a href="http://www.postgresql.org/">Postgres</a> 9.1 - great open source RDMBS - actually I did not work with Postgres very much  (rather with Oracle or MySql) and I was very much impressed.

<a href="http://postgis.net/">PostGIS</a> 1.5 - is a geographic extension for Postgres, which enables to store and manipulate spacial data.    As I understood from reading few articles this should be one of most advanced and commonly used solutions around (even with comparison to commercial solutions).

<a href="http://www.qgis.org/">QGIS</a> \- open source GIS program ( GIS = Geographical Information System - system to visualize and analyze geographical data)

<a href="http://www.openstreetmap.org/">OSM</a> \- Open Street Maps - absolutely fantastic project, where thousands of volunteers are mapping our planet. OSM now offers maps  data, which are getting closer to leading commercial maps with respect to level of details and accuracy.  You can freely download their data and use them for any project (where occasional  inaccuracies and omission in maps are not critical).

<code>&#10;</code>


## Install SW


Install postgres 9.1 RDBMS and postgis using apt-get.

Install <a href="http://www.pgadmin.org/">pgadmin</a> III also using apt-get.
pgadmin is a GUI admin tool for postgres - it'll help to you overview and manage DB objects and to run queries.

QGIS - install release from their repository:
`deb     http://qgis.org/debian precise main`
<code>&#10;</code>

Install <a href="http://wiki.openstreetmap.org/wiki/Osm2pgsql">osm2pgsql</a>  from this ppa:kakrueger/openstreetmap
osm2pgsql is a tool to import OSM XML vector data to  PostGIS enabled database.  Although it is possible to work with OSM data directly in QGIS using a plugin, I found it more convenient to have data in a spacial database.   OSM provides tons of data, so database is more flexible and efficient.


## Get Map Data


OSM offers download of all their data in XML format.    But the file is huge (30G compressed), so for purposes of playing with maps it's better to have some extract - like extract of particular country (Czech Republic in my case) - it can be downloaded from <a href="http://download.geofabrik.de/">here</a> for instance.


### Load data into database


First we have to prepare PostGIS database,   osm2pgsql  creates default database called gis, which we can use, or we'll need to create new one (before that I recommend to create user in postgres, named as your linux user and give him all right including superuser - this will make easier to work with the database from command line)

<code>sudo -u postgres createuser -s ivan # this creates new user as superuser&#10;# to enable this user in pgadmin we have to give it pg password like this:  psql and then &#92;password&#10;createdb -O ivan  test&#95;gis</code>
`psql -d test_gis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql`
` psql -d test_gis -f /usr/share/postgresql/9.1/contrib/postgis_comments.sql  `
`psql -d test_gis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql`

Then we can load data into database (have to wait a while - all Czech republic file took me more then hour on Core i5 notebook with 8G memory):

`osm2pgsql -s -C 2000 -U ivan -d test_gis ~/tmp/czech_republic-2013-05-11.osm`


## A Bit  of theory


Before start to play with OSM data the is one important thing to understand - it 's called CRS (Coordinates Reference System) or sometimes SRS (Standard Reference System) -  it basically determines two things:

a) How to model Earth to identify a point on it's surface
Since Earth is not and  ideal sphere, for more precise measurements is has to be modeled as an ellipsoid, bit squeezed over the poles, or even something more complicated. Model of the Earth is also called  <span style="text-decoration: underline;">datum</span>. Most common models of Earth(datums )now are either sphere approximation (used by many online maps including OSM, Google maps ...) or WGS84 (which is an ellipsoid, where polar axis is shorter by about  0.33%)

b) How geographical coordinates (latitude and longitude in particular model/datum) are projected to plane (2 dimensions)  - there are many ways how to do it - most common is cylindrical projection (when cylinder is alongside polar axis it is also called Mercator project). The projection  define how radial geographical coordinates - latitude and longitude are projected to meters (or other distance metric) on the plannar  map

This topic is quite complex and there are over 4000 different CRSes, but to start with there are few most common/useful (CRSes are regitered by authorities, which gives them a registration number, which is then used in programs like QGIS):


<ul>
<li>EPSG:4326 - is using WGS84 datum and simple projection were latitude and longitude are directly used as  2D map coordinates (x=longitude, y= latitude)- this projection is also called plate carree or geographic projection.</li>
<li>EPSG:3857 0r EPSG:900913 - is system used by many on-line maps like OSM or Google,  where datum is an ideal sphere and projection is Mercator (cylindrical).</li>
<li>EPSG:3395 - is using more precise WGS84 datum and Mercator projection.</li>
<li>UTM - there are  series of CRSes based on UTM system - UTM system is using WGS84 datum and cylindrical projection, but cylinder is now orthogonal to polar axis. This means that this projection is useful only for limited longitudes range - so UTM system defines 60 stripes -  each is using a cylindrical projection placed at the middle of   6 degree longitude range (starting for -180).</li>
</ul>




## Rendering map in QGIS


Now when we have map data in the database and we can start to play with them in QGIS.

First we need to add layers to the project -   we can add layers from PostGIS database -   enter the connection information and add all PostGIS enabled tables - each table will create a layer .   Now we  see some kind of map, but it is ugly and messy.    It's because all map elements (also called features) are rendered with default style.   The true art of nice map is in styling - to provide nice and appropriate styles to each map feature.   First let's look at  available data - we have 4 layers containing some interesting data, which are called features of the map.

<strong>planet_osm_point</strong> \-   are various points on map - it can be  points indicating town, villages,  places like restaurants, banks or transport amenities like bus or train stops or many other things.
<strong>planet_osm_line</strong> \-   are lines on the map, which can represent roads, highways, streets but also creeks, trenches etc.
<strong>planet_osm_roads</strong> \- is a subset of planet\_osm\_line containing main roads - this is available as a separate layer for convenient styling - see more about styles later.
<strong>planet_osm_polygon</strong> \- are polygons, closed lines, which can represent borders of countries, states, town,  natural features like lakes, rivers, forest, but also artificial features like buildings, roads etc.

Each layer contains features spacial data (coordinates of points, lines) and also meta-data  to explain what particular feature  represents (is it road?, what type of road,  road number, ...)

QGIS enables us to  style each layer with rules that relates to meta-data of features  - so we can have one style for small roads, another for main roads,  a style to polygons representing lake, another style for forest and so on.    For more accurate styling it is better to separate similar features to separate layer - this can be easily done in QGIS because layer is actually a select query to database.   Also selection of layer features for particular styling rule is a select query - so there is great flexibility in selecting features for styling.

To style a layer  we have to go to the layer properties (double click layer or right click and select Properties) and set Style to 'Rule based'. Here we can add styles for particular features classes.  Or we can load existing style.  I have some sample styles ( <a href="/wp-content/uploads/my_styles.zip">my_styles) </a> for OSM data  (roads.qml should be applied on both roads and line layers).   One note about labels -  QGIS has new label styling engine, which is not on layer properties window. We can access it separately via toolbar - "Labeling".

With these styles we have already quite nice looking map,   but there is more.  There are  other sources  of  free geographical data - for instance elevation profile provided by NASA satellites, we will speak about it in the next chapter.

 


##   Adding 3rd dimension


NASA provides free dataset called ASTER GDEM 2 containing satellite measurements of ground elevation of the Earth surface. Data are provided by tiles one degree by one degree containing grid of cells of app. 30  meters size .  Data are provided in GeoTiff format, size of one tile is app. 25MB uncompressed (5MB compressed). Data can be downloaded from<a href="https://lpdaac.usgs.gov/products/aster_products_table/astgtm"> this site</a>.

We load data (\*\_dem.tif) to our project using "Add Raster Layer" button in the toolbar.   Since this data are using latitude and longitude as coordinates, it's useful to edit project properties (In File menu, or click CRS icon in bottom-right corner) and set "Enable on fly CRS transformation" - thus we  see all layers in the right positions.

With elevation data we can:


<ul>
<li>See color map of elevation
By default we  see this layer asa  gray color - if we open layer properties and set Style /Colormap Style to Colormap and define our own colormap (just set number of entries in the map and click classify, also we can change Color Interpolation), which  displays elevations in different colors.
More advanced colormaps can be created by Raster/Analysis/DEM (Terrain models)/Color relief or plugins.</li>
<li>Create shaded hills layer
We can add shaded hills layer by using menu Raster/Analysis/DEM (Terrain models)/Hillshade   - this will create another raster layer, with hills shaded to grey colors - for better combination with other layers we set transparency of this layer to ~ 90%.</li>
<li>Create contours layer (vector layer with lines of same elevation)
Using Raster/Extraction/Contours we can extract terrain contours into new vector layer.  For this layer we set the style to make contours look nice on the map ( here is sample style for contours - <a href="/wp-content/uploads/contours.qml_.zip">contours.qml</a>).</li>
</ul>


And  finally here is an example how such map  looks like:

<a href="/wp-content/uploads/cernosice.png"><img alt="" class="alignleft size-medium wp-image-574" decoding="async" height="199" loading="lazy" sizes="(max-width: 300px) 100vw, 300px" src="/wp-content/uploads/cernosice-300x199.png" srcset="/wp-content/uploads/cernosice-300x199.png 300w, /wp-content/uploads/cernosice-1024x679.png 1024w, /wp-content/uploads/cernosice.png 1134w" title="cernosice" width="300"/></a>

 

 

 

 

 

 

 


## Displaying custom data


We can display also some other data on the map - for instance, if we have a set of places with their postal address we can use geocoding services (the is a nice python library <a href="http://code.google.com/p/geopy/">geopy</a>, wrapping most common services)  to acquire their locations and display them on a map - here is an example showing all breweries in Czech Republic:

<a href="/wp-content/uploads/pivovary.png"><img alt="" class="alignleft size-medium wp-image-575" decoding="async" height="199" loading="lazy" sizes="(max-width: 300px) 100vw, 300px" src="/wp-content/uploads/pivovary-300x199.png" srcset="/wp-content/uploads/pivovary-300x199.png 300w, /wp-content/uploads/pivovary-1024x679.png 1024w, /wp-content/uploads/pivovary.png 1134w" title="pivovary" width="300"/></a>

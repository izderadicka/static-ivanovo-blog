+++
title = "Oracle Application Express and PL/SQL"
path = "/projects/oracle-application-express-and-plsql/"
date = "2012-09-26T11:50:52"
include_in_feeds = false
[extra]
wordpress_id = 159
kind = "page"
node_key = "159"
author = "admin"
source_url = "http://zderadicka.eu/projects/oracle-application-express-and-plsql/"
source_guid = "http://zderadicka.eu/?page_id=159"
source_date_gmt = "2012-09-26 10:50:52"
menu_order = 0
parent = "/projects/"
+++
Recently I've  used <a href="http://apex.oracle.com/i/index.html">Oracle Application Express</a> recently for several commercial projects.  Application Express (short name Apex) is RAD development environment for Oracle 11 database.  It has quite comprehensive visual development environment,  where you can build quickly web application based on some tables.  Internally all Apex is written in PL/SQL (So I have to refresh this language little bit ). As any visual environment, there is a lot of clicking, when working with Apex,   easy things are really easy,  more complicated things might get pretty hard, because one has to know how Apex works in details (which for more advanced/complex things is not well documented) to be able to extend it or modify it.   But in general I would say that Apex has fair level of extensibility to do   every very special things. The main mechanisms for extensibility of APEX are:


<ul>
<li><strong>Page Processes</strong> - where you can write custom PL/SQL, which will process submitted data, or influence page rendering.</li>
<li><strong>Authorisation/Authentication Schemes</strong> - where you can define completely customized access to application - again programming is done in PL/SQL</li>
<li><strong>Plugins</strong> - here one can design completely customizes widgets for pages (using PL/SQL on server side and Javascript +JQuery on client side) or also custom processes, that could be plugged into application.</li>
</ul>


My Apex projects are internal, so there are  no means in sharing them, but I can share some plugins and sniplets, that can be useful to others.   I'll also publish some blog post about some interesting aspects of Apex development I've encountered.


### Plugins:


<strong><a href="/wp-content/uploads/select.png" rel="lightbox[multiselect]"><img alt="" class="alignleft wp-image-168" decoding="async" height="106" loading="eager" sizes="(max-width: 322px) 100vw, 322px" src="/wp-content/uploads/select.png" srcset="/wp-content/uploads/select.png 402w, /wp-content/uploads/select-300x98.png 300w" title="select" width="322"/></a><a href="http://www.apex-plugin.com/oracle-apex-plugins/item-plugin/multiselect-item_225.html">MultiSelect Item</a></strong> \- multiselect list is always challenge for usability. The default one provided by browser is problematic in almost all use cases.  So there are many more replacements available around.   I used one JQuery plugin, which seemed to be good for my usecase and created Apex Item plugin for it.  Particular challenge was to make it work good in Apex framework - especially to enable cascading LOV -   I did not found anywhere good description of how to do it - so I think I'll post an article here about my experiences.

 

<a href="/wp-content/uploads/gantt-chart.png" rel="lightbox[gantt]"><img alt="" class="alignleft wp-image-458" decoding="async" height="30%" loading="lazy" sizes="(max-width: 1410px) 100vw, 1410px" src="/wp-content/uploads/gantt-chart.png" srcset="/wp-content/uploads/gantt-chart.png 1410w, /wp-content/uploads/gantt-chart-300x88.png 300w, /wp-content/uploads/gantt-chart-1024x302.png 1024w" style="margin-right: 15px;" title="gantt-chart" width="30%"/></a> <a href="http://www.apex-plugin.com/oracle-apex-plugins/region-plugin/gantt-chart_242.html">Gantt Chart</a> plugin is based on an existing <a href="http://taitems.github.com/jQuery.Gantt/">jQuery plugin</a>,  however this plugin is patched significantly to work for my use-case (scale hours and days,  limited by dates in page items).
This region plugin will display Gantt like chart for data supplied in a query. The chart is interactive - can display tooltips on individual bars, can be zoomed,  scrolled, and can have dynamic actions assigned to click action on a bar or outside of  bars (to add or edit tasks).

To work correctly user db session and browser should have same TZ (otherwise chart bars are moved - actually displayed according to browser TZ) - so use auto-timezone application setting or something more sophisticated . Also assure that date ranges displayed are 'reasonable' -   for too wide range script will block ( much more then is displayed on screen) ,   for too small it'll display nonsence (less then day, or only few days on day scale)
Licensed by either MIT or GPL v3 license.

 

<a href="/wp-content/uploads/options_map.png" rel="lightbox[options]"><img alt="" class="alignleft wp-image-462" decoding="async" height="191" loading="lazy" sizes="(max-width: 377px) 100vw, 377px" src="/wp-content/uploads/options_map.png" srcset="/wp-content/uploads/options_map.png 629w, /wp-content/uploads/options_map-300x152.png 300w" title="options_map" width="377"/></a><a href="http://www.apex-plugin.com/oracle-apex-plugins/item-plugin/options-map_243.html">Options Map</a> item plugin is useful when user has to choose from large amount of options, which are hierarchically organized.   When one level is chosen, it hides all children, because they are considered to be included in this choice. We used this item for regional coverage, for instance.
This plugin uses data from a table which must contain following columns: ID of the options, name of the options and ID of parent options.
It takes some space on screen (which was design intent), but then user has relatively easy way how to choose all relevant   options.
It is designed as well behaving APEX item, so can be used as read only, disabled, hidden etc.
Credits to my colleague Martin Pokorny for an idea how this item plugin  should look like.

+++
title = "Web Clients Are Getting Thick"
path = "/web-clients-are-getting-thick/"
date = "2013-10-15T09:47:59"
include_in_feeds = true
[extra]
wordpress_id = 637
kind = "post"
node_key = "637"
author = "admin"
source_url = "http://zderadicka.eu/web-clients-are-getting-thick/"
source_guid = "http://zderadicka.eu/?p=637"
source_date_gmt = "2013-10-15 08:47:59"
categories = ["Programming", "Web Design"]
tags = ["django", "Javascript", "python", "RESTful"]
+++
Remembering days when client-server rules the world, then days when everybody praised light web clients where all user interface (UI) was prepared on web server and any user action was communicated back to server (this could lead to heavy network traffic - I've seen one mainstream ERP  program, where a change in one input, say line item quantity,  lead to several megabytes being sent over network).  I'm quite amused to see how we're returning back to thick clients and passing  more and more UI tasks back to user devices.   This probably make sense, taking into account the computing power available in user devices now (my mobile has approximately same computing power (dual core 1.2 GHz ARM CPU)  as  a reasonable  server  ten years back(Sun V240 for instance)) and  improvement of web browsers and especially their Javascript engines.   Normally utilization on an average client machine would be very low, unless client is dealing with digital media, so using  available computing  power there  is an obvious step. Network bandwidth could be now  more precious resource then client  computing cycles.<span id="more-637"></span>

Working on a small project of mine  I tried to catch up with  web user interface 'state of the art',  as per my understanding it looks like this:


<ul>
<li>On servers side splits to static and dynamic content:
<ul>
<li>static content is served via  proven web servers like apache, ngix - on global scale this task might be delegated to <a href="http://en.wikipedia.org/wiki/Content_delivery_network">CDN</a>  providers.</li>
<li>dynamic content is available via Web Services API -   now most common is <a href="http://en.wikipedia.org/wiki/Representational_state_transfer#RESTful_web_APIs">RESTful</a> API with <a href="http://www.json.org/">JSON</a> as data serialization format (with XML often as an alternative, but more complicated technologies like <a href="http://en.wikipedia.org/wiki/SOAP">SOAP</a>/<a href="http://en.wikipedia.org/wiki/Web_Services_Description_Language">WSDL</a> seem to be disappearing) .</li>
</ul>
</li>
<li>On client side Javascript  renders UI - static HTML is only skeletal -   Javascript is  getting data via RESTful API as needed and displays them using client side templates.    Web client usually utilizes existing JS libraries to get help  with its work  - either to create UI elements and manipulate dynamically page <a href="http://en.wikipedia.org/wiki/Document_Object_Model">DOM</a> , to consume  RESTful API, or to organize code.    Quite popular are <a href="http://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller">MVC</a> frameworks (like <a href="http://backbonejs.org/">Backbone.js</a>),   which help to organize code into logical components, thus keeping code manageable even for quite complex UIs.</li>
</ul>


This approach leads to so called "<a href="http://en.wikipedia.org/wiki/Single-page_application">single-page applications</a>" -   where everything (HTML, HTML Templates, Scripts, CSS, Initial Data) is loaded with first page, page is then modified by Javascript based on user actions,   later server provides only additional data  via API calls. Conceptually it's now quite close to desktop application  - with views. models, events in views etc.

Following diagram summarizes idea of single page application:

<a href="/wp-content/uploads/thick_web_client.png"><img alt="thick_web_client" class="alignnone size-large wp-image-651" decoding="async" height="240" loading="eager" sizes="(max-width: 640px) 100vw, 640px" src="/wp-content/uploads/thick_web_client-1024x384.png" srcset="/wp-content/uploads/thick_web_client-1024x384.png 1024w, /wp-content/uploads/thick_web_client-300x112.png 300w, /wp-content/uploads/thick_web_client.png 1090w" width="640"/></a>

I wanted to try this new paradigm with <a href="https://www.djangoproject.com/">Django</a> framework, which is more oriented to classic multi-page web applications, but has so many good features, that I hoped it can serve me well also in this case.

First I needed to provide RESTful API -  simple approach would be to use Django views to return JSON,   but for more complex approach some framework would be useful -  luckily there are several RESTful frameworks for Django - these two seems to be most prominent:  <a href="http://django-rest-framework.org/"> django-rest-framework</a>  and<a href="http://tastypieapi.org/"> django-tastypie</a>

I've chosen django-rest-framework,   it's very well documented and based on  well-know Django technologies -  forms and views -   resources here are defined as a combination of serializers (which are defined in a way similar to Django forms) and views (which bind serialized data to HTTP methods). Django-rest-framework understands Django  models so it is easy to create an API from existing models.  Django-rest-framework also provides nice way to access API from web browser, so you can test it and play with it.

Once having the API on server side I started to work on client -   I decided to try <a href="http://backbonejs.org/">Backbone.js </a>with support of <a href="http://jquery.com/">JQuery</a> (for AJAX and DOM manipulation).   Backbone has shown to be very well though-out MVC framework, which really helped me  to organize Javascript code in a nice way.  First I had to describe  models (that represents resources from the server). But it  was actually  a duplication of work already done in Django - each model needed  url,  fields,  data types, validation, etc. , which was available for corresponding resources on server. This lead me to an idea of an additional small framework  that generates models (and possibly some other useful things)   from resources definitions in Django and makes them available as Javascript to clients -  the idea was realized in <a href="/projects/python/rest2backbone/" title="rest2backbone">rest2backbone</a> project, which can help with RESTful client development - it provides ready to use models for Backbone.js,  also templates to display models and some additional support for creating views.

With <a href="/projects/python/rest2backbone/" title="rest2backbone">rest2backbone</a> creating an application  became easy,      <a href="/projects/python/rest2backbone/" title="rest2backbone">rest2backbone</a> contains sample application,  based on data model (author/publisher/book) from Django documentation.  The actual work focused mainly on skeleton HTML for application main page,   templates and views  to display 'expandable list of items', Backbone.js router code to transition between views  and a bit of Javascript code to tight it all together.   Below is the screenshot of sample application available in <a href="/projects/python/rest2backbone/" title="rest2backbone">rest2backbone</a>:

<a href="/wp-content/uploads/rest-sample.png"><img alt="rest-sample" class="alignnone size-large wp-image-649" decoding="async" height="386" loading="lazy" sizes="(max-width: 640px) 100vw, 640px" src="/wp-content/uploads/rest-sample-1024x618.png" srcset="/wp-content/uploads/rest-sample-1024x618.png 1024w, /wp-content/uploads/rest-sample-300x181.png 300w, /wp-content/uploads/rest-sample.png 1047w" width="640"/></a>

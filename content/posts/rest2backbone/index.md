+++
title = "rest2backbone"
path = "/projects/python/rest2backbone/"
date = "2013-09-24T09:45:51"
include_in_feeds = false
[extra]
wordpress_id = 631
kind = "page"
node_key = "631"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/rest2backbone/"
source_guid = "http://zderadicka.eu/?page_id=631"
source_date_gmt = "2013-09-24 08:45:51"
menu_order = 0
parent = "/projects/python/"
+++
<strong>rest2backbone</strong> can help to quickly build a web browser interface for <a href="http://en.wikipedia.org/wiki/Representational_state_transfer#RESTful_web_APIs">RESTful</a> API in <a href="https://docs.djangoproject.com">Django.</a>  It's achieved by connecting two notable components <a href="http://django-rest-framework.org">Django REST Framework</a> on server side and <a href="http://backbonejs.org">Backbone.js</a> on client side.   Django REST Framework enables us to quickly define RESTful API from existing Django models, we just need to create few classes in a similar way, how Django forms classes are defined.  Backbone.js is a MVC framework that can consume server RESTful API and provide us with Models and Collections in Javascript.  Also bring additional level of order into client JS code, forcing us to put data into models,   use views and templates, and providing a controller/router for single page applications.

However to use these two together we have to duplicate a significant amount of code between definitions of models in Python and definitions of models in Javascript.  Also for models we have to create  forms to display and update models, validate forms for correct values etc.  rest2backbone tries to minimize this duplication and generate as much JS and HTML code  as it can - so we can focus on client logic mostly.


## Features


rest2backbone can generate for you:


<ul>
<li>models, collections and index for all resources available via API (  index is a 2 columns collection with id and string representation of the model -  useful  for dynamic selects, auto-completes etc.</li>
<li>support for  validation of models (as per definitions of models in Django -  types, limits, formats ...), filtering, ordering and pagination of collections.</li>
<li>form templates for given models, including some code to save form data into model and display validation errors on the form.</li>
<li>some extensions to Django REST Framework - like HTML 5 input types, viewset with indexes, ...</li>
<li>Dynamic widgets -   contains small framework for dynamic widgets to be used in in form templates - includes dynamic select (refreshes from models index) and in place edit (edits related model in place - in parent form).</li>
<li>it uses Django internationalization framework - so no problem to use in several languages</li>
</ul>


rest2backbone is now rather small (I'd say a proof of concept),   but I hope it may grow as I'll use it in my other projects and maybe somebody else will find it useful and will contribute.


## Quick Start


You can quickly build a modern one page web application in few steps:


<ol>
<li>Create your models in Django, if necessary add additional logic to them etc.</li>
<li>Create a RESTFul API - as described in <a href="http://django-rest-framework.org/tutorial/quickstart.html">Django REST Framework documentation</a>    - I prefer to put these definitions in resources.py module.    We provide modified <code>ModelSerializer</code> and <code>ViewSetWithIndex</code> in <code>rest2backbone.resources</code>  - so use these  (see sample_app/<a href="https://github.com/izderadicka/rest2backbone/blob/master/sample_app/resources.py">resources.py</a>) .</li>
<li>Link API ViewSets to urls via modified router :
<pre class="code-highlight" data-language="python"><code><span class="code-line"><span class="kn">from</span> <span class="nn">rest2backbone.resources</span> <span class="kn">import</span> <span class="n">IndexedRouter</span></span>&#10;<span class="code-line"><span class="n">router</span><span class="o">=</span><span class="n">IndexedRouter</span><span class="p">(</span><span class="n">trailing_slash</span><span class="o">=</span><span class="kc">False</span><span class="p">)</span></span></code></pre>
This is our modified router, which can also provide indexes.   It's very important that it's initialized with <code>trailing&#95;slash=False</code> because Backbone is expecting it.
Then register any model ViewSets created earlier with <code>register</code> function, and finally link router's  urls to <code>urlspatterns</code> :
<pre class="code-highlight" data-language="python"><code><span class="code-line"><span class="c1"># add to  urlpatterns  list</span></span>&#10;<span class="code-line"><span class="n">url</span><span class="p">(</span><span class="sa">r</span><span class="s1">&#39;^api/&#39;</span><span class="p">,</span> <span class="n">include</span><span class="p">(</span><span class="n">router</span><span class="o">.</span><span class="n">urls</span><span class="p">)),</span></span>&#10;<span class="code-line"><span class="c1">#needed by rest_framework for browsable API</span></span>&#10;<span class="code-line"><span class="n">url</span><span class="p">(</span><span class="sa">r</span><span class="s1">&#39;^api-auth/&#39;</span><span class="p">,</span> <span class="n">include</span><span class="p">(</span><span class="s1">&#39;rest_framework.urls&#39;</span><span class="p">,</span></span>&#10;<span class="code-line">                               <span class="n">namespace</span><span class="o">=</span><span class="s1">&#39;rest_framework&#39;</span><span class="p">)),</span></span></code></pre>
</li>
<li>Add also an url for generated  javascript models ( it uses router to generate JS models for all registered ViewSets):
<pre class="code-highlight" data-language="python"><code><span class="code-line"><span class="kn">from</span> <span class="nn">rest2backbone.views</span> <span class="kn">import</span> <span class="n">restApi</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="c1">#add to urlpatterns list</span></span>&#10;<span class="code-line"><span class="n">url</span><span class="p">(</span><span class="sa">r</span><span class="s1">&#39;^js-restAPI/?$&#39;</span><span class="p">,</span> <span class="n">restApi</span><span class="o">.</span><span class="n">as_view</span><span class="p">(),</span> <span class="p">&#123;</span><span class="s1">&#39;router&#39;</span><span class="p">:</span> <span class="n">router</span><span class="p">,</span> <span class="s1">&#39;url_prefix&#39;</span><span class="p">:</span><span class="s1">&#39;/api&#39;</span><span class="p">},</span> <span class="n">name</span><span class="o">=</span><span class="s1">&#39;rest-api&#39;</span><span class="p">),</span></span></code></pre>
In Javascript code models are availabe under global object <code>restAPI</code> -   restAPI.<span style="color: #c0c0c0;">YourModelName</span> and restAPI.<span style="color: #c0c0c0;">YourModelName</span>List - for collection and restAPI.<span style="color: #c0c0c0;">YourModelName</span>Index - for index</li>
<li>Create  HTML template page for your application,   it should contain following script references  in the header:
<pre class="code-highlight" data-language="html"><code><span class="code-line"><span class="p">&lt;</span><span class="nt">script</span> <span class="na">src</span><span class="o">=</span><span class="s">&quot;&#123;&#123;STATIC_URL}}js/jquery-2.0.2.js&quot;</span><span class="p">&gt;&lt;/</span><span class="nt">script</span><span class="p">&gt;</span></span>&#10;<span class="code-line"><span class="p">&lt;</span><span class="nt">script</span>  <span class="na">src</span><span class="o">=</span><span class="s">&quot;&#123;% url &#39;django.views.i18n.javascript_catalog&#39;  packages=&#39;rest2backbone&#39;%}&quot;</span><span class="p">&gt;&lt;/</span><span class="nt">script</span><span class="p">&gt;</span></span>&#10;<span class="code-line"><span class="p">&lt;</span><span class="nt">script</span>  <span class="na">src</span><span class="o">=</span><span class="s">&quot;&#123;&#123;STATIC_URL}}js/underscore-min.js&quot;</span><span class="p">&gt;&lt;/</span><span class="nt">script</span><span class="p">&gt;</span></span>&#10;<span class="code-line"><span class="p">&lt;</span><span class="nt">script</span>  <span class="na">src</span><span class="o">=</span><span class="s">&quot;&#123;&#123;STATIC_URL}}js/backbone-min.js&quot;</span><span class="p">&gt;&lt;/</span><span class="nt">script</span><span class="p">&gt;</span></span>&#10;<span class="code-line"><span class="p">&lt;</span><span class="nt">script</span> <span class="na">src</span><span class="o">=</span><span class="s">&quot;&#123;% url &#39;rest-api&#39; %}&quot;</span><span class="p">&gt;&lt;/</span><span class="nt">script</span><span class="p">&gt;</span></span>&#10;<span class="code-line"><span class="p">&lt;</span><span class="nt">script</span>  <span class="na">src</span><span class="o">=</span><span class="s">&quot;&#123;&#123;STATIC_URL}}js/api-forms.js&quot;</span><span class="p">&gt;&lt;/</span><span class="nt">script</span><span class="p">&gt;</span></span></code></pre>
Note Django localization JS library  - it's needed to provide global <code>gettext</code> function, which localizes strings in JS - mostly validation errors.
And also put somewhere in the body this :
<pre class="code-highlight" data-language="html"><code><span class="code-line"><span class="cm">&lt;!-- Templates generated by rest2backbone --&gt;</span></span>&#10;<span class="code-line">&#123;&#123;params.forms.render_all}}</span></code></pre>
It generates  form templates for registered models.
You also have to link your application template to urlpatterns:
<pre class="code-highlight" data-language="python"><code><span class="code-line"><span class="kn">from</span> <span class="nn">rest2backbone.forms</span> <span class="kn">import</span> <span class="n">FormFactory</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="c1">#add to urlpatterns list</span></span>&#10;<span class="code-line"><span class="n">url</span><span class="p">(</span><span class="sa">r</span><span class="s1">&#39;^/?$&#39;</span><span class="p">,</span> <span class="n">TemplateView</span><span class="o">.</span><span class="n">as_view</span><span class="p">(</span><span class="n">template_name</span><span class="o">=</span><span class="s1">&#39;sample/app.html&#39;</span><span class="p">),</span> <span class="p">&#123;</span><span class="s1">&#39;forms&#39;</span><span class="p">:</span> <span class="n">FormFactory</span><span class="p">(</span><span class="n">router</span><span class="p">)}),</span></span></code></pre>
This will generate form templates for all registered models - the form template has id  attribute  r2b_template_<span style="color: #c0c0c0;">yourmodelname<span style="color: #000000;"> or   </span></span>r2b_template_<span style="color: #c0c0c0;">yourmodelname</span>_ro (for read only template).</li>
<li>Now you can start to write some code for your client application using Backbone.js (<a href="http://backbonetutorials.com/">this tutorial</a> and <a href="http://coenraets.org/blog/2011/12/backbone-js-wine-cellar-tutorial-part-1-getting-started/">this tutorial</a>  are nice to get basic overview of Backbone.js) - all  generated models, collections, indexes are available  in <code>restAPI</code> global object.  So you can create some views  for these models and collections- rest2backbone provides  another JS API to help with views in <code>formsAPI</code> global object - it contains several base objects, which you can extend - <code>formsAPI.BaseView</code> (generic view that renders template against model attributes), <code>formsAPI.FormView</code> (with some functions to support form saving and validation) and <code>formsAPI.BaseListView</code> (base for views of collections - supports pagination).  Your views can leverage generated templates - especially for displaying forms.
You can take a look at sample application code  - <a href="https://github.com/izderadicka/rest2backbone/blob/master/sample_app/templates/sample/app.html">app.html</a>   and <a href="https://github.com/izderadicka/rest2backbone/blob/master/sample_app/static/js/app.js">app.js</a> contain all code for the client side.</li>
</ol>




## Install,   Develop


rest2backbone in hosted on github <a href="https://github.com/izderadicka/rest2backbone">here</a>. Looks at <a href="https://github.com/izderadicka/rest2backbone/blob/master/readme.md">readme</a> \-   how to install and get sample application running - that should be app. 5 minutes task.

If you would like to extend, modify you can fork it on GitHub,   any contribution is welcomed indeed.

Where is <strong>API documentation</strong>?  Sorry, not yet -   I'll try - for now just look into code -   it's still small.   Key elements are mentioned above in Quick Start.

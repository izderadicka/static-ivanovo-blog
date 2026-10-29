+++
title = "Farewell Django"
path = "/farewell-django/"
date = "2016-01-16T16:34:56"
include_in_feeds = true
[extra]
wordpress_id = 1205
kind = "post"
node_key = "1205"
author = "admin"
source_url = "http://zderadicka.eu/farewell-django/"
source_guid = "http://zderadicka.eu/?p=1205"
source_date_gmt = "2016-01-16 15:34:56"
categories = ["Programming"]
tags = ["django", "web framework"]
+++
Recently I've been reviving 2 years old Django application (<a href="/projects/python/myplaces/">myplaces</a>)  (from version 1.5.5 to latest version 1.9) and I was very unpleasantly surprised how tedious it was.   As Django  evolved  some features got deprecated and removed and must have been replaced in the code.  And it's not only Django but also other contributed libraries are evolving as rapidly.   In my application I was using django-rest-framework,  which changed so significantly in version 3, that I cannot use it in my application without basically rebuilding the whole application.

Some of the changes might be necessary, but many where just cosmetic changes in names ( mimetype -\> content\_type, etc.), which I do not see as much of value add.  Even core python still keeps bit of naming fuss in favour of backward  compatibility ( for instance string.startswith, string.endswith made it till ver.3,  even if they are not in line with <a href="https://www.python.org/dev/peps/pep-0008/#function-names">PEP008</a> \- python naming standards).

But it's not only about changes of interface between versions (there is a fair process to deprecate features so when one follows development,  it's relatively easy to stay up to date), but it's mainly all concept of the Django. Django was created more then 10 years ago, when web development was focused around servers and everything happened there.  But situation changed radically ( <a href="/web-clients-are-getting-thick/">as I have written some time ago</a>).  Now a lot of things is happening in the browser and you can have complete applications running  there (recently I discovered <a href="http://listen.hatnote.com/">this cool application</a>, which is running almost completely in the browser, it's just using  a stream of events from the server).  Accordingly servers now are used more to provide APIs to browser applications or to route real time communication to/from/between browsers.<span id="more-1205"></span>

Theoretically you can do all this new great stuff in Django (as I have tried  in <a href="/projects/python/myplaces/">myplaces</a> application), however it always needs some add-ons (django-rest-framework for RESTfull API,  gevent-socketio for websockets and socket-io real time communication) and overall it does not feel so great, because new stuff have to match with the old concepts.  Django is quite large and rather monolitic framework, so anything added to it must really try hard to fit in.  As a result new features are bit artificial,  and you need to really understand Django well to see how they should be used.

So where this  article is leading to?  For me to the simple conclusion that I'll try to avoid Django in my future projects. It has been nice 8 years or so and I've learned a lot, but it's time to move on.

There are surely now many valuable alternatives to Django.  In python world it's for instance <a href="http://flask.pocoo.org/">Flask</a>, which I have used in couple of my recent small projects.  Flask is generally much more lighter then Django, so it's easy to start a new project and whole development there feels much more 'natural'.  Of course out of box it does not provide so much functionality as Django, but what is there feels really good ( configuration, Jinja2 templates, session management etc.). And it's easy to add functionality from tons of available extension ( like advanced authentication and SSO with SAML2, which I used recently).  There is a risk there that Flask does not so firmly control the application architecture as the Django does, so one can easily get  into real mess, but on the other hand one can customize application  for specific use cases or technologies more easily ( like using No-SQL data stores).

Outside of Python world there are many interesting possibilities, for instance now very popular <a href="https://nodejs.org/en/">Node.js</a> with it's apps servers like <a href="http://expressjs.com/">Express.js</a>, <a href="http://loopback.io">Loopback</a>, which enable by default many new technologies and approaches (<a href="https://www.quora.com/What-are-the-benefits-of-developing-in-Node-js-versus-Python">see this post by Django contributing author Jacob</a>).  Or for curious seekers like myself there are other more weird and technically interesting web frameworks like <a href="http://ocsigen.org/eliom/">Eliom</a> (see this article about<a href="/ocaml-ocsigen-i-ching-and-web-applications/"> my experieces with Eliom</a>) or something even more obscure like Opa (again see <a href="/opa-mixed-impressions/">my article about Opa experiences</a>).

"<span title="Source: Harry Potter and the Half-Blood Prince"><i>Farewell, Django, king of web frameworks, whose long and faithful friendship those who knew you won't forget! "</i></span>

+++
title = "Lessons Learned From Current Web Application Development"
path = "/lessons-learned-from-current-web-application-development/"
date = "2017-01-21T17:11:44"
include_in_feeds = true
[extra]
wordpress_id = 1524
kind = "post"
node_key = "1524"
author = "admin"
source_url = "http://zderadicka.eu/lessons-learned-from-current-web-application-development/"
source_guid = "http://zderadicka.eu/?p=1524"
source_date_gmt = "2017-01-21 16:11:44"
[taxonomies]
category = ["Programming"]
tag = ["Javascript", "ORM", "python", "Web Application"]
+++
[Mybookshelf2](/projects/python/mybookshelf2-ebooks-management-and-sharing/) (MBS2) is basically in beta stage and provides all functionality available in previous version and more. As I went through programing the new application using several new technologies,  I've realized few things, which I'd like to share here.<span id="more-1524"></span>


## Web client development's got quite complex


It's not enough now to know a bit of Javascript and few libraries (aka [jQuery](https://jquery.com/)) to create compelling web font end. With rise of Single Page Applications (SPA) and dominance of elaborate JS UI frameworks like [Angular](https://angularjs.org/), [Aurelia](http://aurelia.io/), [React](https://facebook.github.io/react/), ... web front end development is getting pretty complex and happily competes with complexity of server side development. One of key factors that contribute to this change is a tool stack needed for current JS front end development. Let me demonstrate this on the tool stack I had to learn for my  Aurelia framework based front end development:



- [NodeJS](https://nodejs.org/en/) - to run all required tools
- [NPM](https://www.npmjs.com/) - to install tools and required packages
- [Babel](https://babeljs.io/) transpiler( compiler that compiles JS to JS)  to compile next generation JS (or [TypeScript](https://www.typescriptlang.org/))  into [ES5](https://en.wikipedia.org/wiki/ECMAScript#5th_Edition) code understandable  by current and legacy browsers
- [Gulp](http://gulpjs.com/) - a build tool
- [BrowserSync](https://browsersync.io/) - to run and test front end application
- [JSPM](http://jspm.io/) - to package the code for the web browsers and load modules in the web browsers
- [Karma](https://karma-runner.github.io/1.0/index.html) and [Jamine](https://jasmine.github.io/) - to run tests



All above was basically needed to to build, test and run my code. On top of that you indeed need UI framework itself and numerous other libraries (like above mentioned jQuery, which is far from being obsolete by new frameworks).  I also found that good knowledge of developer tools in browser (Firefox and Chrome) is essential.

Aurelia framework has done good job to hide this tool chain complexity from me,  but nevertheless as my project evolved I had to cope directly with some of these tools anyhow (browser packing and JSPM especially gave me quite hard time -  I actually made a round trip from JSPM to bare [SystemJS](https://github.com/systemjs/systemjs), then to [WebPack](https://webpack.github.io/), to finally return back to JSPM, which turned out to be best solution for me after all) .

By no means I'd  like to make impression that these tools are not good.  Actually they all are pretty good (some of them are truly impressive, for instance BrowserSync, which saved me a lot of time during development). But still all these new tools were additional things I had to learn to be able to develop modern web applications.


## Quantum leap in Javascript


[ECMAScript](https://en.wikipedia.org/wiki/ECMAScript) 6 ( abbreviated as ES6 or  ES 20015)  is a great progress in Javascript!   It's loaded with tons of new features, both in syntax and functionality of build-in JS objects.  It's so much better then previous versions,  so finally I did start to like Javascript.  Now finally it is getting on pair with Python concerning the expressiveness of the language.

As a part of this project I had to learn ES6 and since there are some many changes I'd recommend to read a book about it. I have found [this free book](https://leanpub.com/understandinges6/read) quite good.


## Is ORM needed for implementation of RESTful API?


On server side MBS2 application is mainly a kind of RESTful API implementation, which is then used by rich SPA JS client. I implemented  it pretty conservatively using [Flask-RESTful](https://github.com/flask-restful/flask-restful), [SQLAlchemy](http://www.sqlalchemy.org/) and [Flask-SQLAlchemy. ](http://flask-sqlalchemy.pocoo.org)SQLAlchemy is pretty impressive package, very powerful (much more then Django ORM), but also quite complex and it took me some time to learn it.  And as I was progressing through server API implementation a heretic thought pop up -  Why I need all that ORM ([Object Relational Mapping](https://en.wikipedia.org/wiki/Object-relational_mapping)) thingy in my API functions. Of course it's very convenient, but as for advanced functionality of ORM layer like sessions, unit of work, caching etc. I had a little use for it.  Usually it was just about grabbing an object or lists of objects and sending  them out ( or insert, update, delete of single object).  Sometimes even advanced ORM functionality stood in the way of correct implementation ( auto-flushing of object to database too early).

It would be probably OK  if there were no additional consequences of using ORM, however as I've shown  in [this article](/sql-or-nosql-why-not-to-use-both-in-postgresql/),  ORM means significant drop in performace - ORM queries are several times slower (5x- 10x) then direct access using SQL. It's understandable, considering complex machinery under the hood, but in case of RESTful API, where we are almost not using it, it looks like quite a waste. Actually more compelling problem for me with RESTful API for me was serialization and deserialization of data, where ORM did helped only little (in case of nested objects).

So if ORM is superfluous (in my opinion), what else we can use.   My proposal would be to use custom DAL (Data Access Layer),  using SQL directly in DBAPI driver  (or through excellent  SQLAlchemy SQL Expressions Language, which makes construction of SQL statements more general and pythonic). Writing DAL could be bit boring,   but in the end probably not much more time consuming then using ORM (considering simple scenarios I have for RESTful API).

I've already done something similar for another part of the application - back-end ebooks processing engine, which is responsible for ebooks conversions and metadata extractions.  As this program is written as completely asynchronous (with asyncio), there is no possibility to use ORM, only core SQLAlchemy for SQL construction. DAL layer is also asynchronous (using [aiopg](https://github.com/aio-libs/aiopg)) and generally works fine.

Actually what I did missed in my project was a good comprehensive library for data management on client side - in the browser. I very quickly looked at [BreezeJS](http://www.getbreezenow.com/), which looks interesting. So on my next project I might try  different approach - very simplistic RESTful API (possibly auto-generated from database schema) and some advanced client side data library like Breeze, because now everything happens in the client anyhow.


## WAMP and Crossbar.io usage was an overkill for such application


I have written about WAMP protocol in [this article](/wamp-is-websocket-on-steroids/).  In MBS2 it's used to send requests to backend processing engine and monitor progress of such tasks.   This functionality is implemented in separate package [ASEXOR](https://github.com/izderadicka/asexor).  I have no particular complains about Crossbar.io and used libraries, they work great and they are mature and reliable, however considering the simplistic needs of the application ( call one remote function and subscribe to one updates source)  using full WAMP stack is just an overkill. Looking at it now I think more simple communication using WebSocket directly and some simple [aiohttp](http://aiohttp.readthedocs.io/en/stable/) server would be more appropriate.  But I have to admit using WAMP and Crossbar.io was a good learning exercise ( as I needed to implement new transport ([asyncio WAMP over rawsocket](https://github.com/crossbario/autobahn-python/pull/679)) into [autobahn](http://autobahn-python.readthedocs.io/en/latest/) WAMP library).


## Python becoming irrelevant as server platform for web applications


Do not take me wrong,  I do love Python. It's a great language, with many applications in many areas, web development being just one of them (as for others, probably more prominent,  I can mention scientific computing and system tools).  However as I looked around during application development I think python is loosing slightly in area of web development.  I have already written about [myself leaving Django behind](/farewell-django/), but generally I think more interesting and progressive  things are now happening outside Python, especially in NodeJS community (if we look within scripting languages  universe, outside of this universe of course a lot of interesting things is happening in Java, Scala, Go etc).  Javascript with  ES6 version became quite nice language and having one language for client and server is indeed a significant benefit. But what attracts me more are interesting projects like [Loopback](http://loopback.io/) (recently acquired by IBM) , [Feathers](http://feathersjs.com/) and others similar, which promise quick path to scalable and flexible API server.

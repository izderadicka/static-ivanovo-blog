+++
title = "Running uWSGI for gevent enabled application"
path = "/running-uwsgi-for-gevent-enabled-application/"
date = "2014-08-21T10:05:31"
include_in_feeds = true
[extra]
wordpress_id = 836
kind = "post"
node_key = "836"
author = "admin"
source_url = "http://zderadicka.eu/running-uwsgi-for-gevent-enabled-application/"
source_guid = "http://zderadicka.eu/?p=836"
source_date_gmt = "2014-08-21 09:05:31"
[taxonomies]
category = ["Admin", "Programming"]
tag = ["gevent", "python"]
+++
[Gevent](http://www.gevent.org/) is a great library that uses [greenlets](http://greenlet.readthedocs.org/en/latest/) (a Python co-routine library) to enable asynchronous I/O, while providing  API that looks like normal synchronous API, so it's  easier to use and understand.  The async magic is done automatically by Gevent, which is running an event loop on background and switching between coroutines as necessary.

This approach can be very useful for concurrent applications, which spend a lot of time in waiting for I/O.  Like web applications - so Gevent is popular there.  For certain type of workloads it can be quite useful - it can enable higher concurrency,  while using less resources (greenlet is much lighter then thread or  process).<span id="more-836"></span>

Another cool thing in Gevent is so called 'monkey patching'  -  basically you can write application using standard Python modules like socket, time etc.   Then add call `gevent.monkey.patch_all()` at beginning of your application and all synchronous functions calls will be replaced with Gevent equivalents transparently and your application will run in Gevent environment straight away (there are some gotchas - I'll speak about one later).

Recently I've created a small web application that serves as a front-end to command line program. Basically it uploads a file, then runs the program with appropriate parameters, reads its output and presents it on web page.  Clearly this web application will spend most of its time waiting for program output.  So it seems as overhead to have additional threads and processes just to enable concurrency of web access.

In python [WSGI](http://wsgi.readthedocs.org/en/latest/) specification defines how web application should interact  with HTTP gateway - there are several good implementations of WSGI servers,  I've read particularly good references for [uWSGI](https://uwsgi-docs.readthedocs.org/en/latest/), so I decided to try in this project,  together with its Gevent support (which is available in recent versions).

Gevent and uWSGI can be easily installed via:

`pip install gevent uwsgi`

In uwsgi you  just need to just use --gevent x option, where x is number of concurrent requests (each request has it's own greenlet), so command might look like this:

`uwsgi --http-socket :8000 --gevent 10  --module my_app`

assuming application my\_app is Gevent aware.  As described above this can be done easily by monkey-patching.  uwsgi can even do this patching for you if you use --gevent-monkey-patch option.  However there is one issue to be aware of. If you use --gevent-monkey-patch  , patching is done <span style="text-decoration: underline;">after</span> your module is loaded. This can have quite fatal consequences. Let's illustrate it on simple example:


```python
import time

def application(e, sr):
    path = e.get('PATH_INFO', '')
    if path=='' or path=='/':
        sr('200 OK', [('Content-Type','text/html')])
        yield "sleeping for 30 seconds...<br/>\n"
        time.sleep(30)
        yield "done<br>\n"
    else:
        sr('404 Not Found', [('Content-Type','text/html')])
        yield "Not found"
```


This application will work as expected - e.g. if you'll send couple of requests (use curl -N,  normal clients serialize requests to same resource) , each one will response immediately with 'sleeping for 30 seconds ...',  because sleep is patched for Gevent asynch mode.

However if we slightly modify the code:


```python
from time import sleep

def application(e, sr):
    path = e.get('PATH_INFO', '')
    if path=='' or path=='/':
        sr('200 OK', [('Content-Type','text/html')])
        yield "sleeping for 30 seconds...<br/>\n"
        sleep(30)
        yield "done<br>\n"
    else:
        sr('404 Not Found', [('Content-Type','text/html')])
        yield "Not found"
```


It will not work - first request will block all others.  It's because sleep is referencing to unpatched version function. (patching was done only after module was loaded).

To prevent this from happening monkey patching must be done before module is loaded - easy solution is not to use --gevent-monkey-patch option, but create small wrapper module that does monkey patching and then imports application:


```python
from gevent import monkey
monkey.patch_all()

from my_app import application
```


 


### uWSGI in Debian


For production I'm using virtual machine with Debian Wheezy -   it has uwsgi package in its repositories, but it's quite old (ver. 1.2, while current version is 2.0,   Gevent support is there only  from 1.9). However uwsgi package can be still useful, because it contains infrastructure to integrate uWSGI into Debian system (/etc configurations,  init.d startup scripts ...), so it worth to install it, but then change uwsgi binary to one installed via pip:


```sh
apt-get install uwsgi
rm /etc/alternatives/uwsgi
ln -s /usr/local/bin/uwsgi /etc/alternatives/

```


Finally we need to add correct configuration file into /etc/uwsgi/apps-available (and link it to /etc/uwsgi/apps-enabled):


```sh
[uwsgi]
socket = /tmp/my_app.uwsgi
chdir = /opt/my_app_directory
gevent = 30
master=false
workers=1
module = my_app

```


This modifies Debian defaults (2 worker processes, 1 master process) to just one process, which should be enough for smaller application.  Here uwsgi is listening on unix socket,  so you need a http server - nginx for instance - this site configuration will work:


```sh
server {
	listen   80; ## listen for ipv4; this line is default and implied
	listen   [::]:80 default_server ipv6only=on; ## listen for ipv6

	root /opt/my_app_directory;
	index index.html index.htm;

	# Make site accessible from http://localhost/
	server_name my_app.example.com;

	location /static/ {
		# static app files
		try_files $uri $uri/ 404;
	}

	location / {
		include uwsgi_params;
		uwsgi_pass unix:/tmp/checker.uwsgi;
	}

}
```


Finally just restart both servers.

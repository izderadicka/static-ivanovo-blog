+++
title = "Long Running Taks in Web App/Django"
path = "/long-running-taks-in-web-appdjango/"
date = "2013-07-18T14:43:04"
include_in_feeds = true
[extra]
wordpress_id = 582
kind = "post"
node_key = "582"
author = "admin"
source_url = "http://zderadicka.eu/long-running-taks-in-web-appdjango/"
source_guid = "http://zderadicka.eu/?p=582"
source_date_gmt = "2013-07-18 13:43:04"
categories = ["Programming"]
tags = ["django", "python", "tasks manager", "web socket", "zeromq"]
+++
Some types of web applications require to start long running tasks - like import of file, compilation etc., but  user still needs to have real time updates about progress of the task, eventually some error messages, warnings from the task (cannot import particular line, compilation error).   There are existing robust solutions like <a href="http://www.celeryproject.org/">Celery</a>, but it is aways fun to reinvent the wheel :-)   In this case we focus on simple solution, without need for request broker in middle, which enables  immediate/ real time updates on running tasks to client browser.

For our solution we will use two cool technologies/libraries web sockets and zeromq library.<span id="more-582"></span>


## Used Libraries


<a href="http://www.zeromq.org/">zeromq</a>  (or zmq)- is C library for asynchronous messaging  with binding to many languages (python included). ZMQ has very good reputation for robustness and ease of use. In this example we used zeromq library 3.2.3, with python binding pyzmq 13.0.2, which was not yet available in latest Ubuntu distro (in there it's still old version 2 of zmq library), so it has to be installed manually from source.

<a href="https://github.com/abourget/gevent-socketio">gevent-socketio</a> \- is python port of <a href="http://socket.io/">socket.io</a> server part. Socket.io is Javascript library, that wraps web sockets and provides advanced functionality on top web socket (namespaces, custom events/messages,  heartbeat etc.). Also for web browsers, which do not support web socket, it provides alternative communication mechanism via same interface.

<a href="http://www.gevent.org/">gevent</a> \- is requirement for gevent-socketio  - gevent is a networking library that enables non-blocking usage of sockets, for this purpose gevent is using so call <a href="http://en.wikipedia.org/wiki/Green_threads">green threads</a> (<a href="http://greenlet.readthedocs.org/en/latest/">greenlets</a>)

optionally <a href="https://www.djangoproject.com/">django</a> \- web application framework, it is not basically necessary - pages and socket server part can run in any other web server that support gevent (gevent itself, gunicorn, ...)

<a href="http://jquery.com/">jquery</a> \- Javascript library


## Solution Architecture


Long running (tens of minutes, hours) tasks are usually not related to content of the web page and can be also pretty complex - so we should better keep them outside of web server in a separate process(es).   We can start processes directly from the web server, but it usually has disadvantages (like limited privileges to web server user, no control over launched processes etc.) ,so we  have another process that will launch our tasks in  separate processes. For communication between processes we will use zeromq. Additionally messages from tasks (progress, errors etc.)  -are switched to browser web socket, so client can immediately see them.   We consider linux as our OS of choice.

On following picture is general architecture of our solution:

<a href="/wp-content/uploads/proc_server.png"><img alt="" class="alignnone size-large wp-image-602" decoding="async" height="353" loading="eager" sizes="(max-width: 640px) 100vw, 640px" src="/wp-content/uploads/proc_server-1024x565.png" srcset="/wp-content/uploads/proc_server-1024x565.png 1024w, /wp-content/uploads/proc_server-300x165.png 300w, /wp-content/uploads/proc_server.png 1122w" title="proc_server" width="640"/></a>

On client side, in Javascript, we  connect socket to web server first - to receive messages from the task and display them on the page in various ways (progress message can update progress bar, error message can be displayed in some kind of log view, or raise pop up window etc.)
Then we  do Ajax call to server to start task in a separate process - web server will pass this request to "Workers Server", which should be already running in background. Web server uses REQ-REP zmq sockets pair for this - request contains name of  function, which should  run remotely and its parameters (something like simple RPC), response confirms that process was launched, eventually any immediate errors, that prevent process to be launched.   Workers Server receives this message and launches appropriate function in a new process (using multiprocessing package).   Task itself has to open PUB zmq socket and publish relevant messages - about it's progress, eventual errors etc.
Workers Server  contains also proxy for all PUB messages, so they are collected  from all tasks and re-published again on one well-known port - so web server can always find them in one fixed location. On the web server we define socket.io namespace, that is activated when client opens a socket  from a page and that  just passes messages from zmq SUB socket to web socket.  Here we also must subscribe only  messages related to the task started from that particular web page - this can be done by assigning unique id to our task, that is sent, when web socket is connected from page.


## Python code


First let's have some utility functions (all supporting code is in remote module - for convenience- zipped <a href="/wp-content/uploads/remote.py_.zip">remote.py</a> ):


```python
def init(green=False):
    global zmq
    if green:
        import zmq.green as zmq
    else:
        import zmq

def create_socket(context,stype, linger=100):
    stype=stype.lower()
    if stype=='client':
        socket=context.socket(zmq.REQ)
        socket.connect(ADDR)
    elif stype=='server':
        socket=context.socket(zmq.REP)
        socket.bind(ADDR)
    elif stype=='pub':
        socket=context.socket(zmq.PUB)
        socket.connect(ADDR_SUB)
    elif stype=='sub':
        socket=context.socket(zmq.SUB)
        socket.connect(ADDR_PUB)
    else:
        raise ValueError('Invalid socket type')

    socket.setsockopt(zmq.LINGER,linger)
    return socket

def context():
    return zmq.Context()
```


`init` function imports right flavor of zmq -   for zmq working correctly in gevent environment we had to import zmq.green.  `create_socket` is just wrapping socket creation into one convenient function.`  zmq.LINGER ` assures that undelivered messages are discarded after socket is closed - otherwise zmq will try to deliver them forever (resp. until whole process is finished). `context` function just wraps context creation.

Next we write  "Workers Server"  code  - it is pretty simple code :


```python
def server():
    ctx=context()
    in_socket=create_socket(ctx, 'server')
    run_proxy( ctx)
    while True:
        do_remote_call(in_socket)
    in_socket.close()

if __name__ == '__main__':
    init()
    server()
```


Server has basically two function - first is to receive requests for a task, which  then runs in a separate process - that is done by `do_remote_call` function:


```python
def do_remote_call(socket):
    def _err(msg):
        socket.send_multipart((ERROR_TAG, msg))
        log.error(msg)
    method, call_id, args= socket.recv_multipart()
    try:
        running_processes=_check_running(call_id)
    except AlreadyRunning:
        _err('Process for call_id %s is already running'%call_id)
        return
    if running_processes>=_PROCESS_LIMIT:
        socket.send_multipart((BUSY_TAG, 'Reached process limit of %d'%_PROCESS_LIMIT))
        log.info('Reached processes limit of %d'% _PROCESS_LIMIT)
        return
    fn=_REMOTE_METHODS.get(method)
    if not fn and not callable(fn):
        _err( 'Uknown method %s'%method)
        return

    try:
        args=pickle.loads(args)
        if not isinstance(args, (list, tuple)):
            _err( 'Invalid arguments, must be tuple or list')
            return
    except Exception, e:
        _err( 'Error while deserializing args - %s'% str(e))
        return
    try:
        p=multiprocessing.Process(target=fn, args=args)
        p.start()
    except Exception,e:
        _err('Error while starting process %s'%str(e))    
    pid=p.pid
    log.debug("Started process %d for %s(%s)", pid, method, args)
    if call_id and pid:
        _running[pid]=call_id
    socket.send_multipart(('',str(pid)))
```


This function is basically taking a function name and its arguments from received message and  using them with multiprocessing module to fork new process.   Majority of the code here is to check limit conditions and report errors . One of important limit conditions is that child processes do not grow over certain limit, another is that same call is not launched twice, if previous is still running - this is checked by supporting function `_check_running`:


```python
def _check_running(call_id):
    children=multiprocessing.active_children()
    children_pids=set([x.pid for x in children])
    to_del=[]
    for pid in _running:
        if pid not in children_pids:
            to_del.append(pid)
    for pid in to_del:
        del _running[pid]
    if call_id and call_id in set(_running.values()):
        raise AlreadyRunning()

    return len(children)
```


which is using global `_running` dictionary.  As noted  before `do_remote_call` will require some function name, which is defined in current scope - for security reason we should not allow to use any name, but only functions, which are intended for this purpose - we can use this function decorator to mark that function is available for remote call:


```python
def is_remote(fn):
    _REMOTE_METHODS[fn.__name__]=fn
    return fn
```


And we indeed need some function that is called - so let's look at one dummy function:


```python
@is_remote
def process(token):
    # need new context after forking
    pid=str(os.getpid())
    ctx=context()
    pub=create_socket(ctx, 'pub')
    for i in range(10):
        print 'Sending from %s' % pid
        send_msg(pub,  token, 'msg', {'process':pid, 'step':i, 'token':token})
        time.sleep(1)
    send_msg(pub, pid,'done', pid)    
    pub.close()
```


In this function it is important to create new zmq context (line 5),  because this code  runs in forked process and parent context there is not valid.  Also we should create a 'pub' socket, where we can send updates from the task (and these are relayed to client web page Javascript).

Function `send_msg` wraps sending message on pub socket:


```python
def send_msg(socket, stream_id, type, data):
    data=pickle.dumps(data)
    socket.send_multipart((stream_id, type, data))
```


As mentioned above Workers Server has also second function - to relay messages published by forked task processes - for this we can use zmq device (device is an utility that just forwards messages between input and output sockets).   In server code we had function  `run_proxy` for this purpose:


```python
def run_proxy(context):   
    proxy=zmq.devices.ThreadDevice(zmq.QUEUE, zmq.XSUB,zmq.XPUB )
    proxy.bind_in(ADDR_SUB)
    proxy.bind_out(ADDR_PUB)
    proxy.start()
```


So that would  be all  fundamental Workers Server  pieces, now to pieces, which should fit into web server - first we have couple of utility functions in remote module:


```python
def sub_msg(socket, stream_id):
    socket.setsockopt(zmq.SUBSCRIBE, stream_id)

def poll_msg(socket, cb_fn, timeout=3600):
    poller=zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    while True:
        available=dict(poller.poll(timeout))
        if available.get(socket)==zmq.POLLIN:
            stream_id, mtype, data=socket.recv_multipart()
            if cb_fn(stream_id, mtype, pickle.loads(data)):
                return
        else:
            raise TimeoutError()

def call_remote(socket, method, args, call_id=''):
    if isinstance(call_id, unicode):
        call_id=call_id.encode('utf-8') 
    socket.send_multipart((method, call_id, pickle.dumps(args)))
    poller=zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    ready=dict(poller.poll(3000))
    if ready and ready.has_key(socket):
        result, resp=socket.recv_multipart()
    else:
        raise RemoteError('No response from server')
    if result==ERROR_TAG:
        raise RemoteError(str(resp))
    elif result==BUSY_TAG:
        raise BusyError(str(resp))
    return resp
```


Function `sub_msg` has to be used on SUB socket to subscribe to particular stream of messages (if SUB socket is not subscribed it will receive nothing).  `poll_msg` is used to receive message with given timeout and `call_remote` is used to create remote task ( opposite end of `do_remote_call`, which was presented above).

In the web server we will have to create a code, that responds to Ajax call and and starts a task with `call_remote`.  In Django we have a view (in views.py)  function for this, bound to certain url:


```python
def sample_view_to_start_dummy_task(request, token, call_id):
    socket=None
    try:
        socket=remote.create_socket(zmq_ctx, 'client', 0)
        try:
            remote.call_remote(socket, 'process', [token], call_id=call_id)
        except remote.RemoteError, e:
            return rjson({'errors':[_('Remote Error (%s)')% str(e)]})
    finally:
        if socket:
            socket.close()
    return rjson({})
```


`rjson` just returns response with JSON content. JSON is used to indicate errors, which can occur when doing remote call. Also global zmq context (`zmq_ctx`) has to be defined somewhere -  one for all process (in our case it is in sockets.py as shown below).

We  need also server code for socket.io,  latest  python-socketio contains some code for integration with Django - we  have to put these lines to root urls.py:


```python
import socketio.sdjango
socketio.sdjango.autodiscover()
urlpatterns = patterns('',
    url("^socket\.io", include(socketio.sdjango.urls)),
)
```


This code  binds a handler to /socket.io url that can start individual namespaces  and `autodiscover`  looks for any sockets.py files in installed Djago applications and register namespaces defined there. Namespace is basically a 'virtual' socket, that has a name, and can receive and send messages limited to that namespace only.

Here is sockets.py for our application:


```python
from socketio.namespace import BaseNamespace
from socketio.sdjango import namespace
import remote

import logging
log=logging.getLogger('mp.sockets')
remote.init(True) #have to init with True to enable gevent support
ctx=remote.context()

@namespace('/log')
class LogController(BaseNamespace):
    def initialize(self):
        log.debug('Log Controller started')

    def on_start(self, stream_id):
        log.debug('Started %s', stream_id)
        socket=remote.create_socket(ctx, 'sub')
        try:
            remote.sub_msg(socket, stream_id.encode('utf-8'))
            def on_msg(proc_id, mtype, msg):
                self.emit(mtype, msg)
                if mtype=='done':
                    self.disconnect()
                    return True
            try:
                remote.poll_msg(socket, on_msg)
            except remote.TimeoutError:
                log.warn('SUB socket timeout')
                self.disconnect()
        finally:
            socket.close()
```


Note that we have to use decorator `namespace` to given class so it is included to socketio namespaces definition and used when client connect this namespace.   The namespace is  waiting on 'start' message from client and then it resends all messages from SUB socket to this namespace  socket (filtered by stream\_id - an identifier of page that started the process).

And finally Javascript code using JQuery, which sits on page that initiates remote task (with two Django template tags to supply context data):


<pre class="code-highlight" data-language="javascript"><code><span class="code-line"><span class="kd">function</span><span class="w"> </span><span class="nx">launchTask</span><span class="p">()</span><span class="w"> </span><span class="p">&#123;</span></span>
<span class="code-line"><span class="w">   </span><span class="kd">var</span><span class="w"> </span><span class="nx">streamId</span><span class="o">=</span><span class="s1">&#39;&#123;&#123;stream_id}}&#39;</span><span class="p">;</span></span>
<span class="code-line"><span class="w">   </span><span class="kd">var</span><span class="w"> </span><span class="nx">errors</span><span class="o">=</span><span class="nx">$</span><span class="p">(</span><span class="s1">&#39;ul.errors&#39;</span><span class="p">);</span></span>
<span class="code-line"><span class="w">   </span><span class="nx">errors</span><span class="p">.</span><span class="nx">empty</span><span class="p">();</span></span>
<span class="code-line"></span>
<span class="code-line"><span class="w">   </span><span class="kd">var</span><span class="w"> </span><span class="nx">startTask</span><span class="o">=</span><span class="kd">function</span><span class="p">()</span><span class="w"> </span><span class="p">&#123;</span></span>
<span class="code-line"><span class="w">	</span><span class="nx">$</span><span class="p">.</span><span class="nx">ajax</span><span class="p">(</span><span class="s1">&#39;&#123;%url your_app.sample_view_to_start_dummy_task token=stream_id stream_id=stream_id%}&#39;</span><span class="p">,</span><span class="w"> </span><span class="p">&#123;</span></span>
<span class="code-line"><span class="w">		</span><span class="nx">method</span><span class="o">:</span><span class="s1">&#39;GET&#39;</span><span class="p">,</span></span>
<span class="code-line"><span class="w">		</span><span class="nx">success</span><span class="o">:</span><span class="kd">function</span><span class="w"> </span><span class="p">(</span><span class="nx">data</span><span class="p">,</span><span class="w"> </span><span class="nx">status</span><span class="p">,</span><span class="w"> </span><span class="nx">resp</span><span class="p">)&#123;</span></span>
<span class="code-line"><span class="w">		  </span><span class="k">if</span><span class="w"> </span><span class="p">(</span><span class="nx">data</span><span class="p">.</span><span class="nx">errors</span><span class="p">)&#123;</span></span>
<span class="code-line"><span class="w">			  </span><span class="k">for</span><span class="w"> </span><span class="p">(</span><span class="kd">var</span><span class="w"> </span><span class="nx">i</span><span class="o">=</span><span class="mf">0</span><span class="p">;</span><span class="nx">i</span><span class="o">&lt;</span><span class="nx">data</span><span class="p">.</span><span class="nx">errors</span><span class="p">.</span><span class="nx">length</span><span class="p">;</span><span class="w"> </span><span class="nx">i</span><span class="o">+=</span><span class="mf">1</span><span class="p">)</span><span class="w"> </span><span class="p">&#123;</span></span>
<span class="code-line"><span class="w">			       </span><span class="nx">errors</span><span class="p">.</span><span class="nx">append</span><span class="p">(</span><span class="nx">$</span><span class="p">(</span><span class="s1">&#39;&lt;li&gt;&#39;</span><span class="p">).</span><span class="nx">append</span><span class="p">(</span><span class="nx">data</span><span class="p">.</span><span class="nx">errors</span><span class="p">[</span><span class="nx">i</span><span class="p">]));</span></span>
<span class="code-line"></span>
<span class="code-line"><span class="w">			  </span><span class="p">}</span></span>
<span class="code-line"><span class="w">		  </span><span class="p">}</span></span>
<span class="code-line"><span class="w">	        </span><span class="p">},</span></span>
<span class="code-line"><span class="w">	        </span><span class="nx">error</span><span class="o">:</span><span class="kd">function</span><span class="p">(</span><span class="nx">req</span><span class="p">,</span><span class="w"> </span><span class="nx">status</span><span class="p">)&#123;</span></span>
<span class="code-line"><span class="w">		   </span><span class="nx">alert</span><span class="p">(</span><span class="nx">gettext</span><span class="p">(</span><span class="s1">&#39;Server Error: &#39;</span><span class="o">+</span><span class="nx">status</span><span class="p">));</span></span>
<span class="code-line"><span class="w">	 </span><span class="p">}})</span></span>
<span class="code-line"><span class="w">   </span><span class="p">};</span></span>
<span class="code-line"></span>
<span class="code-line"><span class="w">   </span><span class="kd">var</span><span class="w"> </span><span class="nx">log</span><span class="o">=</span><span class="nx">io</span><span class="p">.</span><span class="nx">connect</span><span class="p">(</span><span class="s1">&#39;/log&#39;</span><span class="p">,</span><span class="w"> </span><span class="p">&#123;</span><span class="nx">reconnect</span><span class="o">:</span><span class="kc">false</span><span class="p">});</span></span>
<span class="code-line"><span class="w">   </span><span class="nx">log</span><span class="p">.</span><span class="nx">on</span><span class="p">(</span><span class="s1">&#39;connect&#39;</span><span class="p">,</span><span class="w"> </span><span class="kd">function</span><span class="p">()</span><span class="w"> </span><span class="p">&#123;</span></span>
<span class="code-line"><span class="w">	</span><span class="nx">log</span><span class="p">.</span><span class="nx">emit</span><span class="p">(</span><span class="s1">&#39;start&#39;</span><span class="p">,</span><span class="w"> </span><span class="nx">streamId</span><span class="p">)</span></span>
<span class="code-line"><span class="w">	</span><span class="nx">startTask</span><span class="p">();</span></span>
<span class="code-line"><span class="w">	</span><span class="p">});</span></span>
<span class="code-line"><span class="w">   </span><span class="nx">log</span><span class="p">.</span><span class="nx">on</span><span class="p">(</span><span class="s1">&#39;msg&#39;</span><span class="p">,</span><span class="kd">function</span><span class="w"> </span><span class="p">(</span><span class="nx">msg</span><span class="p">)</span><span class="w"> </span><span class="p">&#123;</span></span>
<span class="code-line"><span class="w">	</span><span class="nx">$</span><span class="p">(</span><span class="s1">&#39;#results #messages&#39;</span><span class="p">).</span><span class="nx">append</span><span class="p">(</span><span class="nx">$</span><span class="p">(</span><span class="s1">&#39;&lt;li&gt;&#39;</span><span class="p">.</span><span class="nx">text</span><span class="p">(</span><span class="nx">msg</span><span class="p">))</span></span>
<span class="code-line"><span class="w">	</span><span class="p">});</span></span>
<span class="code-line"><span class="w">   </span><span class="nx">log</span><span class="p">.</span><span class="nx">on</span><span class="p">(</span><span class="s1">&#39;done&#39;</span><span class="p">,</span><span class="w"> </span><span class="kd">function</span><span class="p">(</span><span class="nx">msg</span><span class="p">)</span><span class="w"> </span><span class="p">&#123;</span></span>
<span class="code-line"><span class="w">	</span><span class="nx">$</span><span class="p">(</span><span class="s1">&#39;#results #messages&#39;</span><span class="p">).</span><span class="nx">append</span><span class="p">(</span><span class="s1">&#39;&lt;li&gt;&#39;</span><span class="p">.</span><span class="nx">text</span><span class="p">(</span><span class="s1">&#39;Import finished&#39;</span><span class="p">));</span></span>
<span class="code-line"><span class="w">	</span><span class="p">});</span><span class="w">	</span></span>
<span class="code-line"><span class="p">}</span></span></code></pre>


The function  `launchTask`   is called on button click or other appropriate event on the page.  Itl first connects to our namespace '/log', then when connected it sends 'start' message, which  makes namespace to listen on zmq SUB socket for messages coming from task process.  When namespace  socket  is connected we  do Ajax call to start the task on server.  URL of the ajax call is directed to the view we've introduced earlier - and we use some generated id -`  stream_id ` \- to identify both `call_id` (unique identifier of remote call - to prevent duplicate calls) and `stream_id` (to identify messages coming from our task process). When a message l come sfrom process we display it on the page ( where we have this html: `<div id="result"><ul id=<messages"></ul></div>` to hold messages). Also note that there are several places to report errors:


<ol>
<li>When view returns HTTP error - it is handled  by error option of Ajax call</li>
<li>When view cannot launch remote task - then Ajax returns JSON with errors key</li>
<li>When task itself has a problem - it can return appropriate messages, which are displayed</li>
</ol>


We  also need a page to host our Javascript code (in Django it means page template + view+ url definition).


##  How to Test And Run


In order to test we have to first start Workers Server as separate process.   Then we start web server - in case of Django we need to start it with gevent support -   python-socketio contains sample application "chat" containing custom command for manage.py  (I think I had to add to it `gevent.monkey.patch_all() ` in order to work)- we have to enable this application in Django site settings py.   Then we can start Django web server as `./manage.py runserver_socketio`  and in browser open the page and click button (or whatever action that will start JavaScript above) and fun can begin.

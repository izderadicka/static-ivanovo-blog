+++
title = "WAMP Is WebSocket on Steroids"
path = "/wamp-is-websocket-on-steroids/"
date = "2016-06-13T16:24:21"
include_in_feeds = true
[extra]
wordpress_id = 1385
kind = "post"
node_key = "1385"
author = "admin"
source_url = "http://zderadicka.eu/wamp-is-websocket-on-steroids/"
source_guid = "http://zderadicka.eu/?p=1385"
source_date_gmt = "2016-06-13 15:24:21"
categories = ["Programming"]
tags = ["asyncio", "network", "python", "Websocket"]
+++
If you look for WAMP abbreviation over Internet, you will probably find that <a href="https://en.wikipedia.org/wiki/LAMP_%28software_bundle%29#WAMP">WAMP</a> = Windows + Apache + MySQL + PHP - which was popular web stack some time ago (but who wants to run web server on Windows today?  And other components  now also have  viable alternatives).   But in this article I'd like to talk about <a href="http://wamp-proto.org/">WAMP</a> = Web Application Messaging Protocol.  WAMP is available  as <a href="https://en.wikipedia.org/wiki/LAMP_%28software_bundle%29#WAMP">WebSocket</a> subprotocol, but also can work on plain TCP or Unix domain sockets.<span id="more-1385"></span>

Key difference from plain WebSocket or similar protocols is  that WAMP is <strong>routed</strong> protocol - it requires central router server to work. This enables loose coupling of components - because each component just need to connect to the central router, however the router then becomes  a single point of failure.  As per now there is no model nor implementation for multiple interconnected routers and inter-routers protocol(s), so this limits large scale implementations.

Also WAMP is not very common protocol - it has been designed and maintained by small German company <a href="http://tavendo.com/">Tavendo</a>, which also maintains reference router implementation <a href="http://crossbar.io/">crossbar.io</a> and client libraries for Python, Javascript, Android and C++ - <a href="http://autobahn.ws/">autobahn</a>. WAMP protocol is also <a href="https://tools.ietf.org/html/draft-oberstet-hybi-tavendo-wamp">IETF draft </a>(but draft is expired, so question is if it makes to standard or not).

Yet for small to medium size projects, experiments with micro-services and real time communication  this protocol looks attractive and I decided to give it a try in my current project.

Main advantage of WAMP is it's simplicity and clearly designed client libraries (at least from what I have seen in Python and Javascript). WAMP provides two basic messaging models: Publish - Subscribe and Remote Procedure Call (RPC) - both are very easy to use -  events and remote procedures are identified by generic URIs.  Just to give you idea here is definition of remote method, and publishing in Python:


```python
class Demo(ApplicationSession):

    async def onJoin(self, details):
        def run_task(task_name, *args, **kwargs):
            log.debug(
                'Request for run task %s %s %s', task_name, args, kwargs)
            self.session.publish('my.update', task_name, status='started')


        self.register(run_task, 'my.remote.proc')

# more code then needed to run this class

```


and remote method call and subscription in Javascript:


```javascript
var currentSession = null;

let task_updated = function (args, kwargs, details) {
    console.log('Task update', args, kwargs, details);
}

let connection = new autobahn.Connection({
    url: 'ws://127.0.0.1:8880/ws',
    realm: 'realm1'
});

connection.onopen = function (session) {
    console.log('Connection opened', session);
    session.subscribe('eu.zderadicka.asexor.task_update', task_updated);
    currentSession=session
};

//Somewhere later in code - 

currentSession.call('my.remote.proc', ['dummy task', 'arg'], {'other_arg': 'value'}).then(
      function(res) {
        console.log('Task result is'+ res);
});




```


Messages  in WAMP are based on <a href="http://www.json.org/">JSON</a> format -  so basically anything that is JSON serializable could be an argument or result of remote procedure or content of published event. Internally WAMP can leverage more efficient data serialization like <a href="http://msgpack.org/index.html">MessagePack,</a> <a href="http://ubjson.org/">UBJSON</a> or <a href="http://cbor.io/">CBOR</a>. (serializers are basically pluggable into protocol).

As WAMP is intended to be used  on both private and public networks security is indeed an important part of the protocol.   It can leverage SSL/TSL channel encryption for both Websocket or raw socket and the protocol itself offers authentication ( token, challenge-response, Websocket based ...) and authorization. Authorization allows to granularly define who can call, register procedure or publish, subscribe event based on procedure/event URI and user authentication credentials.

In my use-case I required clients (browser) to be able to submit various potentially long running tasks to server and receive instant updates about tasks progress and final results. Here is the solution architecture:

<a href="/wp-content/uploads/wamp.png"><img alt="wamp" class="alignnone size-large wp-image-1394" decoding="async" height="401" loading="eager" sizes="(max-width: 884px) 100vw, 884px" src="/wp-content/uploads/wamp-1024x465.png" srcset="/wp-content/uploads/wamp-1024x465.png 1024w, /wp-content/uploads/wamp-300x136.png 300w, /wp-content/uploads/wamp.png 1044w" width="884"/></a>

Idea is to extend regular Single Page Application  (browser client communicating with RESTful API server) with WAMP real time communication for specific tasks (conversion of ebooks).  Clients can easily submit requests for long running task via RPC and subscribe to updates via WAMP publish-subscribe model.

So we need server side component to schedule and launch tasks (conversion programs) in separate processes. It also talks WAMP and implements RPC to schedule task and publishes tasks updates.  This component is implemented in Python with autobahn library.   Autobahn library enforces asynchronous programming style using either <a href="https://twistedmatrix.com/trac/">twisted</a> or <a href="https://docs.python.org/3/library/asyncio.html">asyncio</a>.  I choose asyncio, because
a) it's now part of python standard libraries (and new `async` keywords  in 3.5 are really cool) and
b) I think it cleaner and easier to use that twisted (I never liked Twisted library very much -  it always seems to me, how to say it,  ehmm "twisted").

Crossbar.io is written in twisted and can run twisted server components within same process.  However asyncio components need to run in separate process and connect to the router via WAMP.  For server side I would prefer some efficient communication - ideally <a href="https://en.wikipedia.org/wiki/Unix_domain_socket">unix domain socket</a>, (Websocket overhead here would be useless). Small problem was that autobahn library did not have WAMP raw socket support for asyncio.  Fortunately it was not so difficult to add it - so I added it via <a href="https://github.com/crossbario/autobahn-python/pull/679">this pull request</a>.

The proof of concept tasks scheduler/manager called <a href="https://github.com/izderadicka/asexor">ASEXOR</a> (ASynchronous  EXecutOR) is available <a href="https://github.com/izderadicka/asexor">here on github</a>.

But WAMP has many other applications - look for instance at this <a href="https://github.com/crossbario/crossbarexamples/tree/master/django/realtimemonitor">example of simple system real time monitoring solution</a> (with Django frontend).  Or <a href="https://demo.crossbar.io/">look at these demos</a>. Or <a href="http://crossbario.com/iotcookbook">IoT Cookbook</a>.


## Conclusion


WAMP is a nice, simple protocol, which could be used for real time communication in many different scenarios.  It's very  easy to start to play with it (especially in Python and Javascript) and could be quickly plugged into existing web application.  Or new inventive applications can be created around this protocol.

My only worry for now would be scalability of WAMP solution in massive deployment.

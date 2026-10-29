+++
title = "Functional Fun with Asyncio and Monads"
path = "/functional-fun-with-asyncio-and-monads/"
date = "2016-05-06T18:46:01"
include_in_feeds = true
[extra]
wordpress_id = 1362
kind = "post"
node_key = "1362"
author = "admin"
source_url = "http://zderadicka.eu/functional-fun-with-asyncio-and-monads/"
source_guid = "http://zderadicka.eu/?p=1362"
source_date_gmt = "2016-05-06 17:46:01"
categories = ["Programming"]
tags = ["asyncio", "functional programming", "monad", "python"]
+++
Python 3.4+ provides excellent <a href="https://docs.python.org/3/library/asyncio.html">Asyncio</a> library for asynchronous tasks scheduling and asynchronous I/O operations.   It's similar to <a href="http://www.gevent.org/">gevent</a>, but here tasks are implemented by generator based <a href="https://en.wikipedia.org/wiki/Coroutine">coroutines</a>.  Asynchronous I/O is useful for higher I/O loads, where it usually achieves better performance and scalability then other approaches (threads, processes). About a year ago I played with <a href="https://ocaml.org">OCaml</a>, where light weight threads/ coroutines and asynchronous I/O  approaches  are also very popular (Ocaml has same limitation for threading as Python - a global lock) and there were two great libraries - <a href="http://ocsigen.org/lwt/">lwt</a> and <a href="https://janestreet.github.io/">core async</a>.  Both libraries use monads as a programming style to work with asynchronous tasks. In this article we will try to implement something similar on basis of asyncio library. While our solution will  probably not provide "pure" monads it'll still be fun and we'll learn something about asyncio.<span id="more-1362"></span>

Monad is a term from <a href="https://en.wikipedia.org/wiki/Category_theory">category theory</a>, but mostly it's know by <a href="https://en.wikipedia.org/wiki/Monad_%28functional_programming%29">it's usage</a> in functional programming (in Haskell monads play <a href="https://wiki.haskell.org/Monad">a key role</a> in the language).  I never got into depth of monads theory, but from practical perspective they are quite similar to pipe operator in unix shell - they enable to chain operations together, where result of one operation is fed as input to another operation. For this purpose monads define two functions - `unit` \- which turns some value into monadic type and `bind`, which unpacks value from monadic type, calls a function on it and returns function's result packed as monadic type again. If this is not clear look around for various tutorial about monads (such tutorials were very popular several years ago).

Monads have cool application in asynchronous programming,  because we can use them to express a set of serial tasks - something we would write in shell like:
`cat "something" | task1 | task2 | task3`
This in  monadic terms can be written as: `unit "something"  bind task1 bind task2  bind task3`
If bind is represented as a pipe operator we can achieve same concise syntax as above.

For Javascript programers  this sounds quite similar to Promise -
`fetch('http://something').then(task1).then(task2).then(task3)`
and you are quite right - Promise is 'kind of' monad - see <a href="https://gist.github.com/briancavalier/3296186">here</a>.  Asyncio has similar construct called Future, which we will use later.

Python is multi-paradigm programming language, with a lot of functional features.  So let's see if we can use monadic approach also with asyncio.  This could also serve as a small introduction into asyncio.

We start with this trivial example:


```python
def staight():
    #1st task
    print('Hello')
    #2nd task
    print('World')
    x=10
    #3rd task
    print(x)
    
staight()
```


I assume output of this code would be obvious  (or left as exercise to a reader), more interesting for future comparisons  would be its running time:


```sh
10 loops, best of 3: 8.97 µs per loop
```


Lets try now to implement the same with asyncio (using still python 3.4 syntax, 3.5 syntax  is indeed better, but 3.5 is not yet so common), first some common code:


```python
import asyncio
from asyncio import coroutine as coro
loop=asyncio.get_event_loop()
```


and run those 3 trivial tasks in asyncio loop:


```python
@coro
def s1(x):
    print('Hello')
    
@coro
def s2(x):
    print('World')
    return 10

@coro 
def s3(x):
    print(x)
    
@coro
def run_async():
    yield from s1(None)
    x=yield from s2(None)
    yield from s3(x)
    
loop.run_until_complete(run_async())
```


Same output, much more code, and it runs longer time:


```sh
10 loops, best of 3: 177 µs per loop
```


Asyncio has indeed some overhead - tasks have to be scheduled and then picked by internal event loop. While it's wasteful overhead for this trivial example, it'll make more sense for complex cases  we'll see later.

Now back to monads. Let's create monadic wrapper for asyncio - Async class.  We can use constructor as unit function and our class also implements bind method. Since python is dynamic language, we can use Async for several types - plain values, callables and futures. We also add two overloaded  operators (| and \>\>) to represent the bind function.


```python
import asyncio
import logging
import traceback
logger=logging.getLogger('monadic')

class TaskError(Exception):
    pass

def check_result(f, chained=None):
    if f.exception():
        if chained:
            chained.set_exception(f.exception())
        raise TaskError()
    elif f.cancelled():
        logger.debug('%s was cancelled' % f)
        if chained:
            chained.cancel()
        raise TaskError()
    else:
        return f.result()

def pass_result(resolved,unresolved):
    if resolved.exception():
        unresolved.set_exception(resolved.exception())
    elif resolved.cancelled():
        unresolved.cancel()
    else:
        unresolved.set_result(resolved.result())

def assure_coro_fn(fn_or_coro):
    if asyncio.iscoroutinefunction(fn_or_coro):
        return fn_or_coro
    elif callable(fn_or_coro):
        return asyncio.coroutine(fn_or_coro)
    else:
        raise ValueError('Paremeter is not method, function or coroutine')

class Async(object):
    def __init__(self, work, *args, **kwargs):
        if isinstance(work, asyncio.Future):
            self._future=work
        elif asyncio.iscoroutine(work):
            self._future=asyncio.async(work)
        elif callable(work):
            self._future=asyncio.async(assure_coro_fn(work)(*args, **kwargs))
        else:
            self._future=asyncio.async(asyncio.coroutine(lambda: work)())
        self._chained=None

    def bind(self, next_work):
        next_work=assure_coro_fn(next_work)
        def resolved(f):
            try:
                res=check_result(f, self._chained)
            except TaskError:
                return
            t=asyncio.async(next_work(res))
            t.add_done_callback(lambda f: pass_result(f, new_future))

        new_future=asyncio.Future()
        next_async=Async(new_future)
        self._chained=new_future
        self._future.add_done_callback(resolved)
        return next_async

    def __rshift__(self, other):
        return self.bind(other)

    def __or__(self, other):
        return self.bind(other)

    @property
    def future(self):
        return self._future
```


Actual implementation of unit(constructor) and bind could be fairly simple, but for practical reasons we need to add more code to handle exceptions and cancellations - both have to be propagated through chained operations to the last one.

With our new class we can write (using \>\> operator):


```python
a=Async(lambda: print('Hello')) >> (lambda x: print('World') or 10) >> (lambda x: print('%s'%x))
loop.run_until_complete(a.future)
```


This will add yet some small overhead to execution, but the code is definitely shorter:


```sh
10 loops, best of 3: 316 µs per loop
```


Or we can do do the same with already defined coroutines and pipe operator (same semantic as \>\>, use whatever feels more convenient):


```python
a=Async(s1) | s2 | s3
loop.run_until_complete(a.future)
```


We can also modify our Async class for another great python3 library -  <a href="https://docs.python.org/3/library/concurrent.futures.html">concurrent.futures</a>, which creates asynchronous tasks in either thread or process pool:


```python
import concurrent.futures as cf
import logging
import traceback
logger=logging.getLogger('monadic_cf')

class TaskError(Exception):
    pass

def check_result(f, chained=None):
    if f.exception():
        #logger.error('Exception on future %s' % f.exception())
        if chained:
            chained.set_exception(f.exception())
        raise TaskError()
    elif f.cancelled():
        logger.debug('%s was cancelled' % f)
        if chained:
            chained.cancel()
        raise TaskError()
    else:
        return f.result()

def pass_result(resolved,unresolved):
    if resolved.exception():
        unresolved.set_exception(resolved.exception())
    elif resolved.cancelled():
        unresolved.cancel()
    else:
        unresolved.set_result(resolved.result())


class AsyncCF(object):
    _executor=cf.ThreadPoolExecutor(4)
    def __init__(self, work, *args, **kwargs):
        try:
            self._executor=kwargs.pop('executor')
        except KeyError:
            raise ValueError('Supply executor')
        if isinstance(work, cf.Future):
            self._future=work
        elif callable(work):
            self._future=self._executor.submit(work,*args, **kwargs)
        else:
            self._future=self._executor.submit(lambda: work)
        self._chained=None

    def bind(self, next_work):
        if not callable(next_work):
            raise ValueError('Expected callable')
        def resolved(f):
            try:
                res=check_result(f, self._chained)
            except TaskError:
                return
            t=self._executor.submit(next_work, res)
            t.add_done_callback(lambda f: pass_result(f, new_future))


        new_future=cf.Future()
        next_async=AsyncCF(new_future, executor=self._executor)
        self._chained=new_future
        self._future.add_done_callback(resolved)
        return next_async

    def __rshift__(self, other):
        return self.bind(other)

    def __or__(self, other):
        return self.bind(other)

    @property
    def future(self):
        return self._future

    @property
    def result(self):
        if self._future.exception():
            raise self._future.exception()
        return self._future.result()

    def wait_finished(self):
        cf.wait([self._future])
        return self.result
```


With this class we can write:


```python
ex=cf.ThreadPoolExecutor(4)

a=AsyncCF(lambda: print('Hello'), executor=ex) >> (lambda x: print('World') or 10) >> (lambda x: print('%s'%x))
a.wait_finished()
```


Actual execution  (when thread pool is started) takes approximately same time as in asyncio:


```sh
10 loops, best of 3: 275 µs per loop
```


We can try also process pool - here we have to consider one important limitation -  it can execute only serializable  (by pickle module) objects, so we cannot use lambda or local functions - only top level functions:


```python
ex=cf.ProcessPoolExecutor()

def s1():
    print('Hello')
    
def s2(x):
    print('World')
    return 10

def s3(x):
    print(x)

a=AsyncCF(s1, executor=ex) >> s2 >> s3
a.wait_finished()
```


Process based execution has indeed much higher overhead:


```sh
10 loops, best of 3: 7.56 ms per loop
```


All above examples were very simple - what about something more realistic - consider this task:  get some basic statistics about web servers usage.  For this task we  need to gather N random web sites, make a HEAD request to all of them and collect HTTP Server header from all responses.

Here is the solution in asyncio:


```python
import aiohttp
import asyncio
from collections import Counter
import time

random='http://www.randomwebsite.com/cgi-bin/random.pl'
loop=asyncio.get_event_loop()
w=loop.run_until_complete


@asyncio.coroutine
def header(client, sem, url, name):
    with (yield from sem):
        with aiohttp.Timeout(60):
            resp=yield from client.head(url)
            resp.release()
            return resp.headers.get(name)

@asyncio.coroutine
def count_servers(how_many=100, max_concurrent=100):
    def filter_exc(l):
        return filter(lambda s: not isinstance(s, Exception), l)
    sem=asyncio.Semaphore(max_concurrent)
    
    with aiohttp.ClientSession() as client:
        urls=  yield from asyncio.gather(*map(lambda n: header(client, sem, random, 'location'), range(how_many)), return_exceptions=True)
        urls= filter_exc(urls)
        servers= yield from asyncio.gather(*map(lambda url: header(client, sem, url, 'server'), urls), return_exceptions=True)
        servers=filter_exc(servers)
        servers=map(lambda s: s.split('/')[0] if s else '', servers)
        return Counter(servers)

N=1000
start=time.time()
print (w(count_servers(N)).most_common(10))
print('%d sites took %fsec'%(N,time.time()-start))
```


And result:


```sh
[('Apache', 485), ('nginx', 152), ('Microsoft-IIS', 72), ('', 50), ('cloudflare-nginx', 45), ('GSE', 13), ('DOSarrest', 9), ('LiteSpeed', 8), ('ATS', 4), ('GitHub.com', 4)]
1000 sites took 183.702343sec
```


Apart of assurance that Apache still rules and some people are still using IIS (and surprise by  <a href="https://www.cloudflare.com/">Cloudflare</a> popularity), we see fairly compact, readable and powerful code thanks to asyncio.  There is one special thing to mention -  from perspective of connections handling this asyncio code  is highly parallel - so it basically tries to open all 1000 connections at once.  This can easily lead to "Too many open files" errors- as each socket represents one file handle. We can increase limit of open files per process, but better approach here is to limit number of concurrent request with semaphore.

We can rewrite that code with our Async monadic class:


```python
from monadic import Async
from functools import partial
@asyncio.coroutine
def gather(l):
    return (yield from asyncio.gather(*l, return_exceptions=True))

def count_servers2(how_many=100, max_concurrent=100):
    def filter_exc(l):
        return filter(lambda s: not isinstance(s, Exception), l)
    sem=asyncio.Semaphore(max_concurrent)
    with aiohttp.ClientSession() as client:
        a= Async(how_many) >> range >>  partial(map,lambda n: header(client, sem, random, 'location')) >> \
        gather >> filter_exc >> partial(map,lambda url: header(client, sem, url, 'server')) >> \
        gather >> filter_exc >> partial(map, lambda s: s.split('/')[0] if s else '') >> (lambda l: Counter(l))
        return w(a.future)

N=1000
start=time.time()
print (count_servers2(N).most_common(10))
print('%d sites took %fsec'%(N,time.time()-start))
```




```sh
[('Apache', 502), ('nginx', 169), ('Microsoft-IIS', 81), ('', 38), ('cloudflare-nginx', 38), ('DOSarrest', 15), ('GSE', 13), ('AkamaiGHost', 5), ('Varnish', 4), ('Pepyaka', 4)]
1000 sites took 173.110303sec
```


Similar results, compact functional code ...


### Conclusions


None yet. Just impressed by asyncio and had some functional fun.

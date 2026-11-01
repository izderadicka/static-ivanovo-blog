+++
title = "Asyncio Proxy for Blocking Functions"
path = "/asyncio-proxy-for-blocking-functions/"
date = "2016-09-01T10:49:13"
include_in_feeds = true
[extra]
wordpress_id = 1454
kind = "post"
node_key = "1454"
author = "admin"
source_url = "http://zderadicka.eu/asyncio-proxy-for-blocking-functions/"
source_guid = "http://zderadicka.eu/?p=1454"
source_date_gmt = "2016-09-01 09:49:13"
[taxonomies]
category = ["Programming"]
tag = ["asyncio", "python"]
+++
File operations and other IO operations can block asyncio loop and  unfortunately  python does not support true asynchronous disk operations (mainly due to [problematic state of async disk IO in underlying os - aka linux](http://blog.libtorrent.org/2012/10/asynchronous-disk-io/) \- special library is need for true asynchronous disk operations  so normally select (or other IO event library) always reports file as ready to read and write and thus file IO operations block). Current solution is to run such operations in thread pool executor. There is asyncio wrapper library for file object - [aiofiles](https://github.com/Tinche/aiofiles), but there are also many blocking functions in other python modules - like os, shutil etc.  We can easily write wrappers for such methods, but it can be annoying and time consuming if we use many of such methods.   What about to write a generic proxy, which will assure that methods are executed in thread pool and use this proxy for all potentially blocking methods within the module.<span id="more-1454"></span>

The proxy itself can be fairly simple:


```python
class AsyncProxy(object):
    def __init__(self, module, loop=None, executor = None):
        self._module = module
        self._loop = loop or asyncio.get_event_loop()
        self._executor = executor
        
    def __getattr__(self, name):
        function = getattr(self._module, name)
        if isinstance(function, ModuleType):
            return AsyncProxy(function)
        @wraps(function)
        async def _inner(*args,**kwargs):
            loop = kwargs.pop['loop'] if 'loop' in kwargs else self._loop 
            executor = kwargs['executor'] if 'executor' in kwargs else self._executor
            f = partial(function, *args, **kwargs)
            return await loop.run_in_executor(executor, f)
        return _inner
```


We can use our proxy for os module like this: `aos = AsyncProxy(os)`

And we can test it with `stat` method for instance:


```sh
%timeit loop.run_until_complete(aos.stat('/etc/passwd'))
1000 loops, best of 3: 444 µs per loop
```


How does speed compare with regular call to `os.stat`:


```sh
%timeit os.stat('/etc/passwd')
The slowest run took 20.03 times longer than the fastest. This could mean that an intermediate result is being cached.
1000000 loops, best of 3: 1.69 µs per loop

```


Clearly there is an overhead for running this operation in thread pool (and some small overhead from another level of indirection in proxy) so it's up to implementator to consider if 30 microseconds operation should be considered as blocking  (that's worth case in our test, but what if disk will be really slow, possibly spin-down? That's the problem with most of blocking IO operations - we cannot assume how much they will really take).  However with our approach one can easily change how function is call as blocking or non-blocking - by using os or aos prefix.

+++
title = "How much better is the thread pool?"
path = "/how-much-better-is-the-thread-pool/"
date = "2018-05-15T16:39:24"
include_in_feeds = true
[extra]
wordpress_id = 1882
kind = "post"
node_key = "1882"
author = "admin"
source_url = "http://zderadicka.eu/how-much-better-is-the-thread-pool/"
source_guid = "http://zderadicka.eu/?p=1882"
source_date_gmt = "2018-05-15 15:39:24"
[taxonomies]
category = ["Programming"]
tag = ["performance", "Rust"]
+++
Is thread pool worth to consider for my project?   I was  looking for some opinions around the net and as usual they  differ and most common wisdom is it matters. Generally it's "known" that creating and tearing down thread is "significant" overhead, so if you have a lot of small tasks thread pool is much better solution then spawning new thread for each task.  But what is significant overhead?  According to what I read time to create thread on Linux should be about 10μs (which does not look as too much to me) and app. 2MB of memory allocated for stack (configurable).   I was considering thread pool in context of [audioserve](/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/) project, where I started with simplest possible solution (e.g. spawning individual threads ) and was wondering how much I'm loosing by not using thread pool. So I [implemented simple thread pool](https://github.com/izderadicka/simple-thread-pool) (as learning exercise - long term audioserve solution should use [tokio-threadpool](https://github.com/tokio-rs/tokio/tree/master/tokio-threadpool))  and add it to audioserve.  In the remainder of this short article I'd like to share my findings and  roughly quantify benefits of thread pool for such small project.<span id="more-1882"></span>

audioserve is basically working with local file systems - so tasks are running is separate threads not to block main loop. I used Apache [ab](https://httpd.apache.org/docs/2.4/programs/ab.html)  and [Jmeter](https://jmeter.apache.org/download_jmeter.cgi) tools to test 3 scenarios:



1. ** Quick IO task** - listing of small directory ( 2 items - subdirectories)  - 1000 concurrent requests with ab tool
Here I measured response time -  improvement with thread pool was notable - app.  21% decrease ( 75ms vs 95ms).  Notable difference was also on program size - were version with thread pool was about half size in both virtual and residual memory.
1. **Longer IO task** - listing of bigger directory ( &gt; 100 files, audioserve must also read audio metadata from each file header) -  1000 concurrent requests with ab tool.
As expected in longer tasks there was no significant difference in response time (actually version without pool was about 3% faster), but again program with pool took less memory  - about half.
1. **Complex browsing** scenario with Jmeter
Here Jmeter provides compound index - [APDEX](https://en.wikipedia.org/wiki/Apdex) - reflecting 'user satisfaction'. Here again there was no difference between versions (version with pool only marginally better -  0.946 vs 0.935), but again there we difference in memory consumed by program, similar as in previous cases.



In summary although user will not mention difference in audioserve, version with pool provides some benefits. mainly in saved memory footprint. I also observed improved stability (version without pool dropped connection occasionally).  As thread pool is  relatively easy to implement it worth to consider even for smaller solution like audioserve.

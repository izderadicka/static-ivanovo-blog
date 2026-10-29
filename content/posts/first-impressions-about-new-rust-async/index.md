+++
title = "First Impressions about New Rust Async"
path = "/first-impressions-about-new-rust-async/"
date = "2019-11-24T13:13:15"
include_in_feeds = true
[extra]
wordpress_id = 2136
kind = "post"
node_key = "2136"
author = "admin"
source_url = "http://zderadicka.eu/first-impressions-about-new-rust-async/"
source_guid = "http://zderadicka.eu/?p=2136"
source_date_gmt = "2019-11-24 12:13:15"
categories = ["Programming"]
tags = ["asynchronous I/O", "Rust"]
+++
Just recently `async` and `await` made it to stable version of Rust. `futures` library 0.3 is also out and rest of other important libraries is following - for me `tokio` and `hyper` are particularly interesting. `tokio` is now in alpha stage supporting new futures, so I decided it's about a time to give it a try. Some time ago I've <a aria-label=" (opens in a new tab)" href="/asynchronous-again-rewriting-ptunnel-in-rust/" rel="noreferrer noopener" target="_blank">rewritten ptunnel in Rus</a>t using 0.1 version of `tokio` and `futures`.  So here are my first experiences with new libraries and upgrade.




<span id="more-2136"></span>




`ptunnel` is simple program which tunnels local connections through HTTP proxy (through HTTP CONNECT method). As it just forwards bytes back and forth, asynchronous programming is ideal for maximal throughput and minimal resources used. So I was wondering if I can get some more improvements with new tokio.






Before coding I looked a bit around Internet and found <a href="https://tikv.org/blog/client-futures/">this article</a> useful (many finding there where confirmed by my efforts). Also there is a <a href="https://rust-lang.github.io/futures-rs/blog/2019/04/18/compatibility-layer.html">compatibility layer</a> to use old and new futures together, but fortunately I did not need backward compatibility.






I started with updating dependencies and removing some outdated. Great news is that new `tokio` has already asynchronous DNS resolution built in so no external library was needed.  Changes in libraries version immediately lead to something like ~60 errors in code (and those were the easier ones, most tricky problems - related to lifetime and ownership compilers saves to the last minute, you fix seemingly last error and whoa-la - new and tougher errors pop up).      






So I started to go through code. Biggest change is difference in Future type  where  Future now returns one generic `Output` associated type , instead of Result with two associated types. Indeed you can use result too here, but type signature is different. Also signature of Futute's `poll` method changed - self reference is now pinned and there is second parameter - `Context`.  It also means that all Result oriented combinators like `and_then`, `map_or` ... disappeared from basic Future (but are available on `TryFutureExt` trait).  Future trait itself split into two basic one `Future` and `FutureExt` with all combinators.






Other big change  is new `async` functions and blocks and `await` keyword. They are absolutely cool, with their help you can simplify code significantly. Also using them  limits need for future combinators  and explicit use of Future type, so it also helped greatly with first problem during changes.






Also runtime API changed a lot - as I've been using explicit runtime initialization , I had to look for new API, but generally it's nice and clean.






One of biggest issues I have was that some things I used are recently hidden behind features so it took me some time to realize that and use correct dependency version (latest git) with full features.  Also current thread executor seems to have <a href="https://github.com/tokio-rs/tokio/issues/1818">some issues</a> now. But overall I was able to migrate to new code after half day or so.






New code is much more cleaner and I was able to get rid of some unnecessary wrapper code in my previous version (where I use Future to process CONNECT header, now it can be done more easily with async/await). async/await programming style is much closer to what I'm used to from python/javascript, which one huge advantage - static checks - if you forget to await, you'll get compile time error.






And how new code performs? In past article I was measuring throughput with `ab` tool (in setup ab \<-\> ptunnel \<-\> squid \<-\> nginx on local host) and got about 0.31ms per request (on larger number of requests on keep-alive connections). Now in similar setup I've got 0.067ms, so about 4 times better, which is quite nice.






So overall quite positive experience, now I'll wait a bit until new tokio and hyper will get stable and will look into my other project <a href="/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/">audioserve</a>, which is much bigger, so much more work expected. I wish stable versions were available two years back when I started it, but as it's being said "repetitio est mater studiorum".

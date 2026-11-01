+++
title = "Ocaml performance - native code vs byte code"
path = "/ocaml-performance-native-code-vs-byte-code/"
date = "2014-09-08T18:09:54"
include_in_feeds = true
[extra]
wordpress_id = 811
kind = "post"
node_key = "811"
author = "admin"
source_url = "http://zderadicka.eu/ocaml-performance-native-code-vs-byte-code/"
source_guid = "http://zderadicka.eu/?p=811"
source_date_gmt = "2014-09-08 17:09:54"
[taxonomies]
category = ["Programming"]
tag = ["OCaml"]
+++
As noted in <a href="/learning-ocaml/" title="Learning OCAML">this post</a> I've been exploring OCaml language. OCaml  is a compiled language and can be compiled either to native code (for supported platforms) or to byte code, which runs interpreted in provided run-time environment. I was wondering, what is performance difference between these two target codes.<span id="more-811"></span>

To get some basic idea I prepared simple benchmark based on some test code, I've created as part of my learning exercise -   [QuadTree](http://en.wikipedia.org/wiki/Quadtree) implementation in OCaml.  QuadTree is used to represent a set of 17k plus cities in US.
Benchmark task is to get all cities within 50km from coordinates  -87.6, 41.8.   To compare QuadTree search performance there is also basic 'brute-force' algorithm.  Loading of data and Quad tree construction is not included into the benchmark, it's limited to searching routine only. Benchmark in done on 64 bit Linux on Core i5 @ 2.7GHz notebook. Exactly same tests were run for native and byte code with these results:

Byte code:


```sh
┌────────────────────┬──────────┬─────────┬──────────┬──────────┬─────────┐
│ Name               │ Time/Run │ mWd/Run │ mjWd/Run │ Prom/Run │ mGC/Run │
├────────────────────┼──────────┼─────────┼──────────┼──────────┼─────────┤
│ Brute force search │ 241.87ms │ 12.35Mw │   4.04kw │   4.04kw │   47.12 │
│ Qtree search       │  48.89ms │  1.14Mw │   3.36kw │   3.36kw │    4.34 │
└────────────────────┴──────────┴─────────┴──────────┴──────────┴─────────┘

```


Native code:


```sh
┌────────────────────┬──────────┬─────────┬──────────┬──────────┬─────────┬──────────┐
│ Name               │ Time/Run │ mWd/Run │ mjWd/Run │ Prom/Run │ mGC/Run │ mjGC/Run │
├────────────────────┼──────────┼─────────┼──────────┼──────────┼─────────┼──────────┤
│ Brute force search │ 110.96ms │  6.35Mw │   3.07kw │   3.07kw │   24.22 │          │
│ Qtree search       │   5.88ms │  1.03Mw │   3.07kw │   3.07kw │    3.93 │  0.65e-3 │
└────────────────────┴──────────┴─────────┴──────────┴──────────┴─────────┴──────────┘

```




### Conclusions


As expected native code is faster.   Interesting is that actual gain is dependent on type of task -  Quadtree search, which leverages much more Ocaml structures is faster by factor of 8,  while simpler code for brute-force search if faster only by factor of 2. Also interesting is that heap allocations and garbage collections  (all other columns apart of first one) are slightly different for both codes (again preferring native code).


### Another test


More recently I've been playing with my learning project (distributed map-reduce), which is bit more complex, using Core and Async libraries -  here difference between native and bytecode was 15 secs vs 35 secs (for word count sample) - so native code was more then  2 x faster.

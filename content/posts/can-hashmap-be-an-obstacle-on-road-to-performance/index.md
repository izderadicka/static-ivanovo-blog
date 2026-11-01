+++
title = "Can Hashmap Be An Obstacle on Road to Performance"
path = "/can-hashmap-be-an-obstacle-on-road-to-performance/"
date = "2020-04-02T13:45:32"
include_in_feeds = true
[extra]
wordpress_id = 2225
kind = "post"
node_key = "2225"
author = "admin"
source_url = "http://zderadicka.eu/can-hashmap-be-an-obstacle-on-road-to-performance/"
source_guid = "http://zderadicka.eu/?p=2225"
source_date_gmt = "2020-04-02 12:45:32"
[taxonomies]
category = ["Programming"]
tag = ["performance", "Rust"]
+++
I'm still playing with small exercises, one interesting is "[alphametics](https://en.wikipedia.org/wiki/Verbal_arithmetic)"  (it's available on [exercism](https://exercism.io)). Exercise goal is  to evaluate if an expression like "SEND + MORE == MONEY", when letters are replaced uniquely with numbers, is valid equation (more details in link above). As I have written in [previous article](/performance-should-matter/), I try to think about performance and this exercise was quite interesting from that perspective.




<span id="more-2225"></span>




My initial solution was based on brute force approach, searching for all possible assignments of numbers to present letters - it did work, but it was slower then "best" solution, which was searching for solution per columns - e.g. first find solutions for "D+E == Y" (with possible carry over), then test them with next columns - this should reduce search space. So I modified code to similar approach (although with bit more explicit code) - the code is available on github - branch [normal-hash](https://github.com/izderadicka/alphametics/tree/normal-hash) (for the competing solution see src/other.rs).






I did benchmark comparing to the other solution , but still my code was slower (unfortunately  I have to do  benchmarks in VM (Virtual Box), where variance is much higher then on regular linux installation, but mean value should be OK, as I have checked in previous benchmarks, bench is running hundreds of iterations):






```
 test mine  … bench: 1,673,078,653 ns/iter (+/- 1,223,832,876)
 test other … bench: 497,544,602 ns/iter (+/- 121,667,843)
```






As you can see mine is about 3 times slower (not looking much at variance). So when something is slower then required it's time for performance profiling. In past I used `valgrind callgrind`, but for this case I decided to use `perf` \-  especially because I found nice article how to use it for creating [flame graphs](http://www.brendangregg.com/flamegraphs.html), which is cool way how to visualize call graph and how individual functions consume CPU time. So join me on journey to better performance.






Here are commands to record call graph and then  create a nice flame chart (install perf [FlameGraph](https://github.com/brendangregg/FlameGraph) tools - create links to appropriate scripts to `~/.local/bin` so we can use these scripts easily):






```bash
sudo perf record -g --call-graph dwarf target/debug/examples/ten; sudo chmod a+r perf.data
perf script | stackcollapse-perf | flamegraph > flame0.svg
```






And below is the result - flame0.svg picture (picture is actually interactive, but, you have to open it in separate window by right clicking on it and choosing View Image):






<figure class="wp-block-image"><img alt="" class="wp-image-2230" decoding="async" loading="eager" src="/wp-content/uploads/flame0.svg"/><figcaption>Flame Graph for solution with default hash function</figcaption></figure>






I really do like these flame graphs, because they give you nice overview of CPU time allocation over whole program in one picture, which you can easily see on screen.  Here we can see that majority of work is divided between `Combinator` (later renamed as Permutator) iterator (which generates all possible permutations of numbers assignment to letters )and  `Column::evaluate`, which checks if given permutation is valid (summands adds to correct value).  






Hashmaps are omnipresent data containers and some languages like Python are build around them (class is hashmap, instance is hashmap) and they are also intensively used in this exercise. If we look little bit higher in flash graph, into those "hills", we see that majority of time in spent in hashmap operations.  






So this brings us back to the title of this article - significant part of time is spent in hashmap - it looks like here hashmap is really an obstacle  to reaching better performance. So how to fix this - Rust is known to have rather complex default hash function, which prevents against DOS attacks, but we probably do not need it here. Let's replace it (as hash functions are pluggable) with something faster from crate `fasthash` (quite indicative name, right, we do want fast hash here) and it is [seahash](https://docs.rs/fasthash/0.4.0/fasthash/sea/index.html), which advertise itself as "A bizarrely fast hash function". Modified exercise code is [here](https://github.com/izderadicka/alphametics/tree/fast-hash). And here are benchmark results:






```
 test mine  … bench: 1,310,181,847 ns/iter (+/- 279,684,550)
 test other … bench:    414,885,580 ns/iter (+/- 23,982,803)
```






Not much difference, actually (barely on the edge of results variance - but as I said variance is little bit higher, as tested in virtual machine, when sometimes VM just sits and waits, so few cases get unusually high timing). Let also look at flame graph:






<figure class="wp-block-image"><img alt="" class="wp-image-2231" decoding="async" loading="lazy" src="/wp-content/uploads/flame.svg"/><figcaption>Flame Graph with faster hasher</figcaption></figure>






It's looks kind of similar to previous case, right? But let's look at details - part  where hashmap is looking up for values: 






<figure class="wp-block-image"><img alt="" class="wp-image-2243" decoding="async" loading="lazy" sizes="(max-width: 1024px) 100vw, 1024px" src="/wp-content/uploads/hasher-1-1024x340.png" srcset="/wp-content/uploads/hasher-1-1024x340.png 1024w, /wp-content/uploads/hasher-1-300x99.png 300w, /wp-content/uploads/hasher-1-768x255.png 768w, /wp-content/uploads/hasher-1.png 1185w"/><figcaption>Comparing default hasher (SIP) to SeaHash</figcaption></figure>






Areas highlighted by blue lasso are parts of code, where I think actual hash calculation is done. So we can see that Seahash is faster, but it's not enough to make significant difference. Some more radical changes are needed. If we look at above flame graphs, we see that there is still quite some overhead related to hashmap machinery.  As we are mapping char to byte and chars are ASCII only we actually are mapping byte to byte - so we can represent this as 256 bytes long array - index is a key and array cell a value. So let's try it - code is [here](https://github.com/izderadicka/alphametics) and array is actually implemented as `Vec` and it's wrapped in simple map and set interfaces, so it fits well into existing code. So does this version perform:






```
 test mine  … bench: 158,229,699 ns/iter (+/- 46,468,825)
 test other … bench: 411,004,920 ns/iter (+/- 68,749,867)
```






Voila - we are there, finally, mine version is faster and we can go out for beer (or we could if there would not be fu....g corona virus out there,  pubs are closed:-).  Here is flame graph for completeness:






<figure class="wp-block-image"><img alt="" class="wp-image-2232" decoding="async" loading="lazy" src="/wp-content/uploads/flame2.svg"/><figcaption>Flame Graph for final solution with minimalist map </figcaption></figure>






As you can see (right click, View image to explore), cpu time is spent now elsewhere. Some part is relatedto  vector creation - so what if we use fixed arrays rather then vector? Array is simpler, sits on stack (in this case), so it should be faster, right? But actually it's quite opposite, just by changing `Vec<u8>` to `[u8;256]` (in `fastmap::FastMap` ) we made code about 2x slower (sorry do not have measurements),  so it brings us finally to to first commandment of performance engineering - always measure!

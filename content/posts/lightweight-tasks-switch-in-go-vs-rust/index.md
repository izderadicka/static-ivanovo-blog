+++
title = "Lightweight Tasks Switch in Go vs Rust"
path = "/lightweight-tasks-switch-in-go-vs-rust/"
date = "2019-06-13T17:36:32"
include_in_feeds = true
[extra]
wordpress_id = 2092
kind = "post"
node_key = "2092"
author = "admin"
source_url = "http://zderadicka.eu/lightweight-tasks-switch-in-go-vs-rust/"
source_guid = "http://zderadicka.eu/?p=2092"
source_date_gmt = "2019-06-13 16:36:32"
[taxonomies]
category = ["Programming"]
tag = ["Go", "Rust"]
+++
I've have been following this excellent book "[Operating Systems: Three Easy Pieces](http://pages.cs.wisc.edu/~remzi/OSTEP/)" and as I've been doing a homework - measuring time of context switch and as I was looking around and found another interesting [article](https://eli.thegreenplace.net/2018/measuring-context-switching-and-memory-overheads-for-linux-threads/) related to this topic. It also compares thread switches to switches in "Go routines" - lightweight threads in Go language. Base on these sources I'm made couple of mine own test (yes I know, all benchmarks sucks, but nevertheless they are somehow attractive (as gossips are) and somehow addictive).




<span id="more-2092"></span>




Ok, so first couple of few findings . I've made process context switch measurements in C (as requested in the homework) and then in Rust (using nix crate) - they both showed same numbers (good, once again I was confirmed that Rust can achieve same performance as C code) - resulting around 2.5 µs per process context switch on my notebook. 






Then I tried the same with threads, instead of processes, and numbers were almost the same. That make sense, as I guess context switch is kind of similar for processes and threads - save registers, restore registers. 






But latter article also compared thread context switch to switch between Go routines (aka lightweight threads, green threads, cooperative routines/tasks), which was significantly faster (app. about order of magnitude). This again make sense, as switch between cooperative routines is done in user space and does not need to switch whole thread context, as routines can run in same thread. 






Being a Rust fan I wondered how it would compare - in Rust we have some similar concepts (of cooperative tasks)  in [tokio](https://github.com/tokio-rs/tokio). So original Go benchark code was (funny highlight for Go is missing, somebody does not like Google):






```text
// Ping ponging messages between two goroutines on a channel, measuring number
// of messages sent per second. This should be roughly equivalent to the
// thread-pipe-msgpersec.c benchmark.
//
// Eli Bendersky [http://eli.thegreenplace.net]
// This code is in the public domain.
package main

import (
	"fmt"
	"time"
)

// child takes a channel c and loops over messages in it until it's closed,
// echoing all the messages back into the channel.
func child(c chan string) {
	for msg := range c {
		if len(msg) != 4 {
			panic("unexpected message length")
		}
		c <- msg
	}
}

func main() {
	c := make(chan string)
	go child(c)

	t1 := time.Now()
	const niters = 2000000
	for i := 0; i < niters; i++ {
		c <- "joe0"
		reply := <-c
		if "joe0" != reply {
			panic("oh no, mismatch")
		}
	}
	elapsed := time.Since(t1)

	fmt.Printf("%d iterations took %d ns. %.2f iters/sec\n",
		niters, elapsed.Nanoseconds(),
		1e9*niters/float64(elapsed.Nanoseconds()))
}


```






And here is similar (as far as my understanding is going) code in Rust: 






```rust
use tokio::prelude::*;
use tokio::runtime;
use futures::sync::mpsc;
use std::time;

const ITERATIONS: i64 = 2_000_000;
const MSG:&str = "joe0";
fn main() {
    let mut rt =runtime::current_thread::Runtime::new().unwrap();
    const BUF_SIZE: usize = 0;
    let (w1,r1) = mpsc::channel::<&str>(BUF_SIZE);
    let (w2,r2) = mpsc::channel::<&str>(BUF_SIZE);

    let repeater = r1.forward(w2.sink_map_err(|e| eprintln!("Error {}",e)))
    .map(|_| ());
    rt.spawn(repeater);

    let sender = stream::iter_ok(0..ITERATIONS).map(|_| MSG)
    .forward(w1.sink_map_err(|e| eprintln!("Error {}",e)))
    .map(|_| ());

    rt.spawn(sender);
    let receiver = r2.fold(0, |a, i| if i == MSG {Ok(a+1)} else {Err(())});

    let start = time::Instant::now();
    let res = rt.block_on(receiver).unwrap();
    let dur = start.elapsed().as_nanos();
    assert_eq!(ITERATIONS, res);
    println!("{} iterations took {} ns. {:0.2} iters/sec\n",
    ITERATIONS,
    dur, 
    1e9 * ITERATIONS as f64/ dur as f64);
}
```






And results were (on my notebook with Ubuntu 16.04 Desktop and 4 Cores Intel i5 @ 2.4 Ghz):






Go:<br/>`2000000 iterations took 905413631 ns. 2208935.16 iters/sec`






Rust:<br/>`2000000 iterations took 3985478440 ns. 501821.81 iters/sec`






I also tried thread pool executor (just delete`  ::current_thread ` from source), where tasks should be executed on different OS threads, my expectation was that it would be slower, due to threads context switches and results confirmed by expectations:<br/>`2000000 iterations took 4727579594 ns. 423049.46 iters/sec`






However Rust test was kind of artificial (as noted in comments below), I forced channel buffer to be of size 0, which means tasks had to switch after each message send/receive, which is probably quite inefficient (but fair as to go example comparison). What if we use some reasonable buffer size like 4k  Below is result running on single threaded executor:<br/>`2000000 iterations took 403409172 ns. 4957745.48 iters/sec`<br/>And also result for thread pool executor:<br/>`2000000 iterations took 1412270057 ns. 1416159.74 iters/sec`<br/>Slowdown here for thread pool executor is even more notable, not exactly sure why.






Now to be fair to Go let's slightly modify the program and add also 4k  buffer to channel (just changing channel creation to `make(chan string, 4096)` ).<br/>And results are:<br/>`2000000 iterations took 881620329 ns. 2268550.23 iters/sec`<br/>Surprisingly almost no difference (maybe some optimization is already being done in background?).






## Conclusions






 It's always tricky to benchmark for performance, as one should know perfectly what he's doing and compare to right things. In this case it's rather toy comparison (but at least I run each test several times to assure that presented numbers do not have too high variance) , so do not take numbers too seriously, as noted in comments below go routines and tokio tasks are after all fairly different. But on the other hand they provide similar concepts to us programmers, so I just felt curious about comparison between them.






What we learned:







- for many small tasks,  tokio thread pool executor added some overhead so current_thread executor preformed better
- Looking purely at overhead with task/routine switch (enforced by blocking channels) Go looks better
- But when looking for performance, one must look for appropriate solution - channels with buffering preform much better in Rust.







There is couple of weird  things I do not completely understand. First huge slowdown for buffered channel in thread pool executor (in Rust) and second why adding buffer to channel in Go does not make any difference. So I'm definitely interested in your comments.

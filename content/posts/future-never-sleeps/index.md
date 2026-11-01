+++
title = "Future Never Sleeps"
path = "/future-never-sleeps/"
date = "2018-10-07T11:02:09"
include_in_feeds = true
[extra]
wordpress_id = 1943
kind = "post"
node_key = "1943"
author = "admin"
source_url = "http://zderadicka.eu/future-never-sleeps/"
source_guid = "http://zderadicka.eu/?p=1943"
source_date_gmt = "2018-10-07 10:02:09"
[taxonomies]
category = ["Programming"]
tag = ["Futures", "Rust"]
+++
Recently I've been reading this book:  ["Network Programming with Rust" by Abhishek Chanda](https://www.packtpub.com/application-development/network-programming-rust). I found this book bit problematic. It's just collection of many unrelated examples (often taken from crates documentation), with just little of background and concepts explanation and in some parts this book is just wrong, in other parts it's using too much simplifications, so the result does not make much sense or worst it introduces some dangerous ideas. One of these  places is part about futures and streams - let's look at one example:<span id="more-1943"></span>


```rust
// ch7/streams/src/main.rs

extern crate futures;
extern crate rand;

use std::{io, thread};
use std::time::Duration;
use futures::stream::Stream;
use futures::{Poll, Async};
use rand::{thread_rng, Rng};
use futures::Future;

// This struct holds the current state and the end condition
// for the stream
#[derive(Debug)]
struct CollatzStream {
    current: u64,
    end: u64,
}

// A constructor to initialize the struct with defaults
impl CollatzStream {
    fn new(start: u64) -> CollatzStream {
        CollatzStream {
            current: start,
            end: 1
        }
    }
}

// Implementation of the Stream trait for our struct
impl Stream for CollatzStream {
    type Item = u64;
    type Error = io::Error;
    fn poll(&mut self) -> Poll<Option<Self::Item>, io::Error> {
        let d = thread_rng().gen_range::<u64>(1, 5);
        thread::sleep(Duration::from_secs(d));
        if self.current % 2 == 0 {
            self.current = self.current / 2;
        } else {
            self.current = 3 * self.current + 1;
        }
        if self.current == self.end {
            Ok(Async::Ready(None))
        } else {
            Ok(Async::Ready(Some(self.current)))
        }
    }
}

fn main() {
    let stream = CollatzStream::new(10);
    let f = stream.for_each(|num| {
        println!("{}", num);
        Ok(())
    });
    f.wait().ok();
}
```


As you can see on line 37 above the poll method is blocked by `thread::sleep` \- the author explanation is :

<em>**"We simulate a delay in returning the result by sleeping for a random amount of time between 1 and 5 seconds."**</em>

But this is wrong, very wrong, going against very basic principle of asynchronous  programing and Futures in Rust.  Because what is happening here is that whole event loop is blocked and no other `Future` can progress. Future's `poll` method should never block, rather it should return`  Async::NotReady ` to indicate that it cannot proceed and also schedule next poll for later time, when it expects it could proceed.

So as an exercise I tried to create proper implementation, probably bit simplistic and suboptimal (for proper delay in futures look for instance at [tokio-timer](https://github.com/tokio-rs/tokio/tree/master/tokio-timer) crate).

So here is the code:


```rust
extern crate futures;
extern crate rand;
#[macro_use]
extern crate lazy_static;

use futures::stream::Stream;
use futures::Future;
use futures::{task, Async, Poll};
use rand::{thread_rng, Rng};
use std::cmp::Ordering;
use std::collections::BinaryHeap;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

enum Never {}

struct TaskEntry {
    task: futures::task::Task,
    wake_at: Instant,
}

impl TaskEntry {
    fn new(instant: Instant) -> Self {
        TaskEntry {
            task: task::current(),
            wake_at: instant,
        }
    }
}

impl PartialEq for TaskEntry {
    fn eq(&self, other: &Self) -> bool {
        self.wake_at == other.wake_at
    }
}

impl Eq for TaskEntry {}

impl PartialOrd for TaskEntry {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        other.wake_at.partial_cmp(&self.wake_at)
    }
}

impl Ord for TaskEntry {
    fn cmp(&self, other: &Self) -> Ordering {
        other.wake_at.cmp(&self.wake_at)
    }
}

enum WaitTime {
    Forever,
    None,
    Some(Duration),
}

struct Waker {
    thread: thread::JoinHandle<()>,
    tasks: Arc<Mutex<BinaryHeap<TaskEntry>>>,
}

lazy_static! {
    static ref GLOBAL_WAKER: Waker = Waker::new();
}

impl Waker {
    fn new() -> Self {
        let tasks = Arc::new(Mutex::new(BinaryHeap::new()));
        let tasks2 = tasks.clone();
        let thread = thread::spawn(move || loop {
            let sleep_time = {
                let mut tasks = tasks2.lock().unwrap();
                let time = match tasks.peek() {
                    None => WaitTime::Forever,
                    Some(TaskEntry { wake_at, .. }) => {
                        let now = Instant::now();
                        if *wake_at > now {
                            WaitTime::Some(*wake_at - now)
                        } else {
                            WaitTime::None
                        }
                    }
                };

                if let WaitTime::None = time {
                    let t = tasks.pop();
                    if let Some(task_entry) = t {
                        task_entry.task.notify()
                    }
                };
                time
            };

            match sleep_time {
                WaitTime::None => (),
                WaitTime::Forever => thread::park(),
                WaitTime::Some(d) => thread::park_timeout(d),
            }
        });

        Waker { tasks, thread }
    }

    fn wake_me_at(&self, time: Instant) {
        let mut tasks = self.tasks.lock().unwrap();
        tasks.push(TaskEntry::new(time));
        self.thread.thread().unpark()
    }
}

#[derive(Debug)]
enum Delay {
    Fixed(u64),
    Random(u64, u64),
}

#[derive(Debug)]
struct Sleeper {
    next_instant: Option<Instant>,
    delay: Delay,
}

impl Sleeper {
    fn new(delay: Delay) -> Self {
        Sleeper {
            next_instant: None,
            delay,
        }
    }

    fn poll_sleep(&mut self) -> Poll<(), Never> {
        let should_wait = match self.next_instant {
            None => {
                let now = Instant::now();
                use Delay::*;
                let delay = match self.delay {
                    Fixed(fixed) => fixed,
                    Random(low, high) => thread_rng().gen_range::<u64>(low, high),
                };
                self.next_instant = Some(now + Duration::from_millis(delay));
                true
            }
            Some(i) => {
                if i <= Instant::now() {
                    self.next_instant.take();
                    false
                } else {
                    true
                }
            }
        };

        if should_wait {
            GLOBAL_WAKER.wake_me_at(self.next_instant.unwrap());
            return Ok(Async::NotReady);
        }

        Ok(Async::Ready(()))
    }
}

macro_rules! poll_sleeper {
    ($sleeper:expr) => {
        match $sleeper.poll_sleep() {
            Ok(Async::NotReady) => return Ok(Async::NotReady),
            Ok(Async::Ready(_)) => (),
            Err(_) => unreachable!(),
        }
    };
}

#[derive(Debug)]
struct CollatzStream {
    current: u64,
    end: u64,
    sleeper: Sleeper,
}

impl CollatzStream {
    fn new(start: u64) -> CollatzStream {
        CollatzStream {
            current: start,
            end: 1,
            sleeper: Sleeper::new(Delay::Random(1000, 5000)),
        }
    }
}

impl Stream for CollatzStream {
    type Item = u64;
    type Error = Never;
    fn poll(&mut self) -> Poll<Option<Self::Item>, Never> {
        poll_sleeper!(self.sleeper);

        if self.current % 2 == 0 {
            self.current = self.current / 2;
        } else {
            self.current = 3 * self.current + 1;
        }
        if self.current == self.end {
            Ok(Async::Ready(None))
        } else {
            Ok(Async::Ready(Some(self.current)))
        }
    }
}

struct Ticker {
    ticks: u64,
    sleeper: Sleeper,
}

impl Ticker {
    fn new(ticks: u64) -> Self {
        Ticker {
            ticks,
            sleeper: Sleeper::new(Delay::Fixed(100)),
        }
    }
}

impl Stream for Ticker {
    type Item = ();
    type Error = Never;

    fn poll(&mut self) -> Poll<Option<Self::Item>, Self::Error> {
        poll_sleeper!(self.sleeper);
        if self.ticks > 0 {
            self.ticks -= 1;
            Ok(Async::Ready(Some(())))
        } else {
            Ok(Async::Ready(None))
        }
    }
}

fn main() {
    let stream = CollatzStream::new(10);
    let f = stream.for_each(|num| {
        println!("{}", num);
        Ok(())
    });
    let t = Ticker::new(100).for_each(|_| {
        println!("Tick");
        Ok(())
    });
    let r = f.join(t);
    r.wait().ok();
}

```


 

It's indeed much longer then previous example and majority of code in there is about asynchronous delay.  We have there two streams - `CollatzStream` \- same as in previous example (with random delays before producing value) and then another stream `Ticker`, which provides unit value every 100 ms - just to demonstrate that both streams are running asynchronously.

Then we have two supporting structures `Sleeper` and `Waker` \- to enable proper asynchronous sleeps in our streams.  `Sleeper` sleeps for given delay, returning `Async::NotReady` when sleeping, then `Async::Ready(())` after sleep period and then going to sleep again. Waker registers sleeping futures and wakes them in an appropriate time. `Waker` is using binary heap to keep references to sleeping futures ordered by their planned wake up time (futures are here represented by their tasks) and runs background thread to wake always nearest task  - schedule it for next poll (with `task.notify` method).

So as can be seen by comparing original example with fixed one, too much simplification is sometimes dangerous, it can introduce false ideas and confuse the underlying principles rather then to clarify them.

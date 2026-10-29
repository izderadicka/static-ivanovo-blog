+++
title = "Clone or Reference Count - Which One Is Faster"
path = "/clone-or-reference-count-which-one-is-faster/"
date = "2020-03-22T15:47:41"
include_in_feeds = true
[extra]
wordpress_id = 2207
kind = "post"
node_key = "2207"
author = "admin"
source_url = "http://zderadicka.eu/clone-or-reference-count-which-one-is-faster/"
source_guid = "http://zderadicka.eu/?p=2207"
source_date_gmt = "2020-03-22 14:47:41"
categories = ["Programming"]
tags = ["Rust"]
+++
While I was updating <a href="https://github.com/izderadicka/audioserve">audioserve </a>I hit one part of code, when I was passing a not so big structure (containing data for authentication) to asynchronous task (in tokio multi-threaded executor), as task might run potentially in different thread it has to have static lifetime. Easiest solution was to clone  the structure and move it to thread (which was  original solution). But during refactoring I realized that reference count - `Arc` type could be better solution - it can save a small piece of memory (Arc is 8 bytes), but  also it could perform better (or could not?). To check my later assumption I've run couple of of tests.




<span id="more-2207"></span>




Here is code for the  plain structure and its reference counted wrapper:






```rust
use std::sync::Arc;

#[derive(Debug, Clone)]
pub struct Secrets {
    shared_secret: String,
    server_secret: Vec<u8>,
    token_validity_hours: u32,
}

impl Secrets {
    pub fn sample() -> Self {
        Secrets {
            shared_secret: "kulisak_jede".into(),
            server_secret: b"01234567890123456789012345678901".to_vec(),
            token_validity_hours: 24*100
        }
    }
}

#[derive(Clone, Debug)]
pub struct SharedSecrets{
    inner: Arc<Secrets>
}

impl SharedSecrets {
    pub fn sample() -> Self {
        SharedSecrets{
            inner: Arc::new(Secrets::sample())
        }
    }
}
```






Now let's try simplest benchmark - pass physical clone (copying memory) or pass reference counted smart pointer. Former is called uninventively `test_cloned` latter confusingly `test_shared`:






```rust
#[bench]
fn test_cloned(b: &mut test::Bencher) {
    b.iter(|| {
        let s = Secrets::sample();
        for _i in 0..LOOPS {
            let c  = s.clone();
        }
    })
}

#[bench]
fn test_shared(b: &mut test::Bencher) {
    b.iter(|| {
        let s = SharedSecrets::sample();
        for i in 0..LOOPS {
            let c  = s.clone();
        }
    })
}
```






Now to benchmark results for 1M loops:






```
 test test_cloned          … bench:  67,909,930 ns/iter (+/- 1,036,866)
 test test_shared          … bench:  12,129,636 ns/iter (+/- 334,998) 
```






OK, that was expected right?.  `Arc` is faster then copying memory, even when struct size is rather small - ~ 100 bytes. But question is - how much is this just a toy benchmark  I've tested also on other newer machine and I saw same trend there , but actual difference was much smaller( about half - probably due to faster memory?).






But that was not the way how you normally pass value  - main use case for `Arc` is pass reference to threads. So how does it look like for this scenario:






```rust
 #[bench]
fn test_threaded_cloned(b: &mut test::Bencher) {
    b.iter(|| {
        let s = Secrets::sample();
        let mut threads = vec![];
        for i in 0..THREADS {
            let c  = s.clone();
            threads.push(thread::spawn(move || {
                let x = c;
            }));

        }
        for t in threads {
            t.join().unwrap();
        }
    })
}

#[bench]
fn test_threaded_shared(b: &mut test::Bencher) {
    b.iter(|| {
        let s = SharedSecrets::sample();
        let mut threads = vec![];
        for i in 0..THREADS {
            let c  = s.clone();
            threads.push(thread::spawn(move || {
                let x = c;
            }));

        }
        for t in threads {
            t.join().unwrap();
        }
    })
}
```






And results for 1000 threads (we cannot normally run 1M threads, unless modifying kernel parameters  - remember 10K connections problem? ). As threads have significant overhead, 1000 of them will be enough for our another toy benchmark:






```
 test test_threaded_cloned … bench:  29,858,099 ns/iter (+/- 415,199)
 test test_threaded_shared … bench:  29,651,799 ns/iter (+/- 345,890)
```






So as you can see threads overhead completely hides difference. 






But what about tokio and threadpool - the problem of clone or reference count difference initially  arisen when I was passing values to tokio tasks. So lets try something like this:






```rust
#[bench]
fn test_tokio_shared(b: &mut test::Bencher) {
    let mut rt = Builder::new()
        .threaded_scheduler()
        .build().unwrap();
    b.iter(|| {
        let s = SharedSecrets::sample();
        let mut threads = vec![];
        for _i in 0..TASKS {
            let c  = s.clone();
            threads.push(rt.spawn(async move {
                let x = c;
            }));

        }
        rt.block_on( async {
            for t in threads {
                t.await.unwrap();
            }
        })
        
    })
}

#[bench]
fn test_tokio_cloned(b: &mut test::Bencher) {
    let mut rt = Builder::new()
        .threaded_scheduler()
        .build().unwrap();
    b.iter(|| {
        let s = Secrets::sample();
        let mut threads = vec![];
        for _i in 0..TASKS {
            let c  = s.clone();
            threads.push(rt.spawn(async move {
                let x = c;
            }));

        }
        rt.block_on( async {
            for t in threads {
                t.await.unwrap();
            }
        })
        
    })
}
```






And run 10 000 of tokio tasks on a threadpool:






```
 test test_tokio_cloned    … bench:   6,174,117 ns/iter (+/- 297,534)
 test test_tokio_shared    … bench:   5,730,147 ns/iter (+/- 275,639)
```






Some small difference is visible in favor of `Arc` (based on previous results it was expected).






Finally let's do some baseline measurement - what if we do not copy memory (`test_word_cloned`),  but just value on stack, or pass `Arc` reference (`test_word_shared`), or  pass `Rc` reference (`test_word_shared_rc`). I had to modify code to add bit more work, otherwise first case was so optimized that it was not executed at all (probably as duration was 0 ns).






```rust
#[bench]
fn test_word_cloned(b: &mut test::Bencher) {
    b.iter(|| {
        let s = 24u64;
        let mut acc = 0;
        for _i in 0..LOOPS {
            let c  = s.clone();
            acc+= c;
        }
        println!("{}", acc);

    })
}

#[bench]
fn test_word_shared(b: &mut test::Bencher) {
    b.iter(|| {
        let s = std::sync::Arc::new(24u64);
        let mut acc = 0;
        for _i in 0..LOOPS {
            let c  = *s.clone();
            acc+=c;
        }
        println!("{}", acc);

    })
}

#[bench]
fn test_word_shared_rc(b: &mut test::Bencher) {
    b.iter(|| {
        let s = std::rc::Rc::new(24u64);
        let mut acc = 0;
        for _i in 0..LOOPS {
            let c  = *s.clone();
            acc+=c;
        }
        println!("{}", acc);

    })
}
```






And results for 1M of loops:






```
 test test_word_cloned     … bench:         112 ns/iter (+/- 5)
 test test_word_shared     … bench:  12,131,404 ns/iter (+/- 338,120)
 test test_word_shared_rc  … bench:      10,790 ns/iter (+/- 466)
```






Reference counting is very significantly more expensive, then just copying trivial value  (`u64`). And `Arc` is significantly more expensive to `Rc`.






## Conclusions






So it looks like `Arc` could be little bit faster for my use case, so I use it now in my code instead of cloning the structure.

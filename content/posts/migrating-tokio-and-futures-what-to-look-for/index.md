+++
title = "Migrating Tokio and Futures - What to Look for"
path = "/migrating-tokio-and-futures-what-to-look-for/"
date = "2020-03-15T10:33:44"
include_in_feeds = true
[extra]
wordpress_id = 2188
kind = "post"
node_key = "2188"
author = "admin"
source_url = "http://zderadicka.eu/migrating-tokio-and-futures-what-to-look-for/"
source_guid = "http://zderadicka.eu/?p=2188"
source_date_gmt = "2020-03-15 09:33:44"
[taxonomies]
category = ["Programming"]
tag = ["Futures", "Rust"]
+++
I've finally found courage to look after migrating audioserve to new hyper and tokio and futures crates. As new futures (0.3) are significantly different from previous version, mainly due to support of async/await keywords, I was expecting significant effort, so I was kind of delaying it. Now when it's almost done, I'd like to reflect a bit on the effort. Firstly - it was not as bad as expected (although after updating cargo dependencies I've got about a hundred of errors). Secondly - there are some patterns to follow in migration, which I've like to describe further in the article.




<span id="more-2188"></span>




##  Future traits






Most notable change happened in Future trait, associated type and method signature are different, so probably this is a first thing to start with - wherever you use `Future` or `Stream` in types you should rewrite them. Old future had two associated types (one for successful result, one for error), new future has just one (which make probably more sense, because not all futures have to resolve to error too, one can have future that just always resolves to success value).  So obvious replacement in migration is to use `Result` as future `Output` type - so you will keep you existing  semantic of future results.






Also the content of `Future` trait change dramatically - now it contains only basic poll method and combinator  methods moved to new traits `FutureExt` and `TryFutureExt` (later contains methods related to futures resolving into `Result` \- like `and_then` `map_err` and others). Also `IntoFuture` trait is gone - so some combinators like `and_then` or  `or_else` must return result future - not just result itself.<br/>Similar situation is for `Stream` ( with additional traits `StreamExt` and `TryStreamExt`). Bit different situation is with   `Sink`, where `Item` moved from associated type to generic type parameter (all combinators are in `SinkExt` trait). To use combinator method appropriate trait has to be brought into context. One can import `use futures::prelude::*` to get all common traits imported.






##   Implementing Future






If your code has types implementing `Future`, you will have more work now. This is due to change in poll method signature, `Future` looks now:






```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context) -> Poll<Self::Output>;
}
```






Key change is  pinning self. It's done to assure that self is not moved in memory  in cases when it's self-referencing some of it's own parts. This was introduced especially for `async`/`await` blocks, where self- referencing is common (short explanation of Pin is [here](https://rust-lang.github.io/async-book/04_pinning/01_chapter.html)). <br/>So Future implementation has to be rewritten, if your future is `Unpin` then actually implementation is quite the same, as `Pin` implements `DerefMut` for `Unpin` targets. So you work with `self` in quite same way.  As `Unpin` is common for majority of types I was able to make my custom futures and streams `Unpin` too.






Other aspect is when your future is polling another future, which is very common, now we have to wrap reference into `Pin`, again for `Unpin` types it's trivial- `Pin::new`, for other types which are not `Unpin` you can fix them in memory - easiest way is to allocate on heap and pin - `Box::pin`, which will make resulting type `Pin<Box<T>>`, which is `Unpin`.  If your future stores child futures, stored them pinned, it'll be most convenient.






## Future Trait Object






I hit interesting problem when migrating `Future` trait objects, initially I used same approach as in old code, which is illustrated in code below:






```rust
use futures::{future::{ready}, prelude::*};// 0.3.4
use tokio; // 0.2.11

#[tokio::main]
async fn main() {
    let f: Box<dyn Future<Output=u32>> = Box::new(ready(1));
    
    let f = f.map(|v| {
    println!("Got value {}", v);
    v+1
    }
    );
    
    let x = f.await;
    println!("DONE {:?}", x);
    
}
```






But I've got this strange error:






```
 error: the `map` method cannot be invoked on a trait object  
--> src/main.rs:8:15  
  | 
8 |     let f = f.map(|v| { 
  |               ^^^   | help: another candidate was found in the following trait, perhaps add a `use` for it: 
  |
1 | use futures_util::future::future::FutureExt;  
  | 
```






`FutureExt` trait is for sure imported from `futures::prelude`, so what's going on?






It turns out that problem  is again related to `Unpin` \- `Future` trait is only implemented for `Box<dyn Future + Unpin>` \-  and `FutureExt` requires `Future` \- so  that why our type cannot use map method. Solution is rather simple - either add `Unpin` trait or even better use `Pin<Box` which does implement `Future` as illustrated below:






```rust
use futures::{future::{ready}, prelude::*};// 0.3.4
use tokio; // 0.2.11
use std::pin::Pin;

#[tokio::main]
async fn main() {
    let f: Pin<Box<dyn Future<Output=u32>>> = Box::pin(ready(1));
    
    let f = f.map(|v| {
    println!("Got value {}", v);
    v+1
    }
    );
    
    let x = f.await;
    println!("DONE {:?}", x);
    
}
```






## async and await






`async` and `await` keywords are really great improvement for writing asynchronous code. It does simplify code notably and it's a lot easier to write it (I already mentioned it [in this article](/first-impressions-about-new-rust-async/)). 






I did not covert all code to async/await (partially due to laziness, partially just did not want to touch  things that worked well and does make sense). However some parts - like asynchronous file access with `tokio::fs` required rewrite - while in past file object was owned by  future ( resulting from operation like read) and moved to future result , now mutable reference shared with future is used so chaining futures was more difficult - but quite obvious when rewritten in `async` block. 






## Recap






<ol><li>Use <code>futures::prelude::&#42;</code> to import all useful traits, including Ext traits</li><li>Update references to <code>Future</code> and <code>Steam</code> traits- new ones should have one associated type <code>Result</code>, which contains success and error type of old future.</li><li>  Update your implementations of futures, streams, etc. Try to make them <code>Unpin</code> - it will make you life easier. If they have inner futures, store them pinned.  <code>Box::pin</code> is you friend to make future <code>Unpin</code> (but requires allocation).</li><li>Use <code>Box::pin</code> for you <code>Future</code> (or <code>Stream</code>)  trait objects</li><li>Rewrite code to **async/await **where necessary: too complex combinators,  new futures require mutable reference etc.</li></ol>

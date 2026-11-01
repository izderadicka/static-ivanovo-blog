+++
title = "Higher Rank Trait Bounds in Practice"
path = "/higher-rank/"
date = "2019-09-16T15:58:51"
include_in_feeds = true
[extra]
wordpress_id = 2112
kind = "post"
node_key = "2112"
author = "admin"
source_url = "http://zderadicka.eu/higher-rank/"
source_guid = "http://zderadicka.eu/?p=2112"
source_date_gmt = "2019-09-16 14:58:51"
[taxonomies]
category = ["Programming"]
tag = ["Rust"]
+++
Higher Rank Trait Bounds (HRTB) is relatively advanced feature in Rust, you can read short explanation in the [reference](https://doc.rust-lang.org/reference/trait-bounds.html#higher-ranked-trait-bounds), and more detailed  explanation in in [the RFC](https://github.com/rust-lang/rfcs/blob/master/text/0387-higher-ranked-trait-bounds.md) (frankly spoken RFC is bit more complicated, at least for me).






HRTBs are applied for lifetime parameters only (at least now) and are useful in cases where lifetime parameter in trait cannot be bound to any existing lifetime, but is valid for any particular lifetime, that happen to appear in place where type implementing the trait is used.




<span id="more-2112"></span>




Typical example (similar to what is used in above linked articles), which is most common case for usage of HRTB  is an higher order function implementation (higher order function = function that takes another function/closure as an parameter):






<script src="https://gist.github.com/rust-play/2763b14ea58494ba2fec2c422c9d4a9b.js"></script>






Above is typical use of HRTB - the `f` parameter of `apply` function can take function, which itself has a parameter, that is an reference and has some lifetime. But what is exact lifetime of this parameter? It clearly does not relate to lifetime of  the `struct` that implements the trait, but it stand on its own - it works for any lifetime, which is supplied to `f` \- so that's why `for<'a>` is used here. Actually compiler makes it easy for us, because in these "obvious" cases it just elides this HRTB lifetime as expected (as you can see in the code above explicit and implicit definitions are equivalent). 






However you can meet HRTB also in other circumstances, where it needs to be declared explicitly.  I was testing small program (below is quite simplified version) , where I have a trait for `Checksum` that represents checksum calculator and defines function `calc` that calculates  checksum for some input. Then I implemented several algorithms for inputs that implement `Read` trait (file, bytes slice ...),  and program can dynamically  choose one (based on user input or other conditions).  So this is a classical OOP polymorphism problem of having several implementations of given interface and dynamically deciding, which one to use.  In Rust we have trait objects for this purpose.   I sought it would be rather straightforward code, but I hit interesting problem with lifetimes, which needed to be resolved by explicit usage of HRTB. Here is final code:  






<script src="https://gist.github.com/rust-play/33ca4a67829c48c25b79aff83f4f07d8.js"></script>






As you can see I had to use HRTB on line 48.  Because if you do not use HRTB and line 48 looks just like this:






```rust
let mut checker: Box<dyn Checksum<& [u8]>> = if rand::random() {
```






You'll get following error (and I needed help from Rust community to really understand what's going  on):






```
error[E0502]: cannot borrow `buf` as mutable because it is also borrowed as immutable
  --> src/main.rs:63:32
   |
63 |     let chunk_size = data.read(&mut buf).unwrap();
   |                                ^^^^^^^^ mutable borrow occurs here
64 |     if chunk_size == 0 { break }
65 |     let cs = checker.calc(&buf[..chunk_size]);
   |              -------       --- immutable borrow occurs here
   |              |
   |              immutable borrow later used here

```






As `Checksum` type parameter has now one (yet unmatched) lifetime,  compiler tries to derive it from the code. It sees that `checker.calc` is used in the loop and takes `&buf` shared reference.  As compiler does not know (lifetime analysis is local and done on function signatures bases only), what exactly `checker` will do with this reference, it assumes "worst case", e.g. that `checker` can keep this reference for duration of the loop. So in next iteration it sees that `data.read` needs unique (`mut`) reference to buf, but it's not possible because `checker` already has shared reference. So that's why we got this error.






On the other hand, if we use `for<'a>` HRTB construct (on line 48) compiler knows, that checker should be OK for all lifetimes of its type parameter, so even if it's borrowed just for lifetime of `checker.calc` call as intended here.  So now compiler is satisfied and compiles the code. 






You can use this[ rust playground link](https://play.rust-lang.org/?version=nightly&mode=debug&edition=2018&gist=33ca4a67829c48c25b79aff83f4f07d8) to play with code yourself (for instance if you remove loop then HTRB is not needed) .

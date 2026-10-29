+++
title = "In RUST We Trust"
path = "/in-rust-we-trust/"
date = "2017-05-24T16:34:34"
include_in_feeds = true
[extra]
wordpress_id = 1592
kind = "post"
node_key = "1592"
author = "admin"
source_url = "http://zderadicka.eu/in-rust-we-trust/"
source_guid = "http://zderadicka.eu/?p=1592"
source_date_gmt = "2017-05-24 15:34:34"
categories = ["Programming"]
tags = ["Rust"]
+++
Having been programing recently mostly in dynamic untyped languages (aka Python and JavaScript) I though that it would be nice to try something else, bit different -  meaning compiled and statically typed. Last adventures in this area were with OCAML, which I used for few learning projects couple years ago( like this <a href="/ocaml-ocsigen-i-ching-and-web-applications/">one</a>).  OCAML is very nice language indeed, and learning exercise was very valuable for me (especially getting more accustomed to functional programming style),  but apart  of that learning experience I did not follow it  further (mainly due limited ecosystem of OCAML).

Looking recently to <a href="https://stackoverflow.com/insights/survey/2017#most-loved-dreaded-and-wanted">languages and technology survey on Stackoverflow</a>  where <a href="https://www.rust-lang.org/en-US/">Rust</a> is leading the list of most "loved" languages (meaning developers who used the language like it and want to use it for their next projects) with head start on   second one (<a href="https://en.wikipedia.org/wiki/Smalltalk">SmallTalk</a>) .   This caught my attention and looking quickly at Rust site I decided to give it a try.  Below are my first experiences learning this language.<span id="more-1592"></span>


## Learning RUST


Rust borrows concepts from many established languages (C/C++ like syntax and primitive types, Ocaml/Haskel like type system with algebraic types and  generic types, interfaces (called traits here) and functional features - closures, higher order functions, immutability by default, etc.)  and adds few new concepts (ownership, borrowing, lifetimes) - the result is quite interesting, but not exactly easy to learn, so I'd recommend to starts with some  books (It actually helped me to read about some new concepts in few different books, because each book had bit different approach):
"<a href="http://rust-lang.github.io/book/second-edition/index.html">The Rust Programing Language 2nd Edition</a>" - is the official RUST book from Mozzilla team, 2nd edition is completely rewritten (but yet not fully complete)  and it's much easier for a beginner to comprehend  then <a href="http://rust-lang.github.io/book/first-edition/index.html">1st edition</a>,  so I'd recommend to start with this one.
"<a href="http://shop.oreilly.com/product/0636920040385.do">Programming Rust</a>" by Jim Blandy; Jason Orendorff, published by O'Reilly,   currently available as pre-relase only,  but should be published soon by now. Also very nice introductory book,  going bit more in depth on some topics that are just touched in previous book  ( chap. 19), but which, in my opinion, are very much needed in real programming.

Apart of these two books I've found these three resources extremely useful:
"<a href="http://rustbyexample.com/">Rust by example</a>" - online examples for various RUST features, which can be interactively run and modified.  Great to quickly check basic concepts.
"<a href="http://cglab.ca/~abeinges/blah/too-many-lists/book/">Learning Rust With Entirely Too Many Linked Lists</a>"  is great RUST tutorial, where you are learning Rust as you are building various linked lists.  I liked author approach of try-and-fail experiments, which very much reminded me my struggle with first programs (binary sorted tree etc.).  By  trying some obvious approaches, failing them and explaining what went wrong, author clearly demonstrated some key features of RUST and some not so obvious issues with the code (releasing lists for instance).
"<a href="https://zsiciarz.github.io/24daysofrust/index.html">24 Days of Rust</a>" by Zbigniew Siciarz, language is not only about it's syntax, semantics and core library, but also about whole ecosystem of available libraries, in this online book author walks us through numerous more or less popular Rust third party libraries (the number of currently available Rust libraries is surprisingly high considering short history of the language) .


## Tools


<a href="https://www.rust-lang.org/en-US/install.html">Installation</a> of core Rust tools is piece of cake. `Rustup` utility enables us to have several versions of Rust tool chain, it's particularly useful to have latest "nightly" build around, because Rust is still evolving very rapidly and some newer features are available now only in nightly.

Key tool you will interact with is is <a href="https://crates.io/">cargo</a> \- it's Rust package manager, build manager and test runner, all in one. It's very nice and intuitive tool, I was able to use  it immediately, without any issues.

Concerning editors -  Rust has support for many common editors including Vim, Emacs, Atom, Sublime3  and Eclipse. However finally I've found that most comfortable editor (at least for my learning exercises) was <a href="https://code.visualstudio.com/">Visual Studio Code</a> with <a href="https://github.com/editor-rs/vscode-rust">Rust for Visual Studio Code</a> extension configured to use <a href="https://github.com/rust-lang-nursery/rls">Rust Language Server</a> ( although RLS is in alpha stage, it works reasonably well, with occasional hiccups - like when using undo in editor - luckily restart of RLS is very easy - just click on status bar).


## Experiences


Rust is advertised as system programming language, that is intrinsically safe and provide zero-cost higher level abstractions.    I do not have very much experiences with system programming,  so I can rather compare to my previous experiences (Python, C#, Java, Ocaml, JS).  Interesting is the notion about zero-cost abstractions -   it basically means that you can use some seemingly higher level abstractions  - like iterators or generic types, but they are implemented very efficiently, as if you'd write code in traditional system language - C/C++.

Overall experiences are positive - Rust  feels as very modern language, with many progressive features we've seen in other languages in past years.  I personally like these features from first sight:


<ul>
<li>Type system is very powerful, few picks:
<ul>
<li><code> Option</code> (to represent types with potentially no value, this is great tool to overcome notorious Null errors)</li>
<li><code>Result</code> (to represent error in processing, Rust does not use exceptions)</li>
<li>Traits can implement new behavior for existing types ( something we can do in Javascript with prototype manipulation, but here in Rust it's completely type safe)</li>
</ul>
</li>
<li>Iterators are super powerful in Rust - we have all higher level functions from functional languages and more</li>
<li>Closures - closures syntax is very concise, it plays very well in higher order functions</li>
<li>Testing is integrated into core language - you can write unit tests directly within source file, they will compile only if you run them with <code>cargo test</code> command, but you can also you write separate test files (so called integration tests).</li>
<li>Pattern matching is great for productivity and code readability</li>
<li>Parallel processing is very easy with Rust -  apart of classical threads (which are mapped to OS threads, so limitations of Python, OCAML etc.  and which enjoy improved safety of Rust language ,so it's much easier to use them) there are also build-in channels for threads communication and some great third party libraries like <a href="https://github.com/nikomatsakis/rayon">rayon</a>, which turns regular iterator into parallel iterator, where individual items are process concurrently in multiple threads ( all this with just one method call - <code>par&#95;iter()</code> - it's absolutely amazing!).</li>
</ul>


Concerning expressiveness of the language, here is one quick example - following function finds value in URL query string by it's key, returns default, if the key is not found:


```rust
fn extract_qs<T:FromStr+Copy>(path: &str, name: &str, default: T) -> T {
    let mut url="http:".to_string();
    url+=path;
    Url::parse(&url)
        .ok()
        .and_then(|url| {
                      url.query_pairs()
                          .find(|pair| pair.0 == name)
                          .map(|n| T::from_str(&n.1).unwrap_or(default))
                  })
        .unwrap_or(default)
}
```


The function takes path with query string and returns value of one query string parameter identified by name or some default value.  Key concept to illustrate here is usage of higher order functions like `map`, `find`, `and_then` .   Function is doing basically this - first it normalizes path to URL (with an arbitrary scheme, absolute URL is needed for next function), then   function `Url::parse` returns `Result`, which represents parsed url or error. We ignore error with `ok()` method (turn it into `Option` type, so error becomes None). If Option has value, we iterate through all query string pairs, find one with right name and try to convert it to output type. If we do not find it or cannot convert its value from string, we use default value.  If we know roughly semantics of used methods, then whole intent of this function is pretty clear and reads almost as easily as human language sentence.  And all possible failures (malformed query string, missing key, invalid value in query string)  are already handled ( here by returning default value).   You can also mention that this function is  using generics, so it'll work for any type that can be parsed from string and copied - which are basically all primitive types like integer, float, boolean.

However not all things in Rust are so nice and easy going as I described above.  Here I mean particularly Rust very special features <a href="http://rust-lang.github.io/book/second-edition/ch04-00-understanding-ownership.html">Ownership, Borrowing and Lifetimes</a> \-  all these three features are very closely interrelated and are embedded  in very core of Rust language, so you meet them practically on every line of your code.    For me, at least initially, it was quite hard to cope with them, because they somehow contradicted with my current experiences and intuition. Errors like "value does not live long enough", "cannot borrow", "use of moved value" were omnipresent.  Luckily compiler provided very detailed error messages, often with advice, how problem can be resolved (which I think is quite unique),  so after some trials and failures and I was able to progress in majority of cases.

The ownership rules could be pretty limiting in some cases and may require you to rethink your design from scratch or to look for more advanced features of the language like reference counting  or internally mutable cells (not to speaking about unsafe code, which I try to avoid for now).  The compiler component, responsible for ownership rules, is called "the borrow checker"  (abbreviated often familiarly as TFBC - you may guess what F stands for). During my experiments the borrow checker often drove me mad and it took quite a while to understand what it's complaining about. Then usually two resolutions arose -   either the "Yes, of course" revelation - when I understood what was the issue and fix was obvious and quick,   or "Oh no, not this", when I realized that my approach was completely wrong and I had to start from scratch.   Now I know bit more, so I'm able to prevent some basic issues, but this aspect of Rust is still painful for me and it'll require more time to get right intuition here.

There are a tons of positive great things in Rust, but sometimes it also could be pretty hard and definitely it's not a programing language that can be learned 'quickly' (whatever quickly means to you).   In these <a href="https://www.youtube.com/watch?v=8EPsnf_ZYU0&amp;list=PLo3w8EB99pqJ74XIGe72c9hBZWz9Y16cY">advertising videos</a> prepared by Mozilla one guy said, "Come to Rust and you'll feel like you suddenly have superpowers", I have to admit that often rather I felt that I'm superstupid. But overall feeling now is positive and I'd like to try more small projects in Rust.


## My Toy Rust Project


The only way how I can learn anything about new language is to try to write some code over and over again, staring with simple code (exercises from books, few obvious algorithms and data structures like quick-sort or binary tree etc.) and gradually progressing to more complex stuff. Presenting those overused exercises would definitely be not interesting, so I created one small toy project called <a href="https://github.com/izderadicka/langgen">Bilbo Babbit Babbles</a> \-  which generates nonsensical sentences using trigram model from arbitrary plain text documents (defining language corpus).

If you'd like to try it you can easily build docker image from <a href="https://github.com/izderadicka/langgen/blob/master/deploy/Dockerfile">this file</a>. Or it's also online <a href="http://bbb.zderadicka.eu">here</a>.

So as final words of this article I use the sentence generated by this program (using collected Sherlock Holmes works from A.C. Doyle as language corpus):


<div class="panel-body" id="panel-result"><em>"Six thousand a year so what had caused me to make an occasional ten-pound note upon a patched Dunlop."</em></div>

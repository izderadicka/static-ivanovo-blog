+++
title = "From Ignorance to Enlightenment -  Playing with Tokio"
path = "/from-ignorance-to-enlightenment-playing-with-tokio/"
date = "2018-06-01T08:37:44"
include_in_feeds = true
[extra]
wordpress_id = 1888
kind = "post"
node_key = "1888"
author = "admin"
source_url = "http://zderadicka.eu/from-ignorance-to-enlightenment-playing-with-tokio/"
source_guid = "http://zderadicka.eu/?p=1888"
source_date_gmt = "2018-06-01 07:37:44"
categories = ["Programming"]
tags = ["asynchronous I/O", "Rust", "tokio"]
+++
I have been playing with <a href="https://tokio.rs/">tokio</a> already in couple of small projects (<a href="/asynchronous-again-rewriting-ptunnel-in-rust/">ptunnel-rust</a> and indirectly (via hyper) in <a href="/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/">audioserve</a>), but I cannot say that I'm proficient.  Also tokio is very much moving target -  what I used couple month ago is already bit outdated now(old version is <a href="https://github.com/tokio-rs/tokio-core">tokio_core</a> crate - where default executor was on current thread, now it's work stealing thread pool). So I decided to refresh and deepen my knowledge and created a toy project -  <strong>stupid jokes server</strong> \-  it's a TCP sever, which sends a random  joke to client after it connects and then closes connection. Jokes are stored in text file, separated by dashed lines.  My main interest was to test how to use local file system I/Os, which are blocking by nature, with tokio asynchronous approach (so I initially skipped easiest and probably most efficient implementation, where all jokes would be cached in memory).  Usually in a real project you'll have some blocking code, so I need to know how to handle it. This article is history of my attempts (and failures) recorded in a hope that it might help others in learning tokio (and also writing it down helped me to absorb gained knowledge). <span id="more-1888"></span>


# Prelude


In order to send random jokes from a file, we need to index file first into  Index type


```rust
type Index = Vec<(usize, usize)>;
```


which is just vector of line numbers - start of the joke and end of the joke.  We fill it at server startup in pretty convenient synchronous way:


```rust
fn create_index<P: AsRef<Path>>(f: P) -> Result<Index, std::io::Error> {
    let reader = BufReader::new(File::open(f)?);
    let mut start: Option<usize> = None;
    let mut idx = vec![];
    for (no, line) in reader.lines().enumerate() {
        match line {
            Ok(l) => {
                if l.starts_with("---") {
                    if let Some(s) = start {
                        //println!("joke from {} to {}", s, no);
                        idx.push((s, no));
                    }
                    start = Some(no + 1)
                }
            }

            Err(e) => eprintln!("Error reading line {}: {}", no, e),
        }
    }
    Ok(idx)
}
```


 

Also we should have some code to start tokio runtime - as new runtime is configurable, we use it to start runtime with custom number of threads  and thread life time:


```rust
fn create_runtime() -> Result<tokio::runtime::Runtime, io::Error> {
    let mut tp_builder = tokio_threadpool::Builder::new();
    tp_builder
        .name_prefix("ttest-worker-")
        .pool_size(8)
        .keep_alive(Some(Duration::from_secs(60)));

    tokio::runtime::Builder::new()
        .threadpool_builder(tp_builder)
        .build()
}
```


So main function then looks like this:


```rust
fn main() {
    let jokes_file = match env::args().nth(1) {
        Some(s) => s,
        None => {
            eprintln!("text file is required as first argument");
            return;
        }
    };
    let idx = create_index(&jokes_file).unwrap();
    let idx = Arc::new(idx);

    let addr = "127.0.0.1:12345".parse().unwrap();
    let server = prepare_server(addr, jokes_file.into(), idx);

    let mut rt = create_runtime().unwrap();

    rt.spawn(server.map_err(|e| eprintln!("Server error {}", e)));
    rt.shutdown_on_idle().wait().unwrap()
}
```


So the only thing left is function `prepare_server`, which will contain server logic - generate random number  smaller then number of jokes and then get staring and ending line numbers from the index and send lines within this range to client - this should be easy peasy, right?


# ACT I. - Head First


Ok first try  - read joke, send it :


```rust
fn prepare_server(
    addr: std::net::SocketAddr,
    file_name: PathBuf,
    idx: Index,
) -> Box<Future<Item = (), Error = io::Error> + Send> {
    println!("Starting at {}", &addr);
    let tcp = TcpListener::bind(&addr).unwrap();

    let server = tcp.incoming().for_each(move |socket| {
        println!("Received connection from {}", socket.peer_addr().unwrap());
        
        let i = rand::thread_rng().gen_range(0, idx.len());
        let (from, to) = idx[i];
        println!("Sending joke from lines: {} - {}", from, to);
        let reader = BufReader::new(File::open(&file_name).unwrap());
        let joke: Vec<_> = reader
            .lines()
            .skip(from)
            .take(to - from)
            .filter(|r| r.is_ok())
            .map(|s| s.unwrap())
            .filter_map(|l| {
                let s = l.trim_left();
                if s.len() > 1 {
                    Some(s.to_owned())
                   
                } else {
                None
                }
            })
            .collect();

        let mut text = joke.join("\n");
        text.push_str("\n");
        let write_future= io::write_all(socket, text)
        .then(|res| {
            println!("Written joke -result is Ok {:?}",res.is_ok());
            Ok(())
        });
```


Is it working? Yes - at least appears so - we can try `nc localhost 12345` and we will get a joke.

Is it nice? Somehow - notice my nice iterator - I'm getting really used to them.

Some gotchas:

\- When returning boxed Future it also needs to mark it with `Send` trait, otherwise we get error when using it in runtime. Runtime takes only futures that have Send, as it'll execute them in different threads.

\- Initially I though that I'll need to use Arc wrapper for the index, but it turns out, that it's not needed , as it can be moved to closure.

\- tokio spawn requires future with both Item and Error to be of unit type. However write\_all returns Future with different types. So need to chain new future with correct types using `then` function.

Is it good asynchronous code? Not at all. We are using blocking functions like File::open or .skip,  .lines in asynchronous task. It's bad. It works because I was lucky - the operations are not blocking for long (especially when file is cached by OS after first reads) and runtime thread pool provides some level of concurrency already, so it's not so fatal if some threads block. But we can do better, right?


# ACT II. Tokio Threadpool Helps


Previous code uses blocking calls - is there anything in tokio that can handle blocking calls?  Actually there are couple possibilities possibilities:

\- Spawn blocking code in separate thread, if there are many of such cases, use thread pool.
\- Or use asynchronous library, if such is available - and there is tokio-fs library, which enables asynchronous work with files.

I will try both approaches and see were I'll get. As jokes are supposed to be  distributed is large quantities (as everybody likes stupid jokes) we will probably need a thread pool. There are couple of thread pools implementations around (I also have written <a href="/how-much-better-is-the-thread-pool/">simple one to test with audioserve</a>). But wait - tokio provide also thread pool, which is already used to run tokio tasks.  Could not we use it to to run our blocking code?  And it looks like we can -<a href="https://tokio-rs.github.io/tokio/tokio_threadpool/index.html"> tokio-threadpool</a> provides function <a href="https://tokio-rs.github.io/tokio/tokio_threadpool/fn.blocking.html">blocking</a>, which can surround blocking code and handle it.  So lets try it:


```rust
fn prepare_server(
    addr: std::net::SocketAddr,
    file_name: PathBuf,
    idx: Arc<Index>,
) -> Box<Future<Item = (), Error = io::Error> + Send> {
    println!("Starting at {}", &addr);
    let tcp = TcpListener::bind(&addr).unwrap();

    let server = tcp.incoming().for_each(move |socket| {
        println!("Received connection from {}", socket.peer_addr().unwrap());
        let file_name = file_name.clone();
        let idx = idx.clone();
        let work_future = poll_fn(move || {
            blocking(|| {
                let i = rand::thread_rng().gen_range(0, idx.len());
                let (from, to) = idx[i];
                println!("Sending joke from lines: {} - {}", from, to);
                let reader = BufReader::new(File::open(&file_name).unwrap());
                let joke: Vec<_> = reader
                    .lines()
                    .skip(from)
                    .take(to - from)
                    .filter(|r| r.is_ok())
                    .map(|s| s.unwrap())
                    .filter_map(|l| {
                        let s = l.trim_left();
                        if s.len() > 1 {
                            Some(s.to_owned())
                        } else {
                            None
                        }
                    })
                    .collect();

                let mut text = joke.join("\n");
                text.push_str("\n");
                text
            })
        });
        let write_future = work_future
            .map_err(|_| std::io::Error::new(std::io::ErrorKind::Other, "Blocking Error"))
            .and_then(|text| {
                //println!("Joke is {}", text);
                io::write_all(socket, text)
            })
            .then(|res| {
                println!("Written joke -result is Ok {:?}", res.is_ok());
                Ok(())
            });

        tokio::spawn(write_future);

        Ok(())
    });

    Box::new(server)
}
```


Does it work - yes.

Is it nice code - yes - it's almost same as the previous one. With couple more lines.

Gotchas:

\- Error mapping - we still need to be aware of error types, as chained futures require same Error type.  Here it was easiest to map BlockingError from blocking function to io::Error (it required just one mapping).

\- `blocking` function does not actually returns Future, but polling function (more about polling later) - to turn it into Future we need another function`  poll_fn `

\- as now we get two closures nested we cannot move some values directly, but have to clone them (otherwise we got error "cannot move out of captured outer variable in an \`FnMut\` closure" ).

Is it good asynchronous code? Not yet. Recommended approach for asynchronous code is to split work into many small tasks. So in our case we would like to send text lines as soon as we get them. But we can do that, right?


# Act III. Borrow Checker Fights Back


Tokio also provides Streams - they are similar to Iterators, but asynchronous - we already use an iterator, so we can try to turn it into stream. Actually there is a function for it ` iter_ok,  `so it should be very easy to implement:


```rust
fn prepare_server(
    addr: std::net::SocketAddr,
    file_name: PathBuf,
    idx: Arc<Index>,
) -> Box<Future<Item = (), Error = io::Error> + Send> {
    println!("Starting at {}", &addr);
    let tcp = match TcpListener::bind(&addr) {
        Ok(t) => t,
        Err(e) => return Box::new(err(e)),
    };

    let server = tcp.incoming().for_each(move |socket| {
        println!("Received connection from {}", socket.peer_addr().unwrap());
        let file_name = file_name.clone();
        let idx = idx.clone();
        let lines_future = poll_fn(move || {
            blocking(|| {
                let i = rand::thread_rng().gen_range(0, idx.len());
                let (from, to) = idx[i];
                println!("Sending joke from lines: {} - {}", from, to);
                let reader = BufReader::new(File::open(&file_name).unwrap());
                let joke_iter = reader
                    .lines()
                    .skip(from)
                    .take(to - from)
                    .filter(|r| r.is_ok())
                    .map(|s| s.unwrap())
                    .filter_map(|l| {
                        let s = l.trim_left();
                        if s.len() > 0 {
                            let mut l = s.to_owned();
                            l.push_str("\n");
                            Some(l)
                        } else {
                            None
                        }
                    });

                iter_ok::<_, ()>(joke_iter)
            })
        });

        let write_future = lines_future
            .map_err(|_| ())
            .and_then(move |lines_stream| {
                lines_stream.for_each(move |line|{
                     io::write_all(socket, line)
                     .then(|_| Ok(()))
                })
            })
            .then(|res| {
                println!("Written joke -result is Ok {:?}", res.is_ok());
                Ok(())
            });

        tokio::spawn(write_future);

        Ok(())
    });
```


Ouch - this code does not compile thanks to the error on line 47  - write\_all requires ownership of socket, but it cannot be moved out from captured context. So now what? But we can find some solution, right?


# Interlude - Rusty Futures


Tokio is using Rust <a href="https://crates.io/crates/futures">futures</a> crate heavily, so it's necessary to have good understanding of how futures works, especially their combinators, so let's start with them.

Future is a representation of value that will be available later, but we need some reference to it now. Most commonly known "future" is probably Javascript Promise -  it has two basic combinators - `then` (containing function, which is executed when value becomes available)   and `catch` (which contains error handling function). Rust contains similar combinators and few more (check <a href="https://tokio.rs/img/diagrams/cheatsheet-for-futures.html">futures combinators cheatsheat</a>). Combinators are true essence of asynchronous programing, you create small pieces of code and then glue them together to required logic with appropriate combinators.

Combinators can be used on exiting futures, but sometimes a new future needs to be created from scratch. In Javascript Promise is created by passing function which calls either `resolve` or `reject`.  Rust futures <a href="https://aturon.github.io/blog/2016/09/07/futures-design/">are bit different</a> \- as explained in the linked article Rust futures are "readiness based" - meaning runtime is waking/polling future,  when  relevant events occurred (bytes comes into socket, timer fires ...) and the future decides if it has enough data and can resolve itself, or still needs more.  This decision is done in one function  `poll`, so to create a future it's enough to implement this one function - the rest is then provided by the library. The key factor driving this design is "zero-cost-abstraction" requirement of the Rust language. It wants to provide nice higher level features, but they must be implemented very efficiently, basically with same efficiency (speed, memory) as if you've written optimized code in C. With this polling approach futures are just states machines and combined, more complex futures are just bit more complex state machines.


# Act IV - Hard Way - I Can Do The Future


So in previous Act we have a problem with one particular future - WriteAll (returned from `write_all function`), which consumed socket, so we cannot use it repeatedly. As explained above creating new future is just about implementing one method - poll, so why not to create a new future, which will solve our problem?


```rust
type MyStream = Box<Stream<Item = String, Error = ()> + Send>;
struct Sender {
    stream: MyStream,
    socket: TcpStream,
    buf: Vec<u8>,
    pos: usize,
}

impl Sender {
    fn new(stream: MyStream, socket: TcpStream) -> Self {
        Sender {
            stream: stream,
            socket: socket,
            buf: vec![],
            pos: 0,
        }
    }

    fn write(&mut self) -> futures::Poll<usize, ()> {
        while self.pos < self.buf.len() {
            match self.socket.poll_write(&self.buf[self.pos..]) {
                Err(e) => {
                    eprintln!("Error writing to socket: {}", e);
                    return Err(());
                }
                Ok(Async::NotReady) => return Ok(Async::NotReady),
                Ok(Async::Ready(0)) => {
                    eprintln!("Error write 0 bytes");
                    return Err(());
                }
                Ok(Async::Ready(n)) => self.pos += n,
            };
        }
        Ok(Async::Ready(self.pos))
    }
}

impl Future for Sender {
    type Item = ();
    type Error = ();

    fn poll(&mut self) -> futures::Poll<Self::Item, Self::Error> {
        // write remainder of previous line
        try_ready!(self.write());
        while let Async::Ready(x) = self.stream.poll()? {
            match x {
                Some(l) => {
                    self.buf = l.into_bytes();
                    self.pos = 0;
                    // write what we can
                    try_ready!(self.write());
                }
                None => return Ok(Async::Ready(())),
            }
        }
        Ok(Async::NotReady)
    }
}
```


The poll function is returning type `Poll<T,E> = Result<Async<T>,E>`.  Async is enum with two possible values - `Ready<T>`, which is returned when future is resolved and NotReady, returned when future is still pending and needs to wait for further events.  Tokio runtime then takes care that poll function is called only when events  relevant to pending future (data arrived on socket, chained future resolved, timer triggered etc.). When writing poll function it is crucial to return all NotReady states from incorporated futures' polling methods. Here we have two - socket asynchronous write (poll\_write) and stream's poll (which behaves very similarly to future's poll - but returning Ready\<Option\<T\>\> - with Some option as long as they are some items in the stream and finally returning None to indicate end of stream.  I separated logic of writing to stream into helper function `write`, as it's used in two places -  first when we receive data from steam we try to send as much as we can, before socket would signal NotReady. Then in next call of poll function we need fist send any remaining data. `write` function is using match statement to handle all possible return values of called poll - this can be simplified with `try_ready!` macro, which provides value if available, otherwise makes function return error or NotReady.

Ok, so now with this future we can rewrite our server as:


```rust
fn prepare_server(
    addr: std::net::SocketAddr,
    file_name: PathBuf,
    idx: Arc<Index>,
) -> Box<Future<Item = (), Error = io::Error> + Send> {
    println!("Starting at {}", &addr);
    let tcp = match TcpListener::bind(&addr) {
        Ok(t) => t,
        Err(e) => return Box::new(err(e)),
    };

    let server = tcp.incoming().for_each(move |socket| {
        println!("Received connection from {}", socket.peer_addr().unwrap());
        let file_name = file_name.clone();
        let idx = idx.clone();
        let lines_future = poll_fn(move || {
            blocking(|| {
                let i = rand::thread_rng().gen_range(0, idx.len());
                let (from, to) = idx[i];
                println!("Sending joke from lines: {} - {}", from, to);
                let reader = BufReader::new(File::open(&file_name).unwrap());
                let joke_iter = reader
                    .lines()
                    .skip(from)
                    .take(to - from)
                    .filter(|r| r.is_ok())
                    .map(|s| s.unwrap())
                    .filter_map(|l| {
                        let s = l.trim_left();
                        if s.len() > 0 {
                            let mut l = s.to_owned();
                            l.push_str("\n");
                            Some(l)
                        } else {
                            None
                        }
                    });

                iter_ok::<_, ()>(joke_iter)
            })
        });

        let write_future = lines_future
            .map_err(|_| eprintln!("Blocking error"))
            .and_then(|lines_stream| Sender::new(Box::new(lines_stream), socket));

        tokio::spawn(write_future);
        Ok(())
    });

    Box::new(server)
}
```


Is it working? Yes it is.

Is it nice code? Hmm, actually the server function is OKish, similar to previous one, but to solve our problem we had to write a custom code of size almost the same as the function itself. There has to be some better way, it looks like such common task  to send a steam to outgoing socket. I'll try to ask Rust community, I've heard that they are really helpful.

Is it good asynchronous code? I think there is still small  problem - `iter_ok` function turns iterator into stream, but this stream is always  resolved, it's never  got interrupted,  so it'll be processed in one go.  I'd rather like to send lines as they become available in truly asynchronous manner - a lot of small tasks that are executed as soon as possible.

Futures can help here with `futures::sync::mpsc::channel`  - it's very similar to channel available in standard library, but  modified to use futures. It sounds promising, let's try it, right?


# Act V - Channels Are Good


So here is our server using channel:


```sh
fn prepare_server(
    addr: std::net::SocketAddr,
    file_name: PathBuf,
    idx: Arc<Index>,
) -> Box<Future<Item = (), Error = io::Error> + Send> {
    println!("Starting at {}", &addr);
    let tcp = match TcpListener::bind(&addr) {
        Ok(t) => t,
        Err(e) => return Box::new(err(e)),
    };

    let server = tcp.incoming().for_each(move |socket| {
        println!("Received connection from {}", socket.peer_addr().unwrap());
        let file_name = file_name.clone();
        let idx = idx.clone();
        let (tx,rx) = unbounded::<String>();
        let joker = poll_fn(move || {
            blocking(|| {
                let i = rand::thread_rng().gen_range(0, idx.len());
                let (from, to) = idx[i];
                println!("Sending joke from lines: {} - {}", from, to);
                let reader = BufReader::new(File::open(&file_name).unwrap());
                reader
                    .lines()
                    .skip(from)
                    .take(to - from)
                    .filter(|r| r.is_ok())
                    .map(|s| s.unwrap())
                    .filter_map(|l| {
                        let s = l.trim_left();
                        if s.len() > 0 {
                            let mut l = s.to_owned();
                            l.push_str("\n");
                            Some(l)
                        } else {
                            None
                        }
                    })
                    .for_each(|l| tx.unbounded_send(l).unwrap())
            })
        })
        .map_err(|e| eprintln!("Blocking error: {}", e));

        tokio::spawn(joker);

        let stream = rx
            .map_err(|_| eprintln!("Blocking error"));
        let write_future = Sender::new(Box::new(stream), socket);
        tokio::spawn(write_future);

        Ok(())
    });

    Box::new(server)
}
```


Code is very similar to the one in previous Act.  But here we created unbounded channel (unbounded to make our life easier, so we can send without blocking. Because jokes have maximally tens of lines, it would be OK here, if  there will be more data, we will have to use bounded channel to prevent extensive use of memory, if other side of the channel is not consuming data quickly enough) and send lines to it.  Reading of lines from files is now separate task and runs in parallel with sending lines to socket, so each line can be sent as soon as it gets read from file.

Does this approach work? Yes, works like charm.

Is it nice code? - same as in previous Act - there is still big overhead with that custom future.  But I might get answer to my question. Yes <a href="https://users.rust-lang.org/t/tokio-how-to-easily-implement-sending-to-socket-from-a-stream/17709">there is an answer</a> \- use `lines_stream.forward(socket)` \- cool.  But wait it does not work - forward requires Sink trait, but socket does not implement it. I will need to read bit more about Streams and Sinks. I should have read <a href="https://tokio.rs/docs/getting-started/hello-world/">tokio's guide</a> to the end before messing with code.

Is it good asynchronous code? - I think it's better then previous one, we can achieve better concurrency, as lines are send immediately after they are read.


# Interlude - Stream and Sink


The futures crate provides also two other important traits Stream and Sink. We have seen Stream before, it's an asynchronous equivalent of Iterator and it also provides similar combinators. But stream has to be consumed in an asynchronous way - we have tried `for_each` method before and even custom future. But there is  much better way - Sink.  As there is AsyncRead  and AsynWrite traits pair on lower level, which works with bytes, then there is Stream and Sink traits pair, where Stream produces stream of items of arbitrary type and Sink then consumes them - all happening asynchronously .

So what I need is a Sink for lines (line represented as String type)  (as my channel is already Stream of lines, channel implements Stream).  To help to implement Stream/Sink pair tokio provides useful support - codec,  object that serialize given type from/to bytes. <a href="https://tokio.rs/docs/going-deeper/frames/">This article</a> explaines how to create line codec - and it's also already available in `tokio_io::codec::LinesCodec`. Once we have this codec our task is very easy - as shown in next  Act.


# Act VI - Easy Way - I Framed Sink


With LinesCodec we can write our server as:


```rust
fn prepare_server(
    addr: std::net::SocketAddr,
    file_name: PathBuf,
    idx: Arc<Index>,
) -> Box<Future<Item = (), Error = io::Error> + Send> {
    println!("Starting at {}", &addr);
    let tcp = match TcpListener::bind(&addr) {
        Ok(t) => t,
        Err(e) => return Box::new(err(e)),
    };

    let server = tcp.incoming().for_each(move |socket| {
        println!("Received connection from {}", socket.peer_addr().unwrap());
        let file_name = file_name.clone();
        let idx = idx.clone();
        let (tx,rx) = unbounded::<String>();
        let joker = poll_fn(move || {
            blocking(|| {
                let i = rand::thread_rng().gen_range(0, idx.len());
                let (from, to) = idx[i];
                println!("Sending joke from lines: {} - {}", from, to);
                let reader = BufReader::new(File::open(&file_name).unwrap());
                reader
                    .lines()
                    .skip(from)
                    .take(to - from)
                    .filter(|r| r.is_ok())
                    .map(|s| s.unwrap())
                    .filter_map(|l| {
                        let s = l.trim_left();
                        if s.len() > 0 {
                            Some(s.to_owned())
                        } else {
                            None
                        }
                    })
                    .for_each(|l| tx.unbounded_send(l).unwrap())
            })
        })
        .map_err(|e| eprintln!("Blocking error: {}", e));
        tokio::spawn(joker);

        let framed_socket = socket.framed(LinesCodec::new())
        .sink_map_err(|e| eprintln!("Write error {}", e));
        let write_future = rx.forward(framed_socket).
            map(|_| ());
        tokio::spawn(write_future);

        Ok(())
    });
```


Key trick is to turn socket into Stream/Sink with `socket.framed(LinesCodec::new())`and then we can use it with forward method.

Is it working? Indeed.

Is it nice code? Oh, yes the Stream/Sink symmetry feels very pleasing.

Is it good asynchronous code? I think yes.

Gotchas:

\- Here again I was bit struggling with errors mapping.  Problem was that framed socket implements both Stream and Sink traits - I used map\_err function as usual and was surprised that I cannot match errors type from the sink. But for sink there is `sink_map_err` function rather.

So we done, or not? I promised to show also the other approach, with existing asynchronous fs module, right?


# Act VII - All Async Now


With recent version of tokio there is module fs (crate tokio\_fs), which is doing exactly what I have tried to do in this article before - read asynchronously from files.  As I understood from blog post internally it also uses blocking function of threadpool. So to complete our journey let's use fs module (tokio::fs::File).


```rust
fn prepare_server(
    addr: std::net::SocketAddr,
    file_name: PathBuf,
    idx: Arc<Index>,
) -> Box<Future<Item = (), Error = io::Error> + Send> {
    println!("Starting at {}", &addr);
    let tcp = match TcpListener::bind(&addr) {
        Ok(t) => t,
        Err(e) => return Box::new(err(e)),
    };

    let server = tcp.incoming().for_each(move |socket| {
        println!("Received connection from {}", socket.peer_addr().unwrap());
        let file_name = file_name.clone();
        let i = rand::thread_rng().gen_range(0, idx.len());
        let (from, to) = idx[i];
        println!("Sending joke from lines: {} - {}", from, to);

        let reader_future = tokio::fs::File::open(file_name)
            .map(move |f| f.framed(LinesCodec::new())
                .skip(from as u64)
                .take((to - from) as u64)
                .filter_map(|l| {
                    let s = l.trim_left();
                    if s.len() > 0 {
                        Some(s.to_owned())
                    } else {
                        None
                    }
                })
                .map_err(|e| eprintln!("Error reading from file: {}",e))
            )
            .map_err(|e| eprintln!("Error opening file: {}",e));

        let framed_socket = socket.framed(LinesCodec::new())
        .sink_map_err(|e| eprintln!("Write error {}", e));
        let write_future = reader_future.and_then(|lines_stream| {
            lines_stream.forward(framed_socket)
            .map(|_| ())
        });
        
        tokio::spawn(write_future);

        Ok(())
    });

    Box::new(server)
}
```


It's working, it's nice, it asynchronous ( just notice how stream is using same combinators as our previous examples, I can just copy this logic here - how nice).


# Postlude


So we are at the end, we learned a lot ( at least I did) and it's time for some conclusions.

Lets start with one general.  I had times when I struggled a bit with rustc, but it aways turned out that it was for a good reason. I tried to do something not so smart and compiler prevent me from making fool of myself. This is my general feeling about Rust so far. While other languages let you approach problem from many possible ways and you almost always can progress on that way and  end up with some code that is working (but code can be bit freakish), Rust often stops you on the way and let you rethink whole problem and start from scratch.

Next comment is about tokio, I already used previous version (tokio\_core) and recent version is definitely progress, nicer, richer API. It takes some time to get used to work with futures and it's bit demanding on discipline in ownership and borrowing and requires good understanding of Rust type system, but once I got used to it,  working with it felt good.

And lastly you might ask, which solution is best?  And my answer would be none of already presented. If we really want efficient server with functionality presented here it will be best to cache jokes in memory. Memory is cheap nowdays and it'll make solution notably faster. So for completeness here is final solution - we just need to  change Index type to this:


```rust
struct Index {
    index: Vec<(usize, usize)>,
    lines: Vec<String>
}
```


and fill lines (only usefull ones) at the same time when we are building index. Server now looks like this:


```rust
fn prepare_server(
    addr: std::net::SocketAddr,
    idx: Index,
) -> Box<Future<Item = (), Error = io::Error> + Send> {
    println!("Starting at {}", &addr);
    let tcp = TcpListener::bind(&addr).unwrap();

    let server = tcp.incoming().for_each(move |socket| {
        println!("Received connection from {}", socket.peer_addr().unwrap());
        let i = rand::thread_rng().gen_range(0, idx.index.len());
        let (from, to) = idx.index[i];
        println!("Sending joke from lines: {} - {}", from, to);
        
        let joke: Vec<_> = idx
            .lines.iter()
            .skip(from)
            .take(to - from)
            .map(|s| s.to_owned())
            .collect();

        let mut text = joke.join("\n");
        text.push_str("\n");
        let write_future= io::write_all(socket, text)
        .map_err(|e| eprintln!("Write error: {}", e))
        .map(|_| ());

        tokio::spawn(write_future);

        Ok(())
    });

    Box::new(server)
}
```


I have done quick benchmarking of presented solutions. For this I have written minimal client in Rust+tokio, which spawns 1000 concurrent connections (for this I had to modified SOMAXCONN kernel parameter, otherwise strange things happen as explained <a href="https://github.com/tokio-rs/tokio/issues/383#issuecomment-393447366">here</a>), reads lines from socket and closes connection.  And I run it against different versions of the server.

Slowest version is the one from Act I - with 660ms to process all 1000 requests. It's no surprise as we have done something very bad there - used blocking code directly in asynchronous task. All other solutions, which used blocking function to wrap blocking code, perform better - around 300ms - 330ms. There was no significant difference between them.  Version with tokio\_fs, was very slightly slower - 380ms. Variance in measurements was notable so I'd not put too much significance into differences between solutions from Act || - Act VII in terms of performance. The cached solution was clearly fastest, as expected, with 100ms for all 1000 requests.

The code is also <a href="https://github.com/izderadicka/tokio-test-playground">on github</a> ( look for commit history for different versions).

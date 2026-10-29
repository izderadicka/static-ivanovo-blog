+++
title = "Hyper and TLS"
path = "/hyper-and-tls/"
date = "2020-03-15T20:07:10"
include_in_feeds = true
[extra]
wordpress_id = 2204
kind = "post"
node_key = "2204"
author = "admin"
source_url = "http://zderadicka.eu/hyper-and-tls/"
source_guid = "http://zderadicka.eu/?p=2204"
source_date_gmt = "2020-03-15 19:07:10"
categories = ["Programming"]
tags = ["asynchronous I/O", "Rust"]
+++
For <a href="https://github.com/izderadicka/audioserve">audioserve </a>update I wanted use new `hyper` with `tokio-tls`. Actually it required a bit of documentation reading, but finally  turned our quite straightforward.  




<span id="more-2204"></span>




Here are supportive functions (in `tls` module):






```rust
use futures::{future, stream::{StreamExt, TryStreamExt}};
use hyper::server::accept::{from_stream, Accept};
use native_tls::Identity;
use std::fs::File;
use std::io::{self, Read};
use std::path::{Path, PathBuf};
use tokio::net::{TcpListener, TcpStream};
use tokio_tls::TlsStream;

type Error = Box<dyn std::error::Error + 'static>;

pub struct TlsConfig {
    key_file: PathBuf,
    key_password: String
}

impl TlsConfig {
    pub fn new<P:Into<PathBuf>, S:Into<String>>(key_file: P, pass: S) -> Self {
        TlsConfig{
            key_file: key_file.into(),
            key_password: pass.into()
        }
    }
}

fn load_private_key<P>(file: P, pass: &str) -> Result<Identity, Error>
where
    P: AsRef<Path>,
{
    let mut bytes = vec![];
    let mut f = File::open(file)?;
    f.read_to_end(&mut bytes)?;
    let key = Identity::from_pkcs12(&bytes, pass)?;
    Ok(key)
}

pub async fn tls_acceptor(
    addr: &std::net::SocketAddr,
    ssl: &TlsConfig,
) -> Result<impl Accept<Conn = TlsStream<TcpStream>, Error = io::Error>, Error> {
    let private_key = load_private_key(&ssl.key_file, &ssl.key_password)?;
    let tls_cx = native_tls::TlsAcceptor::builder(private_key).build()?;
    let tls_cx = tokio_tls::TlsAcceptor::from(tls_cx);
    let stream = TcpListener::bind(addr).await?.and_then(move |s| {
        let acceptor = tls_cx.clone();
        async move {
            let conn = acceptor.accept(s).await;
            conn.map_err(|e| {
                error!("Error when accepting TLS connection {}", e);
                io::Error::new(io::ErrorKind::Other, e)
            })
        }
    })
    .filter(|i| future::ready(i.is_ok())); // Need to filter out errors as they will stop server to accept connections

    Ok(from_stream(stream))
}
```






Main trick is to filter out TLS accept errors - because an error in stream will stop the stream and new connections will not be accepted then. (And TLS errors are happening often - you may connect with just plain HTTP or client does not trust certificate,  etc.).






With above function server can be started like this:






```rust
#[macro_use]
extern crate log;
use std::convert::Infallible;
use hyper::{Request, Response, Body, Server, service::{make_service_fn, service_fn}};
use tls::{TlsConfig, tls_acceptor};

mod tls;

type Error = Box<dyn std::error::Error + 'static>;

#[tokio::main]
pub async fn main() -> Result<(), Error> {
     env_logger::init();

    let addr = ([127, 0, 0, 1], 3000).into();
    let tls_config = TlsConfig::new("/home/ivan/tls_key/audioserve.p12", "mypass");
    let incoming = tls_acceptor(&addr,&tls_config).await?;

    let make_svc = make_service_fn(|conn: &tokio_tls::TlsStream<tokio::net::TcpStream>| {
        let peer = conn.get_ref().peer_addr().unwrap();
        async move { Ok::<_, Infallible>(service_fn(move|req| {
            debug!("Request from {} for path {}", peer, req.uri());
            futures::future::ok::<_, Infallible>(Response::new(Body::from("Hello World!")))
        })) }
    });

    let server = Server::builder(incoming).serve(make_svc);
    info!("Listening on https://{}", addr);
    server.await?;
    Ok(())
}

```

+++
title = "Hyper Websocket"
path = "/hyper-websocket/"
date = "2019-04-02T15:10:02"
include_in_feeds = true
[extra]
wordpress_id = 2025
kind = "post"
node_key = "2025"
author = "admin"
source_url = "http://zderadicka.eu/hyper-websocket/"
source_guid = "http://zderadicka.eu/?p=2025"
source_date_gmt = "2019-04-02 14:10:02"
categories = ["Programming"]
tags = ["Rust", "Websocket"]
+++
As much as I do like Rust I have to admit there are some disadvantages of using this language - one common problem is immaturity and fragmentation of libraries -  I encountered this recently when I was looking for a way how create a websocket endpoint for <a href="https://github.com/izderadicka/audioserve">audioserve</a>.  audioserve is using low level HTTP library <a href="https://github.com/hyperium/hyper">hyper</a> \- as it's API is quite simple (which was it's <a href="/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/">key design principle</a>). I wanted to add websocket support on lowest possible level.  Actually it turned out as not totally trivial -  some frameworks like <a href="https://github.com/seanmonstar/warp">warp</a> or actix have build in websocket support, but for pure hyper + websocket we have to start from bottom.  <span id="more-2025"></span>
<strong>UPDATE for new hyper 0.13
</strong>For new hyper solution is much easier with <a href="https://github.com/snapview/tokio-tungstenite">tokio-tungstenite</a>, which provides ready to use implementation of the Tokio Stream and Sink of websocket messages. In hyper you still need to handle upgrade request header and proper response header. See below sample code for websocket server that echos messages (and counts received messages):



<script src="https://gist.github.com/izderadicka/bdc803d38840a15436f1a5ac1b1ca2cd.js"></script>



Key function above is `upgrade_connection`, which processes incoming websocket requests. It returns `Result` \- if websocket request is OK it returns `101 Upgraded` response and a future that will resolve to the structure implementing `Stream` and `Sink` of websocket messages. If websocket request is not OK it returns `400 Bad Request` response.

Function `handle_ws_connection` then shows how to work with that structure - after handling errors, `split` it to separate `Stream` and `Sink`, then process incoming messages by mapping and filtering them and finally `forward` them to outgoing Sink - to be send back. All websocket message handling code is then a Future, which must be  `spawn`ed in new task.

Above sample code also contains simple HTML+Javascript client to test websocket.

<strong>Continue reading if you want more details about original solution for hyper 0.12.</strong>

Recent Hyper has a nice support for HTTP connection upgrade - as can be seen <a href="https://github.com/hyperium/hyper/blob/master/examples/upgrades.rs">in this example</a>.  This was good start, but I needed to plug in there some websocket library in a compatible ( and hopefully easy) way.  And here some problems pop up.  Looking into <a href="https://crates.io/search?q=websocket">crates.io</a>, you can find several libraries, first on top was crate called plainly websocket - it's fairly popular and advertises hyper integration, but  alas with version 0.10, which is already fairly outdated, new hyper 0.12 is much different.  Another popular crate is ws, but there is nothing there about integration with hyper, so it would require a deep dive into the library to find useful parts. There are also couple of other libraries - two derivatives of already mention  websocket crate and some others.  Does not seem to be easy to choose right one.  So I had to look around -  the already mentioned warp framework is supporting both web sockets and hyper and it's created by maintainer of hyper Sean McArthur - so I hoped I could find right solution there.   And yes,  Sean is using yet another websocket crate called <a href="https://crates.io/crates/tungstenite">tungstenite</a>, which advertise itself as lightweight, easy to integrate library.   So I looked into warp code and find necessary parts and  extracted them into separate module, just as an exercise to understand how it works.  If you need just websocket in hyper look at code below:



<script src="https://gist.github.com/izderadicka/bb25bf19b05945c9945dcf2526b1e33c.js"></script>



With provided code it's then fairly easy - in hyper service  use upgrade\_connection function, which consumes request and returns tuple (response, future).  Response is to be sent immediately back (it's either successful 101 protocol upgrade or 400 error in case of websocket handshake problem), future then resolves to WebSocket structure, which implements Stream and Sink of websocket messages.

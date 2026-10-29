+++
title = "Future Is A State Machine"
path = "/future-is-a-state-machine/"
date = "2019-02-16T09:54:05"
include_in_feeds = true
[extra]
wordpress_id = 2002
kind = "post"
node_key = "2002"
author = "admin"
source_url = "http://zderadicka.eu/future-is-a-state-machine/"
source_guid = "http://zderadicka.eu/?p=2002"
source_date_gmt = "2019-02-16 08:54:05"
categories = ["Programming"]
tags = ["asynchronous I/O", "Rust"]
+++
I think I noticed in <a href="/from-ignorance-to-enlightenment-playing-with-tokio/">this article</a> that Rust Future is basically a state machine, which is propagated through its states via appropriate runtime (and parked when not ready to move to a next state). But I did not appreciate this fact fully until recently I was making <a href="https://github.com/izderadicka/async-tar">a small utility</a> (<a href="https://github.com/izderadicka/audioserve/tree/lib-update/crates/async-tar">here</a> is new version for new futures and tokio) for creating tar archive asynchronously - it should be a Stream that produces chunks of data - first file header and then pieces of it's content. When file is done move to next file, until all required files are sent to stream, then finally send two empty blocks, each of 512 bytes of binary zeros. I needed this Stream for my <a href="https://github.com/izderadicka/audioserve">audioserve</a> project, where I wanted to download content of whole directory as a tar archive. Stream is a kind of Future (which produces many values instead of just one), so it's also a state machine. And when I started to think about it this way, implementation was obvious. Rust algebraic type system is of great help here as we can represent state  with one complex enum type ( called TarState in this case) and it's variants represent states of this state machine and also contain necessary internal variables for each state.  So lets see state diagram for our TarStream:<span id="more-2002"></span>
<a href="/wp-content/uploads/tar_state.png"><img alt="tar_state" class="alignnone wp-image-2005 size-full" decoding="async" height="486" loading="eager" sizes="(max-width: 896px) 100vw, 896px" src="/wp-content/uploads/tar_state.png" srcset="/wp-content/uploads/tar_state.png 896w, /wp-content/uploads/tar_state-300x163.png 300w" width="896"/></a>

With this vision in mind it was then fairly easy to implement the TarStream (although the manual implementation of state machine is not usually much exciting, but Rust types at least make it nice and clean).

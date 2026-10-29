+++
title = "Sometime it's tricky to get Rust generics right"
path = "/sometime-its-tricky-to-get-rust-generics-right/"
date = "2024-08-17T14:58:23"
include_in_feeds = true
[extra]
wordpress_id = 2336
kind = "post"
node_key = "2336"
author = "admin"
source_url = "http://zderadicka.eu/sometime-its-tricky-to-get-rust-generics-right/"
source_guid = "http://zderadicka.eu/?p=2336"
source_date_gmt = "2024-08-17 13:58:23"
categories = ["Programming"]
tags = ["Rust"]
+++
At least for me. I think I have learned a lot a bout the language, but still so thing did not come up easily - recent example was a generic map, that can use both owned values or references as keys.  So basically  COW of the type is used as key.  So here is the result, which took me while to put together:




<span id="more-2336"></span>




<script src="https://gist.github.com/izderadicka/296f2c07c984cf7d84335fbad2ca7095.js"></script>

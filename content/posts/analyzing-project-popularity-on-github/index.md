+++
title = "Analyzing Project Popularity on Github"
path = "/analyzing-project-popularity-on-github/"
date = "2021-12-06T22:08:54"
include_in_feeds = true
[extra]
wordpress_id = 2310
kind = "post"
node_key = "2310"
author = "admin"
source_url = "http://zderadicka.eu/analyzing-project-popularity-on-github/"
source_guid = "http://zderadicka.eu/?p=2310"
source_date_gmt = "2021-12-06 21:08:54"
categories = ["Uncategorized"]
tags = ["data analysis", "github"]
+++
Wondering how you project is doing on github and stars and growing over the time?   I was (for my favorite project <a href="https://github.com/izderadicka/audioserve">audioserve</a>) so I created ipython notebook for to analyze trend on the time, which some predictions (which are now called AI  - even linear regression is now called AI :-).




<span id="more-2310"></span>




## Chart first






<figure class="wp-block-image"><img alt="" class="wp-image-2311" decoding="async" loading="eager" sizes="(max-width: 711px) 100vw, 711px" src="/wp-content/uploads/as-stargazers.png" srcset="/wp-content/uploads/as-stargazers.png 711w, /wp-content/uploads/as-stargazers-300x157.png 300w"/></figure>






## And Now Code






<script src="https://gist.github.com/izderadicka/65b88313763261227e37b9f6784bdd5a.js"></script>






You will just need usual data analysis libraries: pip3 install jupyter pandas numpy scipy matplotlib.

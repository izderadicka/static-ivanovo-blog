+++
title = "Secret Sharing Is Caring Too"
path = "/secret-sharing-is-caring-too/"
date = "2017-09-27T23:44:45"
include_in_feeds = true
[extra]
wordpress_id = 1724
kind = "post"
node_key = "1724"
author = "admin"
source_url = "http://zderadicka.eu/secret-sharing-is-caring-too/"
source_guid = "http://zderadicka.eu/?p=1724"
source_date_gmt = "2017-09-27 22:44:45"
[taxonomies]
category = ["Mathematic", "Programming", "Security"]
tag = ["cryptography", "Rust", "secret sharing"]
+++
In todays digital world passwords and other types of secrets are omnipresent and they secure access to various assets dear to our hearts, some of those can have tremendous tangible or moral value. For such assets it's worth to select really good and strong password, which basically means long and hard to remember. How to ensure ourselves in case of memory failure? We can write it down and lock in secure place, share with trusted person etc., but still there is one point of of failure - secure place can be robbed, that person can betray us. Can cryptography  provide us with better options?  Yes it can with help of method called [Secret sharing ](https://en.wikipedia.org/wiki/Secret_sharing)\- we can split secret into n parts - called shared secrets - and distribute them to different places/people. Later we (or someone else) need to collect k (k \> 0 and k \<= n) shared secret to recover original secret. k is called threshold and it is defined when generating shared secrets - so we for instance generate n=5 shared secrets, but only k=3 will be needed to recover original secret.

I believe you can easily imagine  many other real life scenarios where secret sharing can be useful and for sure it's used in many applications and systems today. Cryptography provides several algorithms for secure (by design) secret sharing.  Most common is [Shamir's Secret Sharing](https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing) based on linear algebra approach. There are many tools and libraries for Shamir's scheme (and further advancements of original algorithm),  you can for instance try [ssss](http://point-at-infinity.org/ssss/index.html), which provides command line tool that you can easily install into your Linux and also there is an[ online demo](http://point-at-infinity.org/ssss/demo.html). Another family of secret sharing schemes is based on [Chinese Reminer Theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem), where especially [Asmuth-Bloom scheme](https://en.wikipedia.org/wiki/Secret_sharing_using_the_Chinese_remainder_theorem#Asmuth-Bloom.27s_threshold_secret_sharing_scheme) is interesting.  I have not seen many implementation for Asmuth-Bloom secret sharing so I [created one](https://github.com/izderadicka/asmuth_bloom_secret_sharing) in Rust.<span id="more-1724"></span>

My implementation contains also command line utility so you can easily play with in on your computer:

If you do not have cargo and rustc you can easily install with


```sh
curl -sSf https://static.rust-lang.org/rustup.sh | sh

```


Then install with cargo:


```sh
cargo install asmuth_bloom_secret_sharing
```


And create shared secrets:


```sh
#ensure cargo binaries are on the path
PATH=$PATH:$HOME/.cargo/bin
# and generate shared secrets
asmuth_bloom_secret_sharing generate -n 5 -t 3 my_biggest_secret
```


The output is:


```sh
200p2l:400p4r:2v6a0f1bvhdgqjn0c05eg11oia9v
200p2l:400p5h:m08u392jbfptt071kv3eq3teqaq
200p2l:400p65:2bjrjd73hgsavd805g5g7ohv7kre
200p2l:400p6h:3cr8v18kfqmon2h9vl7j1fi779eo
200p2l:400p71:1k03mp7e6fg2ap6ahi1tt3p0bbtf

```


Each line represents one shared secret. Later we can recover original secret from any 3 shared secrets (as threshold was 3):


```sh
asmuth_bloom_secret_sharing recover -t 3 <<EOF
200p2l:400p5h:m08u392jbfptt071kv3eq3teqaq
200p2l:400p6h:3cr8v18kfqmon2h9vl7j1fi779eo
200p2l:400p4r:2v6a0f1bvhdgqjn0c05eg11oia9v
EOF
echo

```


And indeed we will see our secret again:


```sh
my_biggest_secret
```

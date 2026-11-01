+++
title = "Fearless Upgrades with Typed Languages"
path = "/fearless-upgrades-with-typed-languages/"
date = "2018-09-10T13:39:16"
include_in_feeds = true
[extra]
wordpress_id = 1924
kind = "post"
node_key = "1924"
author = "admin"
source_url = "http://zderadicka.eu/fearless-upgrades-with-typed-languages/"
source_guid = "http://zderadicka.eu/?p=1924"
source_date_gmt = "2018-09-10 12:39:16"
[taxonomies]
category = ["Programming"]
tag = ["Rust", "Static Typing"]
+++
One of many advantages of statically typed programing languages like Rust or Java is their resilience to changes in dependent libraries, usually caused by new library versions with modified interface - e.g. the major version changes. In statically typed language we usually see problems in compile time and it should be relatively easy to fix, but in dynamic languages such as Python or Javascript upgrade is more challenging and problems  demonstrate themselves during tests (in better case, when we have good test coverage) or in production in worst case. I had recently came through this process for couple of  relatively small projects in Rust. Couple of dependencies ([hyper](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=2ahUKEwixy4u1t7DdAhXMfFAKHY1yCNsQFjAAegQIARAB&url=https%3A%2F%2Fgithub.com%2Fhyperium%2Fhyper&usg=AOvVaw12Y-0K_NixUiQbFFByfQ8L) and [tokio](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=2ahUKEwiYlKK-t7DdAhXHKFAKHfckA8kQFjAAegQIABAB&url=https%3A%2F%2Fgithub.com%2Ftokio-rs%2Ftokio&usg=AOvVaw2hAkYKAEpJERcK2PGYLHeV)) had been upgraded to new versions with significant changes to their interface. With update compilation broke with tens of errors, but gradually I was able to fix all of them (in one case it required to improve error handling with custom error type, plus using additional new library, as typed headers were removed form hyper) and after code compiled and run through basic tests I was pretty sure that I'm fine with new libraries. In similar situation in python I would need much more work to be sure that code works after such major upgrade of dependencies. In practice it enables easier maintenance of code and less effort  to keep it up to date with latest libraries. For library authors it provides more freedom and they can introduce breaking changes more often (with great cargo build tool in Rust library users can pin themselves to older version, if they do not want to upgrade).

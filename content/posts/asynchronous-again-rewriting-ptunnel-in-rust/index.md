+++
title = "Asynchronous Again - Rewriting ptunnel in Rust"
path = "/asynchronous-again-rewriting-ptunnel-in-rust/"
date = "2017-11-26T13:36:32"
include_in_feeds = true
[extra]
wordpress_id = 1789
kind = "post"
node_key = "1789"
author = "admin"
source_url = "http://zderadicka.eu/asynchronous-again-rewriting-ptunnel-in-rust/"
source_guid = "http://zderadicka.eu/?p=1789"
source_date_gmt = "2017-11-26 12:36:32"
categories = ["Programming"]
tags = ["asynchronous I/O", "proxy", "Rust", "tokio"]
+++
Asynchronous programing model is quite popular for I/0 intensive tasks - it enables you effective use of resources, while maintaining agility of and assuring scalability of the application. I myself used asynchronous programming many times -   in JavaScript (where it's omnipresent) , Python ( mainly  in <a href="https://docs.python.org/3/library/asyncio.html">asyncio</a> recently, but also bit in <a href="https://twistedmatrix.com/trac/">twisted</a>, which was one of first network asynchronous libraries I met) and also in OCAML with  <a href="http://ocsigen.org/lwt/">lwt</a> or <a href="https://realworldocaml.org/v1/en/html/concurrent-programming-with-async.html">Core Async</a>. The concept is always similar for all implementations -  I/O operations are returning handles to future results - they are called either  Futures, Promises, or Deferred  - and they are returned immediately.  These futures can have functions attached to them, which are executed later, when I/O result becomes available.  Asynchronous  programming is very much about functions, it requires first class functions  and anonymous functions are very useful here, that's why asynchronous model flourishes in functional languages.  Apart of I/O deferred processing usually there are other utilities for later execution - like timeouts, pausing execution for some time (sleep), tasks synchronization (events, locks). Futures are executed in an "event loop",   a loop that monitors various events from OS (availability of data from I/O), timers, etc. to execute futures (meaning functions attached to them), when appropriate. It's also very common to chain futures, executing second one with result of first one , when first one is resolved and result is available and the third one with results from the second one and so on. Apart of this basic scheme languages may provide some syntactic sugar around asynchronous model like await and async keywords in Python or C#, which makes it easier to write the code.




Recently, as I'm progressing in learning of <a href="https://www.rust-lang.org">Rust, </a> I wondered how asynchronous programing is done in Rust. I decided to remake my <a href="/accessing-imapsmtp-via-https-proxy/">old project ptunnel</a> (written in Python) into Rust - ptunnel is a program that tunnels arbitrary connection/protocol through HTTPS proxy, so it can be used to connect IMAP, SMTP or SSH through proxy. In the rest of this article I''l share my experiences from this project.<span id="more-1789"></span>




Rust is relatively young language and asynchronous programing in Rust is even younger - now most popular library is <a href="https://tokio.rs/">Tokio</a>, which is still in version <a href="https://crates.io/crates/tokio-core">0.1,</a> so basically in its infancy.  But site contains good documentation and guidance so it's was relatively easy to get started.




## The Long And Winding Road




I have to admit I'm still  struggling with some Rust concepts (lifetime mainly) and Tokio was quite demanding for sticking with core concepts. Tokio is using intensively <a href="https://crates.io/crates/futures">futures</a> module and all programing  and data processing is done through chaining of futures - this can create very complex types ( especially when anonymous closures are used) and thus provide very cryptic errors ( with type description over half of the screen - reminding me monstrous types in OCAML <a href="/ocaml-ocsigen-i-ching-and-web-applications/">Ocsigen</a> libraries ). In order to make various complex Future types compatible with rest of the program is quite often necessary to create trait objects - e.g. to box values. There is also one hideous features of rustc,  errors concerning lifetime of variables are reported as last - when all more 'serious' errors are resolved. So often it happened to me that I had removed one final error in code only to find that others pop up and I had found that I had screwed lifetime of some variables/parameters and that it couldn't be easily fixed and had to redesign code.




Generally I noticed that while previously in other languages I was able to start and follow a single, relatively straight path from idea to final code and was able to progress steadily further, here in async Rust I had to backtrack several times, because the way lead nowhere. It looks like there are only few ways how to make it right and if you do not catch them initially you are lost. Hopefully those ways should lead to better code.




Tokio provides nice abstractions for higher level protocols (transports + protocols + services), which I believe can help in other cases,  but here I needed something rather low level -  so finally I ended up with using custom stream and  future types, after learning a bit about Tokio internals ( stressing again good documentation of Tokio) and chaining futures with `map` (modifying future value), `and_then` ( creating new future from results of previous one) and `or_else` (resolving error cases)




One of most attractive features of Rust is 'zero-costs' abstraction.  Rust provides higher level language abstractions like algebraic types, iterators etc., which are then implemented in very effective way - basically with same efficiency as if written in lower abstraction level language like C. Tokio abstractions (on lower level, where I was dwelling)  are mainly iterator like traits of Streams and Sinks and future combinators. So after finally being able to cope with these I was wondering how final code will perform and if it'll match 'zero-costs' promise.




## Comparison to Python Version




I have to say that old Python program was a poor contender. It's written in very basic manner and not using any features that could improve performance ( at least thread pool, or asyncio) and it creates (and destroys) two threads for each connection.




So rather then fair benchmark it's just a toy comparison, just to assure that Rust program is doing better. And it is doing better indeed, much better as we see below.




For quick test I used <a href="http://www.squid-cache.org/">squid</a> proxy, <a href="https://nginx.org/">nginx</a> server and <a href="https://httpd.apache.org/docs/2.4/programs/ab.html">ab</a> (apache benchmark tool), all installed locally on my notebook - sending 1000 HTTP GET requests in 5 concurrent threads. So setup is like this:




```sh
ab <-> ptunnel <-> local squid <-> local nginx (default page)
```




And result is ( average time per request in ms):




<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table>
<tbody>
<tr>
<th> </th>
<th>Keep-Alive</th>
<th>No Keep-Alive</th>
</tr>
<tr>
<th>Old Python Tool</th>
<td>10.51 ms</td>
<td>1003.75 ms</td>
</tr>
<tr>
<th>New Rust Tool</th>
<td>0.31 ms</td>
<td>3.28 ms</td>
</tr>
</tbody>
<tbody>
<tr>
<th>Without ptunnel</th>
<td>1.83 ms</td>
<td>2.55 ms</td>
</tr>
</tbody>
</table></div>




As you can see old python tool is no match - especially when no keep alive is used and thus overhead of thread creation is preposterous ( keep-alive case Python was fine on majority of requests, but few, where connection was created, time was again around 1 sec due to thread creation overhead).




For comparison there is also scenario where ab connects directly to squid (ptunnel is left out) -   there is interesting  keep-alive case, where setup with ptunnel is faster.




Even if this benchmark is simplistic it still shows that Rust program keeps to its promise and seems to perform well ( direct benchmark between ab and nginx gives 0.22ms per request).




Looking at code base Rust program is about 3 times bigger then old Python program ( ~ 600 lines vs ~ 200 lines).




## The Code




<ol>
<li>The code is available <a href="https://github.com/izderadicka/ptunnel-rust">on the github</a>, where kind reader can review it, README.md file contains instructions for installation. New Rust program functionality and CLI copies basically old python program, only new feature available is basic authentication with proxy.</li>
</ol>





## Using ptunnel with Thunderbird and Gmail






Main motivation for ptunnel was to be able to use Thunderbird behind corporate proxy for Gmail account (via IMAP/SMTP protocols). You can basically proxy any protocol (like SSH), but these two were most interesting for me. Setup is described somehow in the <a href="/accessing-imapsmtp-via-https-proxy/">original article</a>, but here I'd like to highlight main steps/gotchas for this particular combination ( I tested on both Linux and Windows).






The key problem is with TLS/SSL - both IMAP and SMTP are now possible only through secure socket (and this is probably something, which you'd like to do anyhow) and there is one issue - server certificate - if you connect through local proxy, you set localhost as IMAP and SMTP server, but then hostname in certificate does not match and Thunderbird complains about invalid certificate. 






You can add exception, but Google is using several different certificates (looks like they have different  front ends) and certificates change rather often now, so it'll not work well, we need some workaround.






The trick to make Thunderbird happy is to use `hosts` file to change name resolution for `imap.gmail.com` and `smtp.gmail.com`. Put this into your `hosts` file (`/etc/hosts` on Linux or `C:\Windows\System32\drivers\etc\hosts` on Windows)






```
127.0.0.1    imap.gmail.com127.0.0.1    smtp.gmail.com
```






This will trick TB, however we will have problems with ptunnel in direct mode (not going through proxy - ptunnel can work in proxied mode (through HTTPS proxy, where this trick is OK, as name resolution in done on proxy server), but also it can work in direct mode (and fall back to direct mode, if proxy is not available - e.g. you are on open network) , where it just sends data to final destination, which now resolves to localhost - so it will not work unfortunately. But this "secondary" problem can be fixed  by starting ptunnel with slightly smart script, which initially forces remote name resolution:






```bash
#!/bin/bash
IMAP_ADDR=`dig imap.gmail.com|awk '/^;; ANSWER SECTION:$/ { getline ; print $5 }'`
SMTP_ADDR=`dig smtp.gmail.com|awk '/^;; ANSWER SECTION:$/ { getline ; print $5 }'`

IMAP_ADDR=${IMAP_ADDR:-gmail-imap.l.google.com}
SMTP_ADDR=${SMTP_ADDR:-gmail-smtp-msa.l.google.com}
#ptunnel.py -d -p www-proxy-ams.nl.oracle.com:80 9993:$IMAP_ADDR:993 5587:$SMTP_ADDR:587 &
ptunnel  -p proxy.my-org.com:80 9993:$IMAP_ADDR:993 5587:$SMTP_ADDR:587 &

```






 Or in Windows this Powershell script (and put shortcut in `C:\Users\your_user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup` to start ptunnel automatically):






```text
$ips = Resolve-DNSName  -NoHostsFile -Name imap.gmail.com -Type A 
$imap = $ips[0].Ip4Address
$ips = Resolve-DNSName  -NoHostsFile -Name smtp.gmail.com -Type A 
$smtp = $ips[0].Ip4Address

Write-Host "IMAP: $imap SMTP: $smtp"

Start-Process  -WindowStyle Hidden -FilePath ./ptunnel.exe -ArgumentList "-vvv -p proxy.my-org.com:80 9993:${imap}:993 4465:${smtp}:465"
```






If we do above changes in `hosts` file and start ptunnel with script above, then the only change needed to be done in account settings in Thunderbird is to change IMAP port from 993 to 9993 and SMTP port from 587 to 5587 (or 465 to 4465 - depending what you used) and emails with work in both open networks and behind proxy.

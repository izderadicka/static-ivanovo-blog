+++
title = "Why GMail is not changing all server certificates in synch?"
path = "/why-gmail-is-not-changing-all-server-certificates-in-synch/"
date = "2014-05-03T12:39:17"
include_in_feeds = true
[extra]
wordpress_id = 803
kind = "post"
node_key = "803"
author = "admin"
source_url = "http://zderadicka.eu/why-gmail-is-not-changing-all-server-certificates-in-synch/"
source_guid = "http://zderadicka.eu/?p=803"
source_date_gmt = "2014-05-03 11:39:17"
categories = ["Admin", "Tools"]
tags = ["email", "IMAP", "proxy"]
+++
I'm accessing my Gmail account from behind HTTPS proxy - it was described is <a href="/accessing-imapsmtp-via-https-proxy/" title="Accessing IMAP/SMTP via HTTPS Proxy">this post</a>.  Thunderbird does not support it, for IMAP and SMTP  only SOCKS proxy can work.   To cope with it  I'm using a small local proxy, that redirects any connection via proxy CONNECT method to remote host:port.

This works fine, but in email client I had to set IMAP server as localhost and SMTP server also as localhost.  Thunderbird is cautious about it and since both connections are using TLS/SSL then there is a security issue -  I'm connecting to localhost, but certificates are  for \*.gmail.com domain.  Luckily Thunderbird enables me to set security exception -   it asks me if I'll allow that certificate for that host address, if I confirm everything works like charm until Gmail changes certificate on servers (which happens about couple time per year or so).<span id="more-803"></span>
<strong>Picture 1. - Security exceptions stored in Thunderbird's Properties / Advanced / Certificates:</strong>
<a href="/wp-content/uploads/certificates.png"><img alt="certificates" class="alignnone size-full wp-image-804" decoding="async" height="499" loading="eager" sizes="(max-width: 698px) 100vw, 698px" src="/wp-content/uploads/certificates.png" srcset="/wp-content/uploads/certificates.png 698w, /wp-content/uploads/certificates-300x214.png 300w" width="698"/></a>

They indeed have many servers load balanced, now what happens during certificate change -   some servers have already new certificate, and some have old one.   If my client by a chance connects to a server with new certificate,  I get security warning again, because certificate in the stored permanent exception is different.   Again I confirm, but then what happens then -   next connection goes to other server, which still has old certificate and I get again security warning and next connections goes to server with new certificate, next next to old and so on, round and round.

<strong>Picture 2. - Security exception dialog (for IMAP connected through local proxy)</strong>
<a href="/wp-content/uploads/sec-warning.png"><img alt="sec-warning" class="alignnone size-full wp-image-805" decoding="async" height="508" loading="lazy" sizes="(max-width: 503px) 100vw, 503px" src="/wp-content/uploads/sec-warning.png" srcset="/wp-content/uploads/sec-warning.png 503w, /wp-content/uploads/sec-warning-150x150.png 150w, /wp-content/uploads/sec-warning-297x300.png 297w" width="503"/></a>

This goes on for several days usually - why they cannot change and sync all certificates at once?  Why it takes so long?  I do not know,  but <span style="text-decoration: underline;">if you do I've like to hear why</span>.

Recently again this situation has happened and as usual it's quite annoying (more due to the fact that even if I switch off automatic retrieval of messages in Thunderbird profile,  it still opens some connections to server every few minutes). But then I got idea -   what if I keep correct server names in Thunderbird profile, but mess with name resolution -   e.g. I can put this into /etc/hosts:


```sh
#gmail proxy 
127.0.0.1	imap.gmail.com
127.0.0.1	smtp.gmail.com

```


And it works!

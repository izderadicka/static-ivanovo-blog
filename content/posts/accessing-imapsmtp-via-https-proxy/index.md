+++
title = "Accessing IMAP/SMTP via HTTPS Proxy"
path = "/accessing-imapsmtp-via-https-proxy/"
date = "2012-09-23T20:32:03"
include_in_feeds = true
[extra]
wordpress_id = 134
kind = "post"
node_key = "134"
author = "admin"
source_url = "http://zderadicka.eu/accessing-imapsmtp-via-https-proxy/"
source_guid = "http://zderadicka.eu/?p=134"
source_date_gmt = "2012-09-23 19:32:03"
categories = ["Admin"]
tags = ["email", "IMAP", "proxy", "python"]
+++
<a href="/wp-content/uploads/tunel.jpeg"><img alt="" class="alignleft size-thumbnail wp-image-135" decoding="async" height="150" loading="eager" src="/wp-content/uploads/tunel-150x150.jpeg" title="tunell" width="150"/></a>In some places Internet access is available only via proxy, which in practice means that you are limited to HTTP and HTTPS protocols only.  But if you have  external email accounts like Gmail,  this is bit limiting, because you cannot access your email via IMAP protocol from your  email client.

However there can be a solution -  if proxy support HTTPS protocol, it means also that it supports CONNECT method that  tunnels a connection to remote server unchanged.  This method could be used to tunnel any protocol, so basically  it could tunnel also IMAP ( and SMTP for outgoing email).<span id="more-134"></span>

The only piece that is needed is either support from client (but Thunderbird unfortunately does not support this) or a tunnel program running on local machine + slight change in email account - to use local connection to tunnel proxy instead of direct connection to server.   But there is still one small glitch - if your computer is notebook and you come home, there is no proxy, and you want to connect to mail server directly again. To handle this scenario local tunnelling  proxy should be smart and fall- back to direct connection to server, if HTTPS proxy is not available.  I have not found any program like this, so I've written mine own - called <a href="https://github.com/izderadicka/ptunnel">ptunnel</a>. Recently I returned to this problem and created <a href="https://github.com/izderadicka/ptunnel-rust">new ptunnel</a> in <a href="https://www.rust-lang.org">Rust</a> \- it's much faster and less resource intensive, so I recommend this one.

Now how to do this in practice:


<ol>
<li>Get ptunnel from links above (old one requires <a href="http://python.org">python</a>, new one must be compiled locally first).</li>
<li>Run it with appropriate parameters - for Gmail it should  be something like this:
Rust program:
<pre class="code-highlight" data-language="sh"><code><span class="code-line">ptunnel<span class="w"> </span>-p<span class="w"> </span>proxy_host:proxy_port<span class="w"> </span><span class="m">9993</span>:imap.gmail.com:993<span class="w"> </span><span class="m">5587</span>:smtp.gmail.com:587</span></code></pre>
Python program:
<pre class="code-highlight" data-language="sh"><code><span class="code-line">ptunnel.py<span class="w"> </span>-d<span class="w"> </span>-p<span class="w"> </span>proxy_host:proxy_port<span class="w"> </span><span class="m">9993</span>:imap.gmail.com:993<span class="w"> </span><span class="m">5587</span>:smtp.gmail.com:587</span></code></pre>
You should assure that ptunnel is  automatically started, when computer starts - the ways how you can do this are various - I prefer to start it with my desktop (Startup Applications in Gnome, Unity, Cinnamon), you can use /etc/rc.local or some other ways - I believe it may work fine even under other platforms like Win or Mac, even I never tried it.</li>
<li>You have to reconfigure your email account - IMAP server should be localhost:9993 and smtp server localhost:5587.</li>
<li>After reconfiguration, when you'll try to receive or send  email, you will get security warning - that's because SSL certificates are not matching.  You now connecting to localhost, but certificates are issued to mail server DNS name - you have to add security exceptions for these certificates.</li>
</ol>


This tunnelling works for me  fine for quite  some time ( a year or so).  Tunnelling is not limited to IMAP /SMTP only so it can be used for SSH etc.

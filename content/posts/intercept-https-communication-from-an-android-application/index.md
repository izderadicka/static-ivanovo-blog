+++
title = "Intercept https communication from an Android application"
path = "/intercept-https-communication-from-an-android-application/"
date = "2019-01-12T09:53:09"
include_in_feeds = true
[extra]
wordpress_id = 1988
kind = "post"
node_key = "1988"
author = "admin"
source_url = "http://zderadicka.eu/intercept-https-communication-from-an-android-application/"
source_guid = "http://zderadicka.eu/?p=1988"
source_date_gmt = "2019-01-12 08:53:09"
categories = ["Admin", "Security"]
+++
Many Android applications communicate with severs using some form of <a href="https://en.wikipedia.org/wiki/Representational_state_transfer">REST API</a> secured with <a href="https://en.wikipedia.org/wiki/Transport_Layer_Security">TLS/SSL</a> (so it's  "https" protocol).  If it is your application or an open source application you know what's going on from the source, but for third party application you still may be wondering (hopefully for legit reasons:-), what is this application sending to the server and what it gets back.  With help of few free tools it's fairly easy to monitor encrypted traffic on your local computer (linux, but it will work on other systems too).<span id="more-1988"></span>


## What is needed


<a href="https://developer.android.com/studio/#downloads">Android SDK</a> ( I downloaded it as part of Android Studio, but you can download only command line tools)
<a href="https://mitmproxy.org/">mitmproxy</a> (special proxy that can help to decrypt https using "<a href="https://en.wikipedia.org/wiki/Man-in-the-middle_attack">Man in the Middle</a>" approach)
openssl tool (normally available in your linux distro, in Ubuntu install with `sudo apt install openss`l)


## Setup




<ul>
<li>Install mitmproxy</li>
<li>Run it
<pre class="code-highlight" data-language="sh"><code><span class="code-line">mitmproxy<span class="w"> </span>--set<span class="w"> </span><span class="nv">stream_large_bodies</span><span class="o">=</span>1m</span></code></pre>
</li>
<li>Test it in local browser on an unencryped site to see how it works (set proxy in the browser to localhost:8080)</li>
<li>Get Android application .apk file
There are many approaches, you can use some internet service, or <a href="https://stackoverflow.com/questions/4032960/how-do-i-get-an-apk-file-from-an-android-device">use adb to extract from your phone via USB cable</a>, or create an android emulator with Google Play, install application there and use adb to extract (same approach as in previous case).</li>
<li>Create emulator from bare android image (no Google Play and APIs), thus you will be able to get root access easily.</li>
<li>Now you need to install root certificate of mitmproxy dummy CA to the android image in the emulator into system wide certificates :
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="nb">cd</span><span class="w"> </span>~/Android/Sdk/platform-tools</span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="c1"># prepare key  compatible with Android</span></span>&#10;<span class="code-line"><span class="c1"># this first commad will give you hash code used in following commands to name the fiile</span></span>&#10;<span class="code-line">openssl<span class="w"> </span>x509<span class="w"> </span>-inform<span class="w"> </span>PEM<span class="w"> </span>-subject_hash_old<span class="w"> </span>-in<span class="w"> </span>~/.mitmproxy/mitmproxy-ca.pem<span class="w"> </span><span class="p">|</span><span class="w"> </span>head<span class="w"> </span>-1</span>&#10;<span class="code-line">cat<span class="w"> </span>~/.mitmproxy/mitmproxy-ca.pem<span class="w"> </span>&gt;<span class="w"> </span>c8750f0d.0<span class="w"> </span></span>&#10;<span class="code-line">openssl<span class="w"> </span>x509<span class="w"> </span>-inform<span class="w"> </span>PEM<span class="w"> </span>-text<span class="w"> </span>-in<span class="w"> </span>~/.mitmproxy/mitmproxy-ca.pem<span class="w"> </span>-out<span class="w"> </span>/dev/null<span class="w"> </span>&gt;&gt;<span class="w"> </span>c8750f0d.0</span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="c1"># in other terminal start emulator with writable /system volume</span></span>&#10;<span class="code-line"><span class="nb">cd</span><span class="w"> </span>~/Android/Sdk/emulator</span>&#10;<span class="code-line">./emulator<span class="w"> </span>-writable-system<span class="w"> </span>@Nougat_bare</span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="c1"># and back in first terminal use adb tool</span></span>&#10;<span class="code-line">./adb<span class="w"> </span>root</span>&#10;<span class="code-line">./adb<span class="w"> </span>push<span class="w"> </span>c8750f0d.0<span class="w"> </span>/storage/emulated/0/Download</span>&#10;<span class="code-line">./adb<span class="w"> </span>shell</span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="c1"># in the Android shell</span></span>&#10;<span class="code-line">mount<span class="w"> </span>-o<span class="w"> </span>rw,remount<span class="w"> </span>/system</span>&#10;<span class="code-line">cp<span class="w"> </span>/storage/emulated/0/Download/c8750f0d.0<span class="w"> </span>/system/etc/security/cacerts/</span>&#10;<span class="code-line">chmod<span class="w"> </span><span class="m">644</span><span class="w"> </span>/system/etc/security/cacerts/c8750f0d.0</span>&#10;<span class="code-line"></span>&#10;<span class="code-line">reboot</span>&#10;</code></pre>
 </li>
<li> Check on Android<code> Settings/Security/Trusted credentials</code> - there should be CA certificate with name mitmproxy</li>
<li>Now you restart emulator with proxy settings:
<pre class="code-highlight" data-language="sh"><code><span class="code-line">./emulator<span class="w"> </span>-http-proxy<span class="w"> </span>http://localhost:8080<span class="w"> </span>-writable-system<span class="w"> </span>@Nougat_bare</span></code></pre>
</li>
<li>See traffic from the Android application in the mitmproxy</li>
</ul>




## Alternative setups


I've found above described setup easiest, but you might need different setup for various reasons:


<ul>
<li>The application might ignore <code>http&#95;proxy</code> settings intentionally - then you'll need to set mitmproxy into <a href="https://docs.mitmproxy.org/stable/concepts-modes/#transparent-proxy">transparent proxy mode</a></li>
<li>You can intercept traffic from physical phone, if you set your computer as wifi AP - setup is described <a href="https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/intercepting-ssl-and-https-traffic-with-mitmproxy-and-sslsplit/">here</a>. You'll need rooted device to install there system wide root certificate.</li>
</ul>




## Results


If everything went OK you'll be able to learn a bit more about application of your choice. For instance I learned that application was sending some information to facebook although it was not advertised anywhere and I do not have facebook account:

<a href="/wp-content/uploads/mitm.png"><img alt="mitm" class="alignnone wp-image-1993 size-full" decoding="async" height="563" loading="eager" sizes="(max-width: 882px) 100vw, 882px" src="/wp-content/uploads/mitm.png" srcset="/wp-content/uploads/mitm.png 882w, /wp-content/uploads/mitm-300x191.png 300w" width="882"/></a>

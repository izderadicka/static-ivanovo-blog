+++
title = "Flashing ROM to Samsung Phone"
path = "/flashing-rom-to-samsung-phone/"
date = "2016-05-01T06:16:23"
include_in_feeds = true
[extra]
wordpress_id = 1343
kind = "post"
node_key = "1343"
author = "admin"
source_url = "http://zderadicka.eu/flashing-rom-to-samsung-phone/"
source_guid = "http://zderadicka.eu/?p=1343"
source_date_gmt = "2016-05-01 05:16:23"
categories = ["Admin", "Tools"]
tags = ["Android", "flashing", "phone"]
+++
On Linux there is a great <a href="https://github.com/Benjamin-Dobell/Heimdall">Heimdall</a> tool.  I used it recently to flash stock ROM and custom recovery (<a href="https://twrp.me/">TWRP</a>) to my old Samsung S3 mini. Best to be used from command line.<span id="more-1343"></span>

Heimdall is in Ubuntu repos (or build from source):


```sh
sudo apt-get install heimdall-flash
```


Steps to flash:


<ol>
<li>Restart phone in download mode - push all tree button: Vol -, Home, Power</li>
<li>Connect to USB</li>
<li>
<pre class="code-highlight" data-language="sh"><code><span class="code-line">sudo<span class="w"> </span>heimdall<span class="w"> </span>detect</span></code></pre>
Heimdall must always run as root.
If phone is not found try other USB ports ( worked only on one in my notebook).</li>
<li>Get PIT in readable form:
<pre class="code-highlight" data-language="sh"><code><span class="code-line">sudo<span class="w"> </span>heimdall<span class="w"> </span>print-pit<span class="w"> </span>&gt;myphone_pit.txt</span></code></pre>
</li>
<li>Unzip, untar ROM archive</li>
<li>Match file names to partition names - look into PIT dump:
<span style="color: #999999;">--- Entry #21 ---</span>
<span style="color: #999999;"> Binary Type: 0 (AP)</span>
<span style="color: #999999;"> Device Type: 2 (MMC)</span>
<span style="color: #999999;"> Identifier: 20</span>
<span style="color: #999999;"> Attributes: 5 (Read/Write)</span>
<span style="color: #999999;"> Update Attributes: 5 (FOTA)</span>
<span style="color: #999999;"> Partition Block Size/Offset: 524288</span>
<span style="color: #999999;"> Partition Block Count: 2457600</span>
<span style="color: #999999;"> File Offset (Obsolete): 0</span>
<span style="color: #999999;">File Size (Obsolete): 0</span>
<strong>Partition Name: SYSTEM
</strong><strong>Flash Filename: system.img
</strong><span style="color: #999999;">FOTA Filename:</span></li>
<li>Flash partitions -  in case of stock ROM I did not have to flash all (probably because re-flashing same ROM back):
<pre class="code-highlight" data-language="sh"><code><span class="code-line">sudo<span class="w"> </span>heimdall<span class="w"> </span>flash<span class="w"> </span>--Kernel<span class="w"> </span>boot.img<span class="w"> </span>--CACHEFS<span class="w"> </span>cache.img<span class="w"> </span>--Kernel2<span class="w"> </span>recovery.img<span class="w"> </span>--SYSTEM<span class="w"> </span>system.img</span></code></pre>
To flash custom recovery:
<pre class="code-highlight" data-language="sh"><code><span class="code-line">sudo<span class="w"> </span>heimdall<span class="w"> </span>flash<span class="w"> </span>--Kernel2<span class="w"> </span>~/tmp/recovery.img</span></code></pre>
 </li>
</ol>

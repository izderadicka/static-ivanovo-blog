+++
title = "webresmon - Simple And Efficient Remote System Monitor"
path = "/projects/python/webresmon-simple-and-efficient-remote-system-monitor/"
date = "2013-01-20T19:10:00"
include_in_feeds = false
[extra]
wordpress_id = 495
kind = "page"
node_key = "495"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/webresmon-simple-and-efficient-remote-system-monitor/"
source_guid = "http://zderadicka.eu/?page_id=495"
source_date_gmt = "2013-01-20 18:10:00"
menu_order = 0
parent = "/projects/python/"
+++
Small Python (and Javascript for web interface) program to remotely monitor key system resources (CPU. memory, Net and Disk IO).
Stats are presented in form of live graphs:

<a href="/wp-content/uploads/webresmon2.png" rel="lightbox[webresmon]"><img alt="" class="wp-image-497 alignnone" decoding="async" height="350" loading="eager" src="/wp-content/uploads/webresmon2.png" title="webresmon2" width="800"/></a>


## Features:




<ul>
<li>presents CPU utilization (summarized for all CPUs), Memory usage (physical and swap and Net and Disk I/O (kB/s)</li>
<li>Web based interface with live graphs</li>
<li>can pause updates</li>
<li>can change update interval</li>
<li>multiple web clients (up to a limit) with possibility for different update intervals in each</li>
<li>efficient communication (via websocket), lightweighted server (python gevent), efficient data collection</li>
</ul>




## Usage:




<ul>
<li>depends on following python libraries - that must be installed  (recent versions) before starting this script:
<ul>
<li><a href="http://www.gevent.org/">gevent</a>,</li>
<li><a href="https://github.com/abourget/gevent-socketio">gevent-socketio</a>,</li>
<li><a href="http://pypi.python.org/pypi/Paste">paste</a>,</li>
<li><a href="http://code.google.com/p/psutil/">psutil</a></li>
</ul>
</li>
<li>then just run and connect with browser to given port -  http://your_address:8000</li>
</ul>


Licensed under <a href="http://www.gnu.org/licenses/gpl.html"> GPL v3</a>.

Source is available<a href="https://github.com/izderadicka/webresmon"> on GITHub</a>.

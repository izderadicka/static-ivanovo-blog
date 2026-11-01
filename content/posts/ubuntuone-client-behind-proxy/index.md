+++
title = "UbuntuOne client behind proxy"
path = "/ubuntuone-client-behind-proxy/"
date = "2013-08-28T12:04:07"
include_in_feeds = true
[extra]
wordpress_id = 615
kind = "post"
node_key = "615"
author = "admin"
source_url = "http://zderadicka.eu/ubuntuone-client-behind-proxy/"
source_guid = "http://zderadicka.eu/?p=615"
source_date_gmt = "2013-08-28 11:04:07"
[taxonomies]
category = ["Admin"]
tag = ["linux", "ubuntu", "ubuntuone"]
+++
It can sound bit weird, but most problematic platform for UbuntuOne client is Ubuntu itself - especially when your PC is behind proxy - or even worst when you're moving between several networks with your laptop, where some nets are using proxy.    <span id="more-615"></span>

First issues is that UbuntuOne client does not have proxy support installed by default, fix is easy :

`sudo apt-get install ubuntuone-client-proxy`

Second issue is more tricky -   if you change your proxy settings in Network Settings (which are stored in dconf backend) as you move from one network to another,  UbuntuOne client (especially the daemon process `ubuntuone-syncdaemon`) is not aware of this change and will not connect to cloud any more.   Quick and dirty fix is to restart `ubuntuone-syncdaemon` with a script like this:


```sh
pkill -f ubuntuone
sleep 2
/usr/bin/python /usr/lib/ubuntuone-client/ubuntuone-syncdaemon 1>/dev/null 2>&1 &
```


To automate this changes one can use for instance  a script in `/etc/NetworkManager/dispatcher.d/` that can detect particular network and set proxy and restart UbuntuOne.   I'm using <a href="/projects/python/thetool-quick-actions-for-desktop/" title="TheTool – Quick Actions for Desktop">thetool</a> \- a small tool of mine, that can detect network changes (via DBus) and take some actions - like to set proxy or run a script.

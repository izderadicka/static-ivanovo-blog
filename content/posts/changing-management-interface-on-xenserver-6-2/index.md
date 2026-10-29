+++
title = "Changing Management Interface on XenServer 6.2"
path = "/changing-management-interface-on-xenserver-6-2/"
date = "2014-10-20T12:30:13"
include_in_feeds = true
[extra]
wordpress_id = 909
kind = "post"
node_key = "909"
author = "admin"
source_url = "http://zderadicka.eu/changing-management-interface-on-xenserver-6-2/"
source_guid = "http://zderadicka.eu/?p=909"
source_date_gmt = "2014-10-20 11:30:13"
categories = ["Admin"]
tags = ["XenServer"]
+++
If you are changing management interface on XS (from eth1 to eth2, in my case, because eth1 was not connect to right subnet), be aware that management console must not update routing table for local subnet access appropriately - it keeps the record for previous interface there with same metric value, so actually old record will have preference.   So you might end up in situation, where you cannot access local subnet.

You can check with `route` command:


```sh
route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
10.163.127.32   *               255.255.255.224 U     0      0        0 xenbr1
10.163.127.32   *               255.255.255.224 U     0      0        0 xenbr2
default         prague03-lab-co 0.0.0.0         UG    0      0        0 xenbr2
```


Temporarily it can be fixed by:


```sh
route del -net 10.163.127.32  netmask 255.255.255.224 dev xenbr1

```


However this change is not saved - so it'll not survive reboot.

Final solution is to use xsconsole and "Network and Management Interface" /  "Emergency Network Reset" -  this function will reboot host.

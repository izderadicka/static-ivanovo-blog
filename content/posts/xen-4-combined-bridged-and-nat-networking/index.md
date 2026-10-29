+++
title = "Xen 4 - Combined Bridged And NAT Networking"
path = "/xen-4-combined-bridged-and-nat-networking/"
date = "2012-12-31T11:14:08"
include_in_feeds = true
[extra]
wordpress_id = 433
kind = "post"
node_key = "433"
author = "admin"
source_url = "http://zderadicka.eu/xen-4-combined-bridged-and-nat-networking/"
source_guid = "http://zderadicka.eu/?p=433"
source_date_gmt = "2012-12-31 10:14:08"
categories = ["Admin"]
tags = ["virtualization", "xen"]
+++
<a href="/wp-content/uploads/XenFuPandaWiki.png" rel="attachment wp-att-436"><img alt="" class="alignleft size-full wp-image-436" decoding="async" height="134" loading="eager" src="/wp-content/uploads/XenFuPandaWiki.png" title="XenFuPandaWiki" width="134"/></a>Normally Xen is deployed with plenty of of public IPs,  so it can use bridged networking and each virtual machine can have it's own public IP.  However in my case I was limited by only 1 public IP, but I wanted to run several VMs with services accessible from outside.  Solution was to modify XEN networking scripts.

Idea is to use an internal bridge with hidden IP subnet and to use NAT and port forwading so particular services on VMs can be reached from outside (on public IP, which is assigned to DOM0).This solution works for me successfully on Debian Squeeze.<span id="more-433"></span>

First define two new scripts in /etc/xen/scripts/

/etc/xen/scripts/network-bridge-nat


```sh
#!/bin/bash
#============================================================================
# Modified bridge - enables also kernel level forwarding

dir=$(dirname "$0")
. "$dir/network-bridge" "$@"

get_ip_info $netdev

echo  command is "$@", netdev is $netdev, gtw $addr_pfx

case "$command" in
    start)
	echo "1" > /proc/sys/net/ipv4/ip_forward
        # fist delete previous rules, so it is not stacking
        iptables -t nat -F POSTROUTING 
	iptables -t nat -A POSTROUTING -s $addr_pfx -j MASQUERADE
	;;

    stop)
	echo "0" > /proc/sys/net/ipv4/ip_forward
	iptables -t nat -D POSTROUTING -s $addr_pfx -j MASQUERADE
	;;
esac
```


/etc/xen/scripts/vif-bridge-nat


```sh
#!/bin/bash
#============================================================================
# modified vif-bridge to enable port mapping
logf=/root/test1.log
dir=$(dirname "$0")
. "$dir/vif-bridge" "$@"

case "$command" in
    online)
	$dir/portmap.py $ip
	;;
    offline)
        $dir/portmap.py -d $ip
        ;;
esac
```


 

Then create new python script /etc/xen/scripts/portmap.py,  which will define port mapping on public interface:


```python
#!/usr/bin/env python
netdev='eth0' 
# {'domU'_ip:[(domU_port, dom0port, ['tcp'|'udp']), (domU_port, dom0port), ..}
# 3rd param - protocol is optional - if not specified, tcp is default
portmap={'192.168.1.190': [(22, 2222), (80, 8888), (64738, 64738), (64738, 64738, 'udp')],
        '192.168.1.100': [(8081, 10001), (22, 10002)],
	}

# do not edit below this line
ip_tables_proto='iptables -%s PREROUTING -t nat -p %s -i %s --dport %d -j DNAT --to %s:%d\n'
import sys
is_delete=False
def usage():
	print >>sys.stderr, 'Usage: %s [-d] domU_ip' % sys.argv[0]
	sys.exit(1)
def is_ip(adr):
	ip_list=adr.split('.')
	if len(ip_list)!=4:
		usage()
	for i in ip_list:
		try:
			if int(i)>255 or int(i)<0:
				usage()
		except ValueError:
			usage()

args_no=len(sys.argv)

if args_no==3:
	if sys.argv[1]=='-d':
		is_delete=True
	ip=sys.argv[2]
	is_ip(ip)
elif args_no==2:

	ip=sys.argv[1]
	is_ip(ip)
else:
	usage()

if is_delete:
	action="D"
else:
	action="A"

mapping=portmap.get(ip, [])
cmds=''
for port_map in mapping:
	if len(port_map)==3 and port_map[2] in ('tcp', 'udp'):
		from_port, to_port, proto=port_map
	elif len(port_map)==2:
		from_port, to_port=port_map
		proto='tcp'
	cmds+=ip_tables_proto % (action, proto, netdev, to_port, ip, from_port)

import os
os.system(cmds)
```


<strong>netdev</strong> is public interface attached to DOM0
<strong>portmap</strong> is dictionary defining VMs port mapping, VMs should have static IPs - see comment in the code how to use it.  It should be defined for all your VMs, that should be accessible from outside.

Assure all scripts have execute rights.

Run in terminal:


```sh
echo dummy >> /etc/modules
```


Modify /etc/network/interfaces


```sh
# dummy interface
auto dummy0
iface dummy0 inet static
address 192.168.2.1
netmask 255.255.255.0
```


And modify <code> </code>/etc/xen/xend-config


```sh
(network-script 'network-bridge-nat netdev=dummy0')
(vif-script vif-bridge-nat)
```

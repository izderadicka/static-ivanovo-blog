+++
title = "Partly Cloudy - Openstack in VM"
path = "/partly-cloudy-openstack-in-vm/"
date = "2012-10-21T08:24:00"
include_in_feeds = true
[extra]
wordpress_id = 283
kind = "post"
node_key = "283"
author = "admin"
source_url = "http://zderadicka.eu/partly-cloudy-openstack-in-vm/"
source_guid = "http://zderadicka.eu/?p=283"
source_date_gmt = "2012-10-21 07:24:00"
categories = ["Admin"]
tags = ["cloud", "linux", "virtualization"]
+++
Having heard so much about clouds and 'Infrastructure as A Service' recently I decided to try Openstack - complete open source solution for cloud computing.   Openstack is actually a set of softwares, that together provide necessary services for a cloud infrastructure.  Openstack (Essex release) can be installed in virtual machine, Virtual Box in my case, so I gave it a try and here are some of my observations:<span id="more-283"></span>


### Installation


I used <a href="http://stackgeek.com/guides/gettingstarted.html">this guide for Ubuntu server</a>, which is available on Openstack web,  getting starting section. Actually it took bit more then advertised 10 minutes, due to some small issues and detours, but finally I got it running (computing service with all related components).   There are few important things for an installation in VM:


<ul>
<li><strong>VM disk size</strong> - since Nova VM disk images are stored in the root file system (see below for explanation), the disk size should be reasonably big - at least 20GB - to enable so experiments.  The guide also require separate volume block devices (nova-volume service), but this is something completely else then VM images.</li>
<li><strong>Memory</strong> - 4GB of memory worked for me without any issues</li>
<li><strong>Network interfaces</strong> -   the setup that worked for me :
Adapter 1 - Host-Only 'vboxnet0' - public cloud interface
Adapter 2 - Host-Only 'vboxnet1' - private cloud interface
Adapter 3 - NAT - internet access to install SW packages</li>
<li>If openstack is running in VM it has to use <strong>qemu as virtual machine type</strong> - in this case edit <code>/etc/nova/nova-compute.conf</code>  and put there <code>--libvirt&#95;type=qemu</code></li>
</ul>




### VNC console


Some additional effort is needed for VNC console to work ( as explained <a href="http://docs.openstack.org/essex/openstack-compute/install/apt/content/ch_install-dashboard.html#getting-started-with-vnc-proxy">here</a>):


<ul>
<li>Install this additional packages:
<code>apt-get install novnc nova-consoleauth</code></li>
<li>and edit /etc/nova/nova.conf
<code>--vnc&#95;enabled=true</code>
<code>--novncproxy&#95;base&#95;url=http://your&#95;public&#95;ip:6080/vnc&#95;auto.html</code></li>
</ul>




### VM images vs. block volumes


VM disk  images are stored at `/var/lib/nova/instances`.   Disk images are stored as qcow2 disk image format (this format enables 'Copy On Write', only data additional to base OS image are written here).  This was a source of  some confusion for me - because these images are not maintained by nova-volume services.   Block devices from nova-volume service are handled completely separately and  can be used as additional discs to VMs.


### Errors, Issues


The error reporting in Dashboard interface seemed to quite insufficient to me,    usually just VM instance status indicates that something went wrong, but not providing any clue what it is and how to fix it.  You must go to logs in /var/log/ , where each service has subdirectory with its logs and dig there for details.  Hope this will be better in new release.

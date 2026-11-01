+++
title = "Migrating xend virtual machines to xapi platform (XCP/XenServer)"
path = "/migrating-xend-virtual-machines-to-xapi-platform-xcpxenserver/"
date = "2014-09-19T13:04:32"
include_in_feeds = true
[extra]
wordpress_id = 878
kind = "post"
node_key = "878"
author = "admin"
source_url = "http://zderadicka.eu/migrating-xend-virtual-machines-to-xapi-platform-xcpxenserver/"
source_guid = "http://zderadicka.eu/?p=878"
source_date_gmt = "2014-09-19 12:04:32"
[taxonomies]
category = ["Admin"]
tag = ["xapi", "xen", "XenServer"]
+++
Xen hypervisor has currently 3 tool stacks : [xend](http://wiki.xen.org/wiki/XEND) \+ xm (which is now deprecated),   xl (new low level tool) and xapi+xe.   xapi is most advanced and it is used in [XenServer](http://xenserver.org/) (and [XCP](https://wiki.xenserver.org/index.php?title=XCP_Beginners_Guide) , but it is now also deprecated because XenServer is now open source).  Recently I have been migrating some virtual machines from Xen 4 with xend to XenServer  6.2. Below are details of migrating linux machines to new environment. <span id="more-878"></span>


### Differences between platforms


XenServer(XCP) is proving much more functionality, but for the price of much closed control on your dom0. Key differences are:



- Different tools: xm vs xe
- xend is using configuration files,  XenServer has an internal database, that can be manipulated by xe tool (or programmatically  via XenAPI bindings)
- In xend I used [xen-tools ](http://xen-tools.org/software/xen-tools/) in Debian to create virtual machines,  XenServer has built in templates for most common OSes (plus you can create your own templates as clones of existing VMs)
- For xend I used raw disk images as loopback devices (as provided by xen-tools). Xenserver is managing disk images itself (locally uses LVM2, but can also use shared storage).
- Official XenServer distribution has CentOS in dom0,  I used Debian previously (but XCP can be installed to new Debian)
- XenServer has generally more advanced, enterprise like features.





### Migration steps


On old host enable NFS share - so you can easily access disk images of exiting VMs:


```sh
apt-get install nfs-kernel-server nfs-common
echo /home/xen/domains *(ro,sync,no_subtree_check,fsid=0) >> /etc/exports
/etc/init.d/nfs-kernel-server reload
```


In XenServer dom0 you can mount share with this command:


```sh
mount -t nfs4 old_host:/  /mnt
```


Before migration you need to modify root fs on exiting machine - so first shut it down, then mount disk:


```sh
mount -o loop /home/xen/domains/my_vm/disk.img /mnt
```


Now you have to do two things:


<ol>
<li>Check that root file system has grub configuration /boot/grub/menu.lst. In new environment this disk might be available under slightly different name, so modify it here.   If you're creating menu.lst from scratch, assure that it points to exiting kernel (paravirtualization enabled kernel - or you need to install new kernel before migration) and ramdisk image with root fs. So updated menu.lst should look like:
<pre class="code-highlight" data-language="sh"><code><span class="code-line">default<span class="w">         </span><span class="m">0</span></span>&#10;<span class="code-line">timeout<span class="w">         </span><span class="m">2</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line">title<span class="w">           </span>Debian<span class="w"> </span>GNU/Linux</span>&#10;<span class="code-line">root<span class="w">            </span><span class="o">(</span>hd0,0<span class="o">)</span></span>&#10;<span class="code-line">kernel<span class="w">          </span>/boot/vmlinuz-2.6.32-5-xen-amd64<span class="w"> </span><span class="nv">root</span><span class="o">=</span>/dev/xvda<span class="w"> </span>ro</span>&#10;<span class="code-line">initrd<span class="w">          </span>/boot/initrd.img-2.6.32-5-xen-amd64</span>&#10;</code></pre>
Originally root was /dev/xvda1  in new system it's /dev/xvda.</li>
<li>Modify /etc/fstab on old root -  same change to root device as before.</li>
</ol>


Now you can create new VM on XenServer:


```sh
vm_id=`vm-install new-name-label=my_new_vm template="Other install media"`
#make size  equal to exiting raw image size!
xe vm-disk-add vm=$vm_id device=0 disk-size=2147483648
# make it bootable
vm-disk-list vm=$vm_id # get right VBD is to $vbd_id,   VDI to $vdi_id
vbd-param-set uuid=$vbd_id bootable=true
# add network interface
xe network-list # get right network id to $net_id
xe vif-create device=0 vm-uuid=$vm_id network-uuid=$net_id
# set memory as needed
xe vm-memory-limits-set dynamic-min=256MiB dynamic-max=512MiB static-min=256MiB static-max=512MiB vm=$vm_id
#set VM params to boot PV kernel
xe vm-param-set uuid=$vm_id PV-bootloader=pygrub PV-args="-- quiet console=hvc0" HVM-boot-policy=
```


Key insight here is that size of new disk must be same as size of current VM disk image. And then import image of existing VM to new VID:


```sh
xe vdi-import uuid=$vdi_id filename=/mnt/my_vm/disk.img # assure file is readable
```


Now you should be able to boot up new machine, few final touches are needed:



- login via console
- modify other setups as necessary (net configuration ...)
- install XenServer tools
- reboot


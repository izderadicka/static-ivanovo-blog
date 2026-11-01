+++
title = "Diskless PC (booting from USB stick) with Ubuntu"
path = "/diskless-pc-booting-from-usb-stick-with-ubuntu/"
date = "2013-03-18T14:52:06"
include_in_feeds = true
[extra]
wordpress_id = 508
kind = "post"
node_key = "508"
author = "admin"
source_url = "http://zderadicka.eu/diskless-pc-booting-from-usb-stick-with-ubuntu/"
source_guid = "http://zderadicka.eu/?p=508"
source_date_gmt = "2013-03-18 13:52:06"
[taxonomies]
category = ["Admin"]
tag = ["diskless", "linux", "overlay fs"]
+++
Recently I decided to revamp my linux HTPC and this time to do it properly - there is no disk and all media are on separate server (or NAS - I prefer server, because I'd like to run some other things there, which might be problematic to run on pure NAS box). New PC should boot from from common USB stick - 8GB - value around 5 EUR (I thought it would be more convenient to build  system and I did not have any server yet to boot from network only - actually old HTPC would become server, but first new HTPC has to be created). To overcome two major issues of common USB stick - limit on number of write operations (too much writes decrease lifetime of the stick) and slow write operations speed I decided to use overlays file system (or sometimes called union file system), where (once all system is set up) all writes go to memory - this is similar to linux live CDs or USB sticks. In order to be able to do some user customizations after installation and that user can save various data his home directory, the home directory is hosted on server/NAS and shared via NFS. The  recipe described below is for xubuntu 12.10.<span id="more-508"></span>


<ol>
<li>You will need 8GB stick for system, 1GB or more USB stick for installation media (or DVD mechanic)  and PC hardware.</li>
<li>Install Xubuntu to 8GB stick - format it as one single partition with ext2 file system (no swap, because it does not make sense, when stick will be read-only, also fs with journalling like ext3 or ext4 are not appropriate).</li>
<li>Because all write operations really slow down work I recommend at least to mount /tmp to RAM FS and add noatime option to root fs as soon as possible - modify root line in and put this to /etc/fstab and reboot:
<code>tmpfs /tmp tmpfs nodev,nosuid 0 0&#10;</code></li>
<li>Setup NFS serverver - as described here [https://help.ubuntu.com/community/SettingUpNFSHowTo](https://help.ubuntu.com/community/SettingUpNFSHowTo) - to host home directory later</li>
<li>Install overlayroot package ( part of 12.10,  for earlier version of ubuntu use  ppa:cloud-initramfs-tools/ppa)
Overlay fs isa  new union like file system - which now seems to be preferred over its older colleagues.
More information about overlayroot package is available here  [http://blog.dustinkirkland.com/2012/08/introducing-overlayroot-overlayfs.html](http://blog.dustinkirkland.com/2012/08/introducing-overlayroot-overlayfs.html)</li>
<li>Install nfs and autofs:
<code>sudo apt-get install nfs-common autofs&#10;</code></li>
<li>Install all other packages you need plus customize your system as you need
( XBMC setup for AMD  grafic card is described in detail here http://youresuchageek.blogspot.fr/2012/06/xbmc-install-and-config-howto-for-linux.html, only that swap optimizations are irrelevant here, because we do not use swap).</li>
<li>Add server IP address to /etc/hosts (if you do not have dns running) - this will simplify other steps
for instance: <code>&#10;nas 192.168.1.110</code></li>
<li>Mount remote home  to temporary location
<code>sudo mount -t nfs4 nas:/homes&#95;root&#95;remote /mnt</code>and copy all content of home there
and copy all data from hone there:
<code>copy -av /home/my&#95;user /mnt</code></li>
<li>Edit /etc/default/grub  - add kernel boot parameter <code>overlayroot=tmpfs</code>,   edit this to look like below:
<code>GRUB&#95;CMDLINE&#95;LINUX&#95;DEFAULT="quiet splash overlayroot=tmpfs"</code>
(This will assure that during normal boot root fs will be read-only on the USB stick and all changes will be written to memory,  however if you choose an emergency boot in grub then USB stick will be mounted as read/write - this will enable you  to update/maintain your system  easily later).
And run this command to update grub configuration:
<code>sudo update-grub</code></li>
<li> Configure autofs
First edit /etc/auto.master and add to it
<code>/home  /etc/auto.home</code>
then create /etc/auto.home  like this:
<code>&#42; -fstype=nfs4 nas:/homes&#95;root&#95;remote/&amp;</code></li>
<li>I ran into problem with race conditions between autofs and networkmanager  and lightdm.   Basically autofs tried to mount homes before network was ready and lightdm tried to auto login user before home directory was mounted. To handle this issue I had to modify some upstart scripts (in /etc/init/):
Modify /etc/init/autofs.conf, change start conditions like this:
<code>start on ( runlevel &#91;2345&#93;</code>
<code>        and filesystem</code>
<code>        and net-device-up IFACE!=lo)</code>and modify /etc/init/lightdm.conf  start condition like this:
<code>start on ((filesystem</code>
<code>        and started autofs</code>
<code>                and ...</code></li>
<li>After this reboot should get to your user desktop.</li>
</ol>


 


## Update


I've have been recently using same approach for Xubuntu 14.04 and here is couple of things that can be done  better/easier:


<ol>
<li>Not using autofs anymore -   it's enough to call mount in lightdm upstart script - /etc/init/lightdm.conf:
<code>start on (</code>
<code>    ...</code>
<code>    and net-device-up IFACE!=lo) </code>
<code>....</code>
<code>pre-start script</code>
<code>    mount -t nfs4 server:/home-export /home</code>
<code>    exit 0</code>
<code>end script</code></li>
<li>overlayroot can be more easily configured in <code>/etc/overlayroot.conf</code> (even better in <code>/etc/overlayroot.local.conf</code>, which will not be overwritten by future possible updates)</li>
<li>To enable easily to boot to writable root:
Edit /etc/grub.d/40_custom and copy there main grub entry for Ubuntu (can current find in<code> /boot/grub/grub.cfg</code>) - change here entry name and add kernel parameter <code>overlayroot=disabled</code>
and run <code>sudo update-grub</code></li>
</ol>

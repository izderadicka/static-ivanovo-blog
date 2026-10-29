+++
title = "Poor man's backup for XenServer"
path = "/poor-mans-backup-for-xenserver/"
date = "2014-10-31T11:02:42"
include_in_feeds = true
[extra]
wordpress_id = 933
kind = "post"
node_key = "933"
author = "admin"
source_url = "http://zderadicka.eu/poor-mans-backup-for-xenserver/"
source_guid = "http://zderadicka.eu/?p=933"
source_date_gmt = "2014-10-31 10:02:42"
categories = ["Admin"]
tags = ["backup", "xapi", "XenServer"]
+++
I'm running several XenServer hosts and wanted to provide some basic backup of VMs. I decided to use USB disk - XenServer 6.2  provides great support for external disks.   I was looking around for some simple free tool for backup (to backup several VMs from different servers in scheduled batches), but did not find anything suitable (simple scripts were not flexible enough, bigger solutions were overkill in my case) - so I created my own solution <a href="/projects/python/xapi-back-simple-xen-backup-tool/" title="xapi-back Simple Xen Backup Tool">xapi-back</a>

My setup is:


<ul>
<li>I created small Debian VM and attached USB disk to it (in XS 6.2 this external disk will stay connected to VM after  VM or host reboot)</li>
<li>Installed <a href="/projects/python/xapi-back-simple-xen-backup-tool/" title="xapi-back Simple Xen Backup Tool">xapi-back</a></li>
<li>Created special user for backup</li>
<li>Scheduled VM backups with cron</li>
</ul>


Main advantages of xapi-back  compared to other similar solutions:


<ul>
<li><strong>easy to install</strong> - just download and run <code>python setup.py</code></li>
<li><strong>easy to configure</strong> -   just one simple configuration file with details of xen servers and some basic backup parameters</li>
<li><strong>self-contained</strong>  - does not need xe or other tools (as many other solutions) and can run on any computer ( not only in xenserver Dom0 as some scripts,  generally I think it's not good practice to run backups in Dom0, better is to have it separately).</li>
<li><strong>complete</strong> - you can do all basic tasks from xapi-back via simple command line interface <code>xb</code> -  list VMs and their last backups,  backup, restore,  set VMs for scheduled backup ( with help of cron). You'll not need any other management tools (xe, XenCenter, ....) to make backups.</li>
<li><strong>self-maintaining</strong> - xapi-back can be scheduled and run automatically. It maintains backups' storage, keeps N last backups and removes old backups so it can run unattended for months.</li>
<li><strong>compact</strong> - it's very small solution so it can run on any machine, only python  is needed (it can run easily on minimal Debian install or even on NAS)</li>
<li><strong>universal</strong> - can run on any POSIX system, where python is running ( any Linux, FreeBSD, Solaris ...)</li>
<li><strong>multiple servers</strong> - can handle multiple XenServers and server's pools</li>
</ul>

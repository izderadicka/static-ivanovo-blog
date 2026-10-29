+++
title = "Software RAID 1 And LVM"
path = "/software-raid-1-and-lvm/"
date = "2013-04-22T08:31:21"
include_in_feeds = true
[extra]
wordpress_id = 531
kind = "post"
node_key = "531"
author = "admin"
source_url = "http://zderadicka.eu/software-raid-1-and-lvm/"
source_guid = "http://zderadicka.eu/?p=531"
source_date_gmt = "2013-04-22 07:31:21"
categories = ["Admin"]
tags = ["linux", "lvm", "raid1"]
+++
While adding more capacity to my Ubuntu 12.04 based server I decided to use two disks in RAID 1 - although the whole topic is well discussed and described, it still took me some time to put all pieces together, so here I'd like to share my experiences. Plus there are couple of decision point on the way, so I'd like to explained my decisions, based on informations  I read.<span id="more-531"></span>


### Ingredients


Ubuntu Server 12.04 (installed on separate disk(s) - standard install + OpenSSH + anything you need)

MDADM - Multidisk Admin

LVM - Linux volume manager

parted - disk partion manager

2 x 3TB SATA disks (WD Red in my case, I was really surprised how quiet these disks are )


### Decisions


<strong>What should come first RAID1 or LVM?</strong>
Initially I was wondering - what should come first - LMV  or RAID -   I know that LVM can provide also some SW mirroring of logical volumes.   Based on few articles I read it looks like creating RAID volume first  and then adding it as the physical volume to LVM and creating and volume group on it and then logical volume(s) on it  is the preferred way. Key reason for this approach is simplicity - in mdadm it's much easier to create RAID and to maintain it, in LVM it seems to be much  more complicated.

<strong>Should raw disk (/dev/sdb) be the part of RAID or do I need to create a disk partition first (/dev/sdb1)?</strong>
This is an interesting question because we can do both - RAID can be easily set up  both ways (if this is not boot disk - this is bit different story and there partitions are required).  There has been some discussions around and I finally decided to use a partition.  Reasons for this decision were:


<ul>
<li>If one disk fails and I have to replace it with possibly different model, then that new disk might have slightly different size - so having a partition that is a bit smaller then total disk capacity might be an advantage in future.  I also learned that this is a good  practice in HW RAIDs - not using the whole capacity of disks to enable to replace them with slightly different models.</li>
<li>If  raw disk from my array will be inserted to other computer alone, it will not recognize any partitions on it.  In case of my partition it will at least recognize that there is a RAID partition.</li>
<li>Someone has written that during boot he gets warning that there are no partitions on the disk, if disk is raw.</li>
</ul>


<strong>How to align partition on the disk?</strong>
Modern disks have sector size 4096B (physical sector size), but in Linux logical sector size is 512B.  This means that we need to align at least on physical sector size -  meaning to 8 logical sectors multiple, however the best practice is to align to 1MiB  - e.g 2048 logical sectors.   Loosing less the 1MiB from 3T is nothing and it will assure best performance and compatibility with the system.

<strong>What filesystem?</strong>
It of course depends.  I used XFS, because I'm storing mostly media files on the disk and for this type of load XFS is considered quite fitting.


###  Steps


Install mdadm and lvm: <code>&#10;sudo apt-get install lvm mdadm</code>

partition disk (note that for partitions bigger then 2T we cannot use fdisk any more):<code>&#10;parted /dev/sdb</code>
`mklabel gpt`
`unit MiB`
`mkpart primary 1 -1`
`set 1 raid on`
<code>name 1 Mirror&#95;A&#95;1&#10;quit&#10;</code>

Same for /dev/sdc - just use different name for the volume "Mirror\_A\_2"

Now create raid volume:
`sudo mdadm --create --verbose /dev/md0  --level=1 --raid-devices=2 /dev/sdb1 /dev/sdc1`

and set it up so it'll be available after reboot:
`sudo sh -c "mdadm --detail --scan >> /etc/mdadm/mdadm.conf"`
` sudo update-initramfs -u  `

Now create logical volume (consuming all raid1 volume):
`sudo pvcreate -v /dev/md0`
`sudo vgcreate -v data /dev/md0`
`sudo lvcreate -v -n data -l 100%FREE data`

and finally create filesystem,  add entry to /etc/fstab and mount:
`sudo mkfs.xfs /dev/data/data`
`sudo mkdir /data`
add this to /etc/fstab:`  /dev/data/data /data xfs  auto 0 0 `
`sudo mount /data`


### Future


When current disks capacity will not be enough I can add another 2 disks in RAID1 volume and add it to same logical volume and extend file system.

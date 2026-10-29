+++
title = "Replacing failed disk in Linux RAID1"
path = "/replacing-failed-disk-in-linux-raid1/"
date = "2014-10-21T06:04:53"
include_in_feeds = true
[extra]
wordpress_id = 904
kind = "post"
node_key = "904"
author = "admin"
source_url = "http://zderadicka.eu/replacing-failed-disk-in-linux-raid1/"
source_guid = "http://zderadicka.eu/?p=904"
source_date_gmt = "2014-10-21 05:04:53"
categories = ["Admin"]
tags = ["linux", "raid1"]
+++
In <a href="/software-raid-1-and-lvm/" title="Software RAID 1 And LVM">this past article</a> I've written about setting a sofware based RAID1 on Linux.   After less then two years one disks failed,  so I had to replace it - here are my experiences with this procedure.<span id="more-904"></span>


### Symptoms


After forced reboot (power off), server did not boot -  rebooting manually I've found that problem is with raid -  system complains about raid disk failure and offers to start with raid1  in degraded mode.  If this was not chosen it opened maintenance shell.


### Identifying failed disk


Boot with degraded raid1. Check current raid status


```sh
cat /proc/mdstat 
Personalities : [linear] [multipath] [raid0] [raid1] [raid6] [raid5] [raid4] [raid10] 
md0 : active raid1 sdb1[0]
      2930133824 blocks super 1.2 [2/1] [U_]
      
unused devices: <none>

```


Clearly second disk is missing form raid1,  next you should check what's wrong with the  second disk:


<ul>
<li>check logs and linux kernel messages - like <code>dmesg | grep sdc</code>,</li>
<li>check SMART  status of the disk: <code>sudo smartctl -a /dev/sdc</code> (also note down disk serial for later)
check attributes like "Raw_Read_Error_Rate",  or "Offline_Uncorrectable" for non zero values</li>
<li>optionally run test on the disk  <code>sudo smartctl --test=long /dev/hdc</code> (takes several hours)</li>
</ul>




### Remove failed disk


After boot with degraded raid1 problematic disk should be already removed from raid group. Check it with:


```sh
sudo mdadm --detail /dev/md0
```


If problematic disk is still in raid group you have to remove disk from group:


```sh
sudo mdadm --manage /dev/md0 --fail /dev/sdc1
sudo mdadm --manage /dev/md0 --remove /dev/sdc1
```


Then the disk could be physically removed from server (double check disk serial, that you are removing correct disk).


### Install replacement disk


Install new disk and start with degraded raid1.   Create same partitions on new disk (install gdisk package):


```sh
sgdisk -R /dev/sdc /dev/sdb # careful - not to switch names
sgdisk -G /dev/sdc # create new GUID for new partition
```


After you can also change new partition name  (with  parted).
And add new partion to raid1:


```sh
mdadm --manage /dev/md0 --add /dev/sdc1
```


And check cat /proc/mdstat  that raid1 is synchronizing:


```sh
cat /proc/mdstat 
Personalities : [linear] [multipath] [raid0] [raid1] [raid6] [raid5] [raid4] [raid10] 
md0 : active raid1 sdc1[2] sdb1[0]
      2930133824 blocks super 1.2 [2/1] [U_]
      [>....................]  recovery =  0.1% (3767680/2930133824) finish=349.5min speed=139543K/sec

```


or `mdadmin --detail:`


```sh
sudo mdadm --detail /dev/md0
/dev/md0:
        Version : 1.2
  Creation Time : Fri Mar  8 12:21:09 2013
     Raid Level : raid1
     Array Size : 2930133824 (2794.39 GiB 3000.46 GB)
  Used Dev Size : 2930133824 (2794.39 GiB 3000.46 GB)
   Raid Devices : 2
  Total Devices : 2
    Persistence : Superblock is persistent

    Update Time : Mon Oct 20 21:49:33 2014
          State : clean, degraded, recovering 
 Active Devices : 1
Working Devices : 2
 Failed Devices : 0
  Spare Devices : 1

 Rebuild Status : 1% complete

           Name : nas:0  (local to host nas)
           UUID : f0135e24:8557a5bb:c13ac7a7:9a5cfd6a
         Events : 7014

    Number   Major   Minor   RaidDevice State
       0       8       17        0      active sync   /dev/sdb1
       2       8       33        1      spare rebuilding   /dev/sdc1

```


After synchronization everything should look normal again:


```sh
cat /proc/mdstat 
Personalities : [linear] [multipath] [raid0] [raid1] [raid6] [raid5] [raid4] [raid10] 
md0 : active raid1 sdc1[2] sdb1[0]
      2930133824 blocks super 1.2 [2/2] [UU]
```




```sh
sudo mdadm --detail /dev/md0
/dev/md0:
        Version : 1.2
  Creation Time : Fri Mar  8 12:21:09 2013
     Raid Level : raid1
     Array Size : 2930133824 (2794.39 GiB 3000.46 GB)
  Used Dev Size : 2930133824 (2794.39 GiB 3000.46 GB)
   Raid Devices : 2
  Total Devices : 2
    Persistence : Superblock is persistent

    Update Time : Tue Oct 21 06:54:02 2014
          State : clean 
 Active Devices : 2
Working Devices : 2
 Failed Devices : 0
  Spare Devices : 0

           Name : nas:0  (local to host nas)
           UUID : f0135e24:8557a5bb:c13ac7a7:9a5cfd6a
         Events : 8531

    Number   Major   Minor   RaidDevice State
       0       8       17        0      active sync   /dev/sdb1
       2       8       33        1      active sync   /dev/sdc1

```

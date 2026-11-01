+++
title = "Running Oracle VM Template for DB 12c in XenServer"
path = "/running-oracle-vm-template-for-db-12c-in-xenserver/"
date = "2015-01-08T10:39:56"
include_in_feeds = true
[extra]
wordpress_id = 946
kind = "post"
node_key = "946"
author = "admin"
source_url = "http://zderadicka.eu/running-oracle-vm-template-for-db-12c-in-xenserver/"
source_guid = "http://zderadicka.eu/?p=946"
source_date_gmt = "2015-01-08 09:39:56"
[taxonomies]
category = ["Admin"]
tag = ["Oracle 12c", "XenServer"]
+++
As many may know Oracle VM Server is based on Xen hypervisor so it's possible to run VMs prepared for Oracle VM on other Xen based solutions like XenServer or OCP.  Main difference is management of VMs - Oracle VM is using xm, while recent XenServer is using newer xapi stack.  But paravirtualized Linux kernels can run easily on both.

Oracle is providing [VM templates](http://www.oracle.com/technetwork/server-storage/vm/database-templates-12c-11gr2-1972804.html) with many of it's key products - like for instance new Oracle 12c database.   In this article we will show how to run Oracle 12c Database VM template on XenServer 6.2.<span id="more-946"></span>

First **a warning** \-  this is not officially supported configuration, so if you are looking for safety and support follow official guidelines.

Connect to DOM0 on your XenServer and run following commands (assuming that you unzipped OVM template to NFS location some\_server:/)


```sh
xe vm-install new-name-label=oracle-12 template=Oracle\ Enterprise\ Linux\ 6\ \(64-bit\)
xe vm-disk-list uuid=ec2de1ce-fa05-237a-807a-49fce3d53ecb 
xe vdi-resize uuid=56e863c1-2a50-4668-a9a8-3352c26ae186 disk-size=12884901888
xe network-list
xe vif-create device=0 network-uuid=3f41fc63-6c31-e852-29ec-2bc831eb6931 vm-uuid=ec2de1ce-fa05-237a-807a-49fce3d53ecb 
xe vm-memory-limits-set vm=oracle-12 dynamic-min=4GiB dynamic-max=8GiB static-min=4GiB static-max=8GiB
xe vm-param-set uuid=ec2de1ce-fa05-237a-807a-49fce3d53ecb VCPUs-max=2
xe vm-param-set uuid=ec2de1ce-fa05-237a-807a-49fce3d53ecb VCPUs-at-startup=2
xe vm-disk-add vm=oracle-12 device=1 disk-size=sc3-ssc.cz.oracle.com32212254720
xe vm-param-set uuid=ec2de1ce-fa05-237a-807a-49fce3d53ecb  PV-bootloader=pygrub
mount -t nfs4 some_server:/ /mnt
xe vm-disk-list vm=oracle-12 
xe vdi-import uuid=56e863c1-2a50-4668-a9a8-3352c26ae186 filename=/mnt/oracle12/OVM_OL6U4_X86_64_12101DBRAC_PVM/System.img
xe vdi-import uuid=c99e5328-729a-44fa-b0e3-5a04fa46c8b7 filename=/mnt/oracle12/OVM_OL6U4_X86_64_12101DBRAC_PVM/Oracle12101DBRAC_x86_64-xvdb.img

```


This should give you a VM ready to be started.
Start VM in XenServer management (XenCenter, [OXM](https://github.com/OpenXenManager/openxenmanager), [Xen Orchestra](https://xen-orchestra.com/) or whatever management solution you are using) and go to console.

VM  starts with some configuration questionnaire,   first just type enter on any initial inputs, then you need to answer **yes** to question:  *"Do you want to access the 2-node RAC interview on console ?"* and  then on first next question (prepare to wait a bit before it occurs) type **OUT**. This  ends configuration script and gets you to console login.

Login as root:ovsroot  and then do following command:


```sh
cd /u01/racovm

cp netconfig-sample-si.ini netconfig.ini
vi netconfig.ini
#edit - for DNSIP you can put several servers - just surround all with " and separate with space
# it's shell - so assure no spaces before/after =
# uncomment CLONE_SINGLEINSTANCE_HA=yes, comment CLONE_SINGLEINSTANCE
./netconfig.sh -n1

vi params.ini
# modify needed params like FS_DATAFILE_LOCATION or RACASMGROUPNAME
# following command will build single instance DB according to params.ini
# Default is single tentatnt db
./buildsingle.sh



```


And now you should have running single instance Oracle 12c database.

It's good to apply latest patches - easiest way is to get latest patch set update (PSU).  [This article](http://www.oradba.ch/2013/08/how-to-find-latest-oracle-database-patchset/) describes how to find latest PSUs.

Before application of patches upgrade OPatch to latest version (download latest OPatch from Oracle support):


```sh
mv $ORACLE_HOME/OPatch/ OPatch-old
unzip -d $ORACLE_HOME p6880880_121010_Linux-x86-64.zip 
opatch version

```


Then just download appropriate PSUs, unzip and follow instructions to install them.

+++
title = "Quick And Dirty Oracle Backup"
path = "/quick-and-dirty-oracle-backup/"
date = "2012-12-01T17:13:35"
include_in_feeds = true
[extra]
wordpress_id = 387
kind = "post"
node_key = "387"
author = "admin"
source_url = "http://zderadicka.eu/quick-and-dirty-oracle-backup/"
source_guid = "http://zderadicka.eu/?p=387"
source_date_gmt = "2012-12-01 16:13:35"
[taxonomies]
category = ["Admin"]
tag = ["linux", "oracle 11g"]
+++
I have an Oracle 11g installation running in virtual machine (under Xen). Oracle is used for APEX development and some host few local applications for our team. From time to time I need to do cold backups - to keep data around or to move them to another VM on different server, which is running identical version of oracle  and can be used as cold backup eventually.   The backup device is an USB disk with FAT32 filesystem (FAT32 was chosen a while ago for compatibility reason - to be able to attach it to almost any OS) and the disk is attached to other server. FAT32 means that there is a limit on file size, so the database backup need to be split to chunks (backup is 10-15 GB). Of course RMAN can do proper job, but since I'm no real DBA I want to have something quick ( data are not mission critical and also it is no problem to bring DB down) - so **warning** do not apply this procedure for important databases - no guarantee that it will work in all circumstances and** you may loose your data** .<span id="more-387"></span>

To do a cold backup of db:


```sh
echo shutdown immediate | sqlplus / as sysdba
cd /path_where_database_dir_is
tar czv your_database_dir | ssh root@other.server.com "split -b 2G - /backup_dir/database.tgz_"
echo startup | sqlplus / as sysdba
```


Then to restore backup:


```sh
echo shutdown immediate | sqlplus / as sysdba
cd /path_where_database_dir_is
#or better just to rename to keep files if something goes wrong
rm  your_database_dir/*
ssh root@other.server.com "cat  /backup_dir/database.tgz_*" | tar xzv
#try to start
echo startup | sqlplus / as sysdba
```


When you start database you might get and error concerning control file inconsistency - to solve it:


<ul>
<li>check control files locations:   <code>SHOW PARAMETER control&#95;files</code></li>
<li>shutdown database</li>
<li>copy control file, which was restored from backup to the other location</li>
<li>startup database</li>
</ul>

+++
title = "xapi-back Simple Xen Backup Tool"
path = "/projects/python/xapi-back-simple-xen-backup-tool/"
date = "2014-10-31T10:46:56"
include_in_feeds = false
[extra]
wordpress_id = 927
kind = "page"
node_key = "927"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/xapi-back-simple-xen-backup-tool/"
source_guid = "http://zderadicka.eu/?page_id=927"
source_date_gmt = "2014-10-31 09:46:56"
menu_order = 0
parent = "/projects/python/"
+++
**xapi-back **is a simple backup tool for XenServer or XCP - xen hypervisors using xapi toolstack.   xapi-back is a command line tool with simple and clear interface (command + options). Tool is written in python.


### Features





- simple command line interface
- can backup VMs from multiple hosts
- backup of live VMs (creates temporary snapshot of VM)
- can combine several backups into one batch (which then can be scheduled in cron)
- keeps x previous backups (can be set in config file)
- backups are gziped to save space
- ideal for small scale backups to USB disk
- and of course free and open source





### Install


Source is on [github](https://github.com/izderadicka/xapi-back).

To install on new system run as root (assuming pip is already installed):

`pip install git+https://github.com/izderadicka/xapi-back.git#egg=xapi-back`

This will install xb tool and create sample configuration file in ` /etc/xapi-back.cfg  `or `~/.xapi-back.cfg` if run as non root user. (For security reasons it better to have this file in your home directory with 0600 access - you can copy it or install as non root user).<code>&#10;</code>


### Usage


Edit configuration file `~/.xapi-back.cfg` or ` /etc/xapi-back.cfg  `(if you have both the one in home directory is used), file has JSON syntax.  Change:


<ul>
<li>your hosts
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="s2">&quot;servers&quot;</span>:<span class="o">[</span></span>&#10;<span class="code-line"><span class="o">&#123;</span><span class="s2">&quot;name&quot;</span>:<span class="s2">&quot;your server&quot;</span>,</span>&#10;<span class="code-line"><span class="w"> </span><span class="s2">&quot;url&quot;</span>:<span class="s2">&quot;https://your_server.example.com&quot;</span>,</span>&#10;<span class="code-line"><span class="w"> </span><span class="s2">&quot;user&quot;</span>:<span class="s2">&quot;root&quot;</span>,</span>&#10;<span class="code-line"><span class="w"> </span><span class="s2">&quot;password&quot;</span>:<span class="s2">&quot;your_pass&quot;</span></span>&#10;<span class="code-line"><span class="o">}</span></span>&#10;<span class="code-line"><span class="o">]</span>,</span></code></pre>
</li>
<li>backup directory root:
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="s2">&quot;storage_root&quot;</span>:<span class="s2">&quot;/backup/vms&quot;</span>,</span></code></pre>
</li>
<li>number of backup copies to keep:
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="s2">&quot;storage_retain&quot;</span>:5,</span></code></pre>
</li>
<li>compression - backed-up VM image can be either uncompress ("none"), or compressed in xb ("client"), or compressed on XenServer ("server") ( in dom0 as part of export process).
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="s2">&quot;compress&quot;</span>:<span class="s2">&quot;client&quot;</span>,</span></code></pre>
**WARNING:** This is pretty important decision and must not be changed afterwards, when storage_root already contains some backups, because modes are mutually incompatible!
"client" - is a default mode and usually good unless you require some special scenario covered by other two. Backup speed is limited by gzip speed or slow network. Compression is offloaded from Dom0, which is usually good thing,
"none" -  it's  good, if you have fast disks and network and you do not care about disk space, backup is not limited by gzip, but only by I/O speed.
"server" - compression in done in XenServer Dom0. It's good if you have slow network (making backups over Internet for instance).</li>
<li>Compression level 0 (no compression, but gzip still calculates checksum) - 9 (best compression,  but slowest - level 9 is about 4 - 5 times slower then level 1 and additional space gained is not so significant -  usually 10 - 15% ). It works only for "client" compression:
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="s2">&quot;compress_level&quot;</span>:1,</span></code></pre>
</li>
<li>log file (optional):
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="s2">&quot;log_file&quot;</span>:<span class="s2">&quot;/var/log/xapi-back/log.txt&quot;</span></span></code></pre>
</li>
<li>Email log - there is possibility to send session log after each xb run - this section in config file can specify details:
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="s2">&quot;mail_log&quot;</span>:<span class="w"> </span><span class="o">&#123;</span></span>&#10;<span class="code-line"><span class="w">  </span><span class="s2">&quot;host&quot;</span><span class="w"> </span>:<span class="w"> </span><span class="s2">&quot;&quot;</span>,</span>&#10;<span class="code-line"><span class="w">  </span><span class="s2">&quot;port&quot;</span><span class="w"> </span>:<span class="w"> </span><span class="m">25</span>,</span>&#10;<span class="code-line"><span class="w">  </span><span class="s2">&quot;from&quot;</span><span class="w"> </span>:<span class="w"> </span><span class="s2">&quot;&quot;</span>,</span>&#10;<span class="code-line"><span class="w">  </span><span class="s2">&quot;to&quot;</span><span class="w"> </span>:<span class="w"> </span><span class="o">[</span><span class="s2">&quot;&quot;</span>,<span class="s2">&quot;&quot;</span><span class="o">]</span>,</span>&#10;<span class="code-line"><span class="w">  </span><span class="s2">&quot;user&quot;</span>:<span class="w"> </span><span class="s2">&quot;&quot;</span>,</span>&#10;<span class="code-line"><span class="w">  </span><span class="s2">&quot;password&quot;</span>:<span class="w"> </span><span class="s2">&quot;&quot;</span>,</span>&#10;<span class="code-line"><span class="w">  </span><span class="s2">&quot;secure&quot;</span>:<span class="w"> </span>false,</span>&#10;<span class="code-line"><span class="w">  </span><span class="s2">&quot;subject&quot;</span>:<span class="w"> </span><span class="s2">&quot;&quot;</span></span>&#10;<span class="code-line"><span class="o">}</span></span></code></pre>
 </li>
</ul>


Test then you can connect to your hosts:


```sh
xb hosts
Name    URL                            Can Connect
------  -----------------------------  -------------
sc1     https://sc1.example.com  True
sc2     https://sc2.example.com  True
sc3     https://sc3.example.com  True

```


Next try this command:


```sh
xb list
Host    VM              UUID      State    AutoBck    AutoBck Batch    Last Backup       Dur. (m)
------  --------------  --------  -------  ---------  ---------------  ----------------  ----------
sc1     proxy           136a8...  Running  true       daily            2014-11-08 13:25  164.8
sc1     checker         da90e...  Running  true       daily
sc2     apex            56b3c...  Running  true       weekly-sun
sc2     xen-manage      d9437...  Running  true       test             2016-02-15 17:28  35.7
sc2     gitrepo         1d285...  Running  true       daily
sc3     backup          89116...  Running  false
sc3     oracle-12c      1086d...  Running  true       weekly-sat
sc3     Docker          8e93b...  Running  false
sc3     deki            93501...  Running  true       weekly           2016-01-20 11:38  4.3
sc3     cml             43ee0...  Running  true       weekl
```


You see list of all available VMs with information about their backups.

There are several  possibilities how to backup VM:

<strong>manual - single VM
</strong>


```sh
xb backup --host sc3 --vm xen-manage
Progress 3.33%

```


Backup speed is basically limited by speed of gzip compression, which can be 30-60MB/s on common machine for level 1 (and can be much slower for highest levels). So if you are really concerned about speed you can turn off compression in configuration.  Also there is --insecure switch, which will force http connection with server for backup transport - theoretically it can speed up backup a bit, because you are not encrypting transport, but in practice I did not mention notable difference - TLS encryption is pretty fast .

If there are VMs with same name you'll receive error about non-unique name, you need to then specify VM with `--uuid` argument -  usually first few character of UUID is enough.

**manual -  batch**

Add VMs to batch:


```sh
xb enable --host sc3 --vm xen-manage --batch weekly
```


And run batch:


```sh
xb backup-batch --batch weekly
```


xapi-back can backup of running VMs - it creates a temporary snapshot for backup purpose, (which is basically a template in XenServer - so you should take this in account when restoring).  If you'd rather like to shutdown machine before backup and do a cold backup use --shutdown option in backup command.

Backups can be also easily scheduled via cron (that was an idea behind batches -  to create different batches, which can be scheduled with different periodicity) -  see sample cron script:


```sh
# m h  dom mon dow   command
15 1 * * * /usr/local/bin/xb backup-batch --batch daily --no-progress
15 2 * * 6 /usr/local/bin/xb backup-batch --batch weekly --no-progress
```


To restore a VM use:


```sh
xb restore --host sc3 --vm xen-manage
```


It'll restore  last backup of VM under same name  on given host (or snapshot name, which is Temp. backup of ...). There are some additional restore options, check `xb restore -h`. Restore is done to default Storage Repository (SR),  unless you specify specific SR with`  --sr_id `  argument.
If you are restoring snapshot and you need to restore as VM (not as template) use `--as-vm` parameter.

You can also  list SRs available on the host with`  xb srs --host host_name `.

Restoring other then latest backup has to be done outside the tool - just find correct file (under backup root in directory with VM name) ,  gunzip it and use `xe vm-import` or other tool to import VM.

+++
title = "What Is This Weird File Name in My Samba Share?"
path = "/what-is-this-weird-file-name-in-my-samba-share/"
date = "2017-10-17T12:00:22"
include_in_feeds = true
[extra]
wordpress_id = 1752
kind = "post"
node_key = "1752"
author = "admin"
source_url = "http://zderadicka.eu/what-is-this-weird-file-name-in-my-samba-share/"
source_guid = "http://zderadicka.eu/?p=1752"
source_date_gmt = "2017-10-17 11:00:22"
categories = ["Admin"]
tags = ["file names", "samba"]
+++
In IT there are big things and there are small things. Some small things can be pretty annoying and they seem to stay here forever.  One of these annoying little things is difference between restrictions for file names in Windows versus  unix/linux (others are for instance legacy character encodings, http proxy support, these things has teased me many times in past).  Have you ever seen strange file name like W3NEM5~I on shared disc instead of meaningful file name, that you expected? If so and you're interested what's going on continue reading. <span id="more-1752"></span>

So what is the issue actually:  while linux is pretty tolerant for file names -  only two characters  are not allowed:  forward slash / and  null byte \\x00 , Windows are much more restrictive - they do not allow any control character below \\x20 (32 decimal, space character), but what is worst neither of rather common characters:  \< \> : " / \\ ? | \* is allowed  and if this is not enough there is one more special rule that file names cannot end with space or dot.   One of places where this discrepancy between filesystems is often visible are <a href="https://www.samba.org/">Samba</a> shares - sharing linux based filesystem across local network. Samba is one of most common ways for running small home <a href="https://en.wikipedia.org/wiki/Network-attached_storage">NAS</a>.

When Samba is sharing linux filesystem, it has to somehow cope with this problem - that potentially  some valid local file names are not valid for network clients.  Samba handles it with so called file name mangling (here is <a href="http://www.oreilly.com/openbook/samba/book/ch05_04.html">bit outdated description</a>, in Samba 3 it's slightly different). Mangling basically means that windows illegal name is transformed to legal name automatically and Samba server maintains mapping between real name and mangled name so client can work with file normally. Downsize of this method is that mangled names are not very informative, matching with original file name only by first letter.

So what we can do if we do not want to see those ugly file names? There are several possibilities, which I'll list later in the article.  First let's look at directory in linux server - it contains files with problematic names (last one in first row has space at the end):


```sh
wrong-<-test  wrong-|-test  wrong-?-test  wrong-*-test  wrong-test 
wrong->-test  wrong-:-test  wrong-"-test  wrong-\-test  wrong-test.
```


 

First options indeed is to do nothing.  The discrepancy between file systems is real and this is how to Samba deals with it.  You'll see files like this (in <a href="https://wiki.gnome.org/Apps/Nautilus">Nautilus</a> file explorer):
<a href="/wp-content/uploads/files1.png"><img alt="files1" class="alignnone size-full wp-image-1756" decoding="async" height="349" loading="eager" sizes="(max-width: 564px) 100vw, 564px" src="/wp-content/uploads/files1.png" srcset="/wp-content/uploads/files1.png 564w, /wp-content/uploads/files1-300x186.png 300w" width="564"/></a>

 

Another option is to switch off file names mangling -  you can easy do this in Samba configuration file  /etc/samba/smb.conf (and reload smbd):


```sh
[global]
mangled names= no

```


Behaviour for problematic file names  in this case is 'undefined' in linux - gnome vfs show files with dot or space at the end and they can be manipulated, other files are not visible in Nautilus and this is what can be seen in terminal:


```sh
$ ls -la /run/user/1000/gvfs/smb-share\:server\=nas\,share\=data_all/tmp/wrong_names/
ls: cannot access '/run/user/1000/gvfs/smb-share:server=nas,share=data_all/tmp/wrong_names/wrong-\-test': No such file or directory
ls: cannot access '/run/user/1000/gvfs/smb-share:server=nas,share=data_all/tmp/wrong_names/wrong-:-test': No such file or directory
ls: cannot access '/run/user/1000/gvfs/smb-share:server=nas,share=data_all/tmp/wrong_names/wrong-"-test': Invalid argument
ls: cannot access '/run/user/1000/gvfs/smb-share:server=nas,share=data_all/tmp/wrong_names/wrong-<-test': Invalid argument
ls: cannot access '/run/user/1000/gvfs/smb-share:server=nas,share=data_all/tmp/wrong_names/wrong->-test': Invalid argument
ls: cannot access '/run/user/1000/gvfs/smb-share:server=nas,share=data_all/tmp/wrong_names/wrong-|-test': Invalid argument
ls: cannot access '/run/user/1000/gvfs/smb-share:server=nas,share=data_all/tmp/wrong_names/wrong-*-test': Invalid argument
ls: cannot access '/run/user/1000/gvfs/smb-share:server=nas,share=data_all/tmp/wrong_names/wrong-?-test': Invalid argument
total 0
drwx------ 1 ivan ivan 0 Oct 15 20:09 .
drwx------ 1 ivan ivan 0 Oct 14 11:55 ..
?????????? ? ?    ?    ?            ? wrong-<-test
?????????? ? ?    ?    ?            ? wrong->-test
?????????? ? ?    ?    ?            ? wrong-|-test
?????????? ? ?    ?    ?            ? wrong-:-test
?????????? ? ?    ?    ?            ? wrong-?-test
?????????? ? ?    ?    ?            ? wrong-"-test
?????????? ? ?    ?    ?            ? wrong-*-test
?????????? ? ?    ?    ?            ? wrong-\-test
-rwx------ 1 ivan ivan 0 Oct 15 20:09 wrong-test 
-rwx------ 1 ivan ivan 0 Oct 14 12:02 wrong-test.

```


If the share is mounted directly with mount -t cifs then directory looks normal, but files with special characters in name are not accessible:


```sh
$ ls
wrong-<-test  wrong->-test  wrong-|-test  wrong-:-test  wrong-?-test  wrong-"-test  wrong-*-test  wrong-\-test  wrong-test   wrong-test.
$ cat 'wrong-<-test' 
cat: 'wrong-<-test': No such file or directory

```


And what is even worst - if you try edit such file it's possible, but actually new file is created with modified name. On client new file appears to have same name  in the terminal (and Nautilus displays only one of duplicated files)  - so it's complete mess:


```sh
$ ls 
wrong-<-test  wrong-<-test  wrong->-test  wrong->-test  wrong-|-test  wrong-:-test  wrong-:-test  wrong-?-test  wrong-"-test  wrong-*-test  wrong-*-test  wrong-\-test  wrong-test   wrong-test.
```


Actually what is happening behind scene is that problematic character is replaced by 3 byte code on the server ( ef 80 a3 in one case, which is UTF-8 code in private code area, so officially it's no known character) :


```sh
$ ls  $'wrong-\xef\x80\xa3-test'
wrong--test
```


In windows files are visible, but cannot be accessed ( error is  path does not exist).

Another option is to use <a href="https://www.samba.org/samba/docs/man/manpages/vfs_catia.8.html">catia vfs module</a> which is by default bundled with Samba -in can be activated with this addition to smb.conf :


```sh
[your-share]
       # share definition
        vfs objects = catia
        catia:mappings = 0x22:0xa8,0x2a:0xa4,0x2f:0xf8,0x3a:0xf7,0x3c:0xab,0x3e:0xbb,0x3f:0xbf,0x5c:0xff,0x7c:0xa6,0x20:0xb1

```


With this modification windows 'hostile' characters are mapped to other characters ( the trick is that mapping has to work in both directions - so best strategy is to use some rare characters to avoid naming conflicts). So names looks like this:
<a href="/wp-content/uploads/files2.png"><img alt="files2" class="alignnone size-full wp-image-1757" decoding="async" height="349" loading="lazy" sizes="(max-width: 531px) 100vw, 531px" src="/wp-content/uploads/files2.png" srcset="/wp-content/uploads/files2.png 531w, /wp-content/uploads/files2-300x197.png 300w" width="531"/></a>

So now most of file names  is much more similar to original file names (only dot at the end of file name is still mangled). The disadvantage would be that it's harder to write file name manually.

When combined with previous option (switch off mangling), it displays even first one correctly (but in windows it  still cannot be accessed).

Last option is to assure that filenames are consistent with both worlds (basically means consistent with Windows as it is more restrictive).  I personally found this option best, because it assures trouble-free consistency across systems.  Ideally application has to be aware of these restrictions and assure them programatically.   If by accident we create files with wrong names we can use simple script to rename these files (for instance like this one, if we are not particular about possibility of name collisions and eventually overwriting some files, otherwise bit more sophisticated script is needed ):


```sh
find . -depth ! -path . -execdir bash -c "echo -n '{}' | sed 's/[\*>\?\"|\\\:<]/-/g' | sed -r 's/\.+$| +$//g'|  xargs -0  mv -b '{}' 2>&1 | grep -v 'same file'" \;
```

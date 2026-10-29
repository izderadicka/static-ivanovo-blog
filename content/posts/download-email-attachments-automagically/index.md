+++
title = "Download Email Attachments Automagically"
path = "/download-email-attachments-automagically/"
date = "2015-12-09T10:21:55"
include_in_feeds = true
[extra]
wordpress_id = 1157
kind = "post"
node_key = "1157"
author = "admin"
source_url = "http://zderadicka.eu/download-email-attachments-automagically/"
source_guid = "http://zderadicka.eu/?p=1157"
source_date_gmt = "2015-12-09 09:21:55"
categories = ["Programming", "Tools"]
tags = ["IMAP", "python"]
+++
Emails are still one of the most important means of electronic communication.  Apart of everyday usage with some convenient client ( like superb <a href="https://www.mozilla.org/en-US/thunderbird/">Thunderbird</a>), from time to time one might need to get messages content out of the mailbox and perform some bulk action(s) with it - an example could be to download all image attachments from your mailbox into some folder - this can be done easily manually for few emails, but what if there is 10 thousands of emails?  Your mailbox is usually hosted on some server and you can access it via <a href="https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol">IMAP</a> protocol. There are many possible  ways how to achieve this, however most of them require to download or synchronize full mailbox locally and then extract required parts from messages and process them.  This could be very inefficient indeed.   Recently I have a need for automated task like one above - search messages in particular IMAP mailbox,  identify attachments of certain type and name and download then and run a command with them, after command is finished successfully delete email (or move it to other folder).   Looking around I did not found anything suitable, which would meet my requirements (Linux, command line, simple yet powerful).  So having some <a href="http://old.zderadicka.eu/mailexp.php">experiences with IMAP and python</a>, I decided to write such tool myself.   It's called <a href="/projects/python/imap_detach-tool-download-email-attachments/">imap_detach</a>, and you can check details <a href="/projects/python/imap_detach-tool-download-email-attachments/">on it's page</a>. Here I'd like to present couple of use cases for this tool in hope they might be useful for people with similar email processing needs.

<span id="more-1157"></span>Let's start with simple example:


```sh
detach.py -H imap.example.com -u user -p password  -f ~/tmp/attachments/{year}/{from}/{name} -v 'attached'
```


This will download all attachments from all emails in user's  inbox and save them in subdirectories - first grouped by year, then by sender. If there are many emails it can take quite some time. In some cases you might notice error messages complaining that output file isa  directory, which means that attachment does not have any name defined within the email.

This is resolved in next example by using more sophisticated naming of output file using {name|subject+section}  replacement ( | serves as 'or',  + joins two variables - so if attachment does not have name we use subject and section as a file name -  so it can look like "Important message\_2.1")

We also can try to add argument --threads, which will enable concurrent download of attachments in separate threads:


```sh
detach.py -H imap.example.com -u user -p password  -f ~/tmp/attachments/{year}/{from}/{name|subject+section} -v --threads 5 'attached'
```


In my tests with my gmail mailbox concurrent download with 5 threads was 3.7 times faster then single threaded ( downloading ~1200 files, ~450MB).

But we are not limited just to email attachments, all email parts are available to us.  What about to get all plain text parts and put them into one big file, which we can later use for some analysis :


```sh
detach.py -H imap.example.com -u user -p password -v -c "cat >> /home/you/tmp/emails.txt" -v 'mime="text/plain"'

```


We might be more specific on which messages to get - for instance we are interest just in junk messages from this year:


```sh
detach.py -H imap.example.com -u user -p password -v -c "cat >> /home/you/tmp/junk{year}.txt" -v 'mime="text/plain" & year=2015 & flags="Junk"'
```


Text message parts in an email can have different charsets encodings ( for instance for Czech language we can  have iso-8859-2 or win-1250 or UTF-8). The tool solves this by re-encoding text to UTF-8, so the in output file all text is in this charset.

Similarly we can look at messages  in other folders - say folder Spam and all it's sub-folders and just look for text in first sub-part of the email message (that should be the text of the email) and getting only emails, where subject starts with "Re:":


```sh
detach.py -H imap.example.com -u user -p password -v -c "cat >> /home/you/tmp/spam.txt" -v --folder "Spam**" 'mime="text/plain" & (section="1" | section~="1.") & subject^="re:"'
```


And what about finding all links in your mailbox (with a bit of quote escape madness):


```sh
detach.py -H imap.example.com -u user -p password -v -c 'grep -ioP '\''<a .*?href=["'\'\\\'\''][^"'\'\\\'\'']+["'\'\\\'\'']'\'' | sed -r '\''s/.*href=["'\'\\\'\'']([^"'\'\\\'\'']+)["'\'\\\'\'']/\1/i'\'' >> /home/you/tmp/links.txt' 'mime="text/html"'
```


Or using fairly complex filter:


```sh
detach.py -H imap.example.com -u user -p password -v -f "/home/you/tmp/{name|subject+section}" -v '(mime="application/pdf" & ! from ~= "bill" & ! cc~="james" & size>100k & size<1M) | (mime="image/png" & ! name^="bi" & from~="bill") | (mime^="image" & (name$="gif" | from~="matt"))'
```


And there are many more possibilities - check details on the<a href="/projects/python/imap_detach-tool-download-email-attachments/"> tool home page</a>.

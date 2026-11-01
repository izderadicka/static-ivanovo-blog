+++
title = "Sudo without password"
path = "/sudo-without-password/"
date = "2012-10-29T08:47:38"
include_in_feeds = true
[extra]
wordpress_id = 310
kind = "post"
node_key = "310"
author = "admin"
source_url = "http://zderadicka.eu/sudo-without-password/"
source_guid = "http://zderadicka.eu/?p=310"
source_date_gmt = "2012-10-29 07:47:38"
[taxonomies]
category = ["Admin"]
tag = ["linux"]
+++
I need to use superuser privileges quite often and not so particular about security, but still want to work mainly under my own user.  The solution is to set sudo not to require password for my user:

`sudoedit /etc/sudoers`

add following line to the end:

`your_user_name ALL=NOPASSWD:ALL`

As noted this is basically a security risk, so apply only if you are sure what you are doing.

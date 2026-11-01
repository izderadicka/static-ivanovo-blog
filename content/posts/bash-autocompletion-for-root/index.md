+++
title = "Bash Autocompletion for Root"
path = "/bash-autocompletion-for-root/"
date = "2012-10-29T08:57:12"
include_in_feeds = true
[extra]
wordpress_id = 313
kind = "post"
node_key = "313"
author = "admin"
source_url = "http://zderadicka.eu/bash-autocompletion-for-root/"
source_guid = "http://zderadicka.eu/?p=313"
source_date_gmt = "2012-10-29 07:57:12"
[taxonomies]
category = ["Admin"]
tag = ["linux"]
+++
Debian/Ubuntu do not have bash autocompletion enabled for  root account by default.  When working under root account, this is quite missed feature,   but luckily it can be enabled very easily:

`cd ~`
`apt-get install bash-completion  # if not installed - like in minimal Debian install`
`nano .bashrc`

add folowing to the file:

`if [ -f /etc/bash_completion ]; then`
`    . /etc/bash_completion`
`fi`

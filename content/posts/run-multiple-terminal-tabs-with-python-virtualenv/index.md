+++
title = "Run Multiple Terminal Tabs with Python Virtualenv"
path = "/run-multiple-terminal-tabs-with-python-virtualenv/"
date = "2016-05-27T11:53:19"
include_in_feeds = true
[extra]
wordpress_id = 1382
kind = "post"
node_key = "1382"
author = "admin"
source_url = "http://zderadicka.eu/run-multiple-terminal-tabs-with-python-virtualenv/"
source_guid = "http://zderadicka.eu/?p=1382"
source_date_gmt = "2016-05-27 10:53:19"
[taxonomies]
category = ["Programming"]
tag = ["linux", "python", "virtualenv"]
+++
[Virtualenv](https://github.com/pypa/virtualenv) is a must have for python development.  If your project is a complex beast consisting  of multiple services/components you want them see running  in different terminals  (ideally tabs of one terminal window).  Staring all terminal manually could be cumbersome. This simple script starts terminal tabs (in gnome-terminal) with activated virtual environments and eventually appropriate services/applications started:


```sh
#!/bin/bash
VENV=".venv/bin/activate"

export PYTHONPATH=~/workspace/asexor

gnome-terminal \
--tab -e "bash --rcfile $VENV -ci 'cd asexor && crossbar start'" \
--tab -e "bash --rcfile $VENV" \
--tab -e "bash --rcfile $VENV" \
--tab -e "bash --rcfile $VENV"
```


None `-ci` argument -  interactive shell must be enforced to run command with virtual environment loaded.w

Also gnome terminal recently drop support for --title parameter, which enabled to set title to the tab (really do not understand why, because it was very useful).   So now our tabs will have same prompt.

This can be somehow fixed with modification of virtualenv activate script to include terminal escape sequence  shown below (thus we will see current terminal directory as tab title):


```sh
PS1="\[\e]0;\W\a\](`basename \"$VIRTUAL_ENV\"`)$PS1"
```

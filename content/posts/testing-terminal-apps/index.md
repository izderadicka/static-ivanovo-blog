+++
title = "Testing Terminal Apps"
path = "/testing-terminal-apps/"
date = "2015-12-07T08:27:16"
include_in_feeds = true
[extra]
wordpress_id = 1185
kind = "post"
node_key = "1185"
author = "admin"
source_url = "http://zderadicka.eu/testing-terminal-apps/"
source_guid = "http://zderadicka.eu/?p=1185"
source_date_gmt = "2015-12-07 07:27:16"
categories = ["Programming"]
tags = ["terminal", "testing"]
+++
Sometimes you need to test a terminal application, which reads user inputs from terminal and prints results to terminal.  These tasks are very common in introductory programming courses. Simple testing tool can help here, and students can learn good practices - automatic testing - from the very beginning.  I've been looking around and does not find anything, simple enough, that ie can be used by beginner and provide basic actions - for  testing output of program and supplying inpu to itt.  So I created such tool - <a href="https://github.com/izderadicka/simpletest">simpletest</a>.<span id="more-1185"></span> (written in Python, using <a href="https://pexpect.readthedocs.org/en/stable/">pexpect</a>)

You just need to create test script as text file, where lines are started by \> (for expected output) or  \< (for supplying input into program).  Here is trivial example of the test script:


```sh
$ tests/test2.sh
> Your wish:\\
< mys
> mys
? 0
---
```


For this script:


```sh
#!/bin/bash

read -p "Your wish:" WISH
echo $WISH
```


 

And here is result of running it:


```sh
$ stest tests/test2.txt 
0 $ tests/test2.sh
1 > Your wish:\\
2 < mys
3 > mys
4 ? 0
5 ---
All OK :-)

```


And here other scripts, which yields  error:


```sh
$ stest tests/echo-err.txt 
1 $ echo hi
2 > hou
PROGRAM ERROR at line 2 (> hou): Program ended before expected output, with this output: hi
```


Usage is very simple,  key advantage is that user can just copy interaction with program from terminal to text editor, quickly amened it and test script is ready.

There are couple more features - checking return code (?),  running program ($), line continuation (\\\\) and sending control control characters, which together provide everything one needs to create simple test cases. <a href="https://github.com/izderadicka/simpletest/blob/master/README.md">More in tool readme file</a>.

Tool can be easily installed via <a href="https://pip.pypa.io/en/stable/">pip</a> ( if you do not have pip on your system you can install with `sudo apt-get install python-pip` on Debian/Ubuntu,  more details about <a href="https://pip.pypa.io/en/stable/installing/">installing pip</a>):


```sh
# you'll need git to runn this
# sudo apt-get install git # on debian/ubuntu
sudo pip install git+https://github.com/izderadicka/simpletest.git#egg=simpletest
```

+++
title = "Subtle evil of close_fds parameter in subprocess.Popen"
path = "/subtle-evil-of-close_fds-parameter-in-subprocess-popen/"
date = "2015-05-09T07:45:36"
include_in_feeds = true
[extra]
wordpress_id = 1017
kind = "post"
node_key = "1017"
author = "admin"
source_url = "http://zderadicka.eu/subtle-evil-of-close_fds-parameter-in-subprocess-popen/"
source_guid = "http://zderadicka.eu/?p=1017"
source_date_gmt = "2015-05-09 06:45:36"
[taxonomies]
category = ["Programming"]
tag = ["python"]
+++
In python newly created sub-process inherits file descriptors from parent process and these descriptors are left open - at least this was default till python ver. 3.3. `subprocces.Popen` constructor has parameter `close_fds` (defaults to False on python ver. 2.7), which can say if to close inherited FDs or not.  Leaving them open FDs for child process can lead to many problems as explained [here](https://www.python.org/dev/peps/pep-0446/) and [here](http://bugs.python.org/issue7213).<span id="more-1017"></span>

I was also hit by this problem in very strange manner -  when working on [btclient](https://github.com/izderadicka/btclient) I experienced strange behaviour in HTTP client (based on urllib2), when a sub-process was launched HTTP requests behaved slightly differently - which caused remote server to return many 503 errors.  This was very weird, and it was driving me mad, until I tracked it down to the issue of inheriting opened file descriptors in sub-process.

I still wonder how exactly can sub-process ( it was basically any program - even something as simple as `bash -c "sleep 1000"` \- it was just enough to inherit opened FDs) influence behaviour of socket ( on linux platform) and thus behaviour of HTTP  protocol. I'd be glad if somebody more profound in linux  can explain me exact mechanism behind this.

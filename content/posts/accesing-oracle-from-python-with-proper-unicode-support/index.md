+++
title = "Accesing Oracle from Python (with proper unicode support)"
path = "/accesing-oracle-from-python-with-proper-unicode-support/"
date = "2015-01-02T20:18:02"
include_in_feeds = true
[extra]
wordpress_id = 970
kind = "post"
node_key = "970"
author = "admin"
source_url = "http://zderadicka.eu/accesing-oracle-from-python-with-proper-unicode-support/"
source_guid = "http://zderadicka.eu/?p=970"
source_date_gmt = "2015-01-02 19:18:02"
[taxonomies]
category = ["Admin"]
tag = ["oracle", "python"]
+++
It's not obvious to set it right, so I'm putting some notes here:

Installation is described [here](http://csgeek-random.blogspot.co.uk/2013/04/installing-python-cxoracle-on-ubuntu.html).
Few comments:


<ul>
<li>ORACLE_HOME is needed just for installation</li>
<li>If you add client library path to <code>/etc/ld.so.conf.d/oracle.conf</code>   and update <code>ldconfig</code>, you don't need to export modified LD_LIBRARY_PATH</li>
<li>when you install Oracle client library and set environment,  you can install cx_oracle also via <code>pip install cx&#95;Oracle</code></li>
</ul>


The **crucial step** not mentioned in the installation guide is  to set <a href="http://docs.oracle.com/cd/E11882_01/server.112/e10729/ch3globenv.htm#i1006280"><strong>NLS_LANG</strong></a> environment variable - this should be in the environment of your python program using cx\_oracle.  So for instance for Flask+SQLAlchemy you can have:


```python
if app.config.get('SQLALCHEMY_DATABASE_URI').startswith("oracle"):
    os.environ['NLS_LANG']= 'AMERICAN_AMERICA.AL32UTF8'
```


Without this variable oracle client is using 7bits ASCII! So any unicode character will raise "UnicodeEncodeError: 'ascii' codec can't encode character" error.

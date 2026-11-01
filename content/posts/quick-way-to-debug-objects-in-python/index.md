+++
title = "Quick Way to Debug Objects in Python"
path = "/quick-way-to-debug-objects-in-python/"
date = "2012-10-02T14:42:40"
include_in_feeds = true
[extra]
wordpress_id = 216
kind = "post"
node_key = "216"
author = "admin"
source_url = "http://zderadicka.eu/quick-way-to-debug-objects-in-python/"
source_guid = "http://zderadicka.eu/?p=216"
source_date_gmt = "2012-10-02 13:42:40"
[taxonomies]
category = ["Programming"]
tag = ["python"]
+++
Often it is necessary to print an object to debugging log. This small utility function can help to print all  properties:


```python
import inspect, pprint
def dprint(object):    
    props=filter(lambda t: not t[0].startswith('__'),
                 inspect.getmembers(object, lambda m: not inspect.ismethod(m)))   

    pprint.pprint(props)
```

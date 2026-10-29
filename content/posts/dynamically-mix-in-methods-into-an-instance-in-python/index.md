+++
title = "Dynamically Mix in Methods into An Instance in Python"
path = "/dynamically-mix-in-methods-into-an-instance-in-python/"
date = "2013-09-16T11:17:42"
include_in_feeds = true
[extra]
wordpress_id = 626
kind = "post"
node_key = "626"
author = "admin"
source_url = "http://zderadicka.eu/dynamically-mix-in-methods-into-an-instance-in-python/"
source_guid = "http://zderadicka.eu/?p=626"
source_date_gmt = "2013-09-16 10:17:42"
categories = ["Programming"]
tags = ["python"]
+++
As Python is a dynamic language it offers many possibilities how to manipulate object instances during runtime.   We may for instance inject methods from another class,  achieving similar results as  if  this instance has this calls as a mix-in super class. This approach could be useful to hack some existing libraries with extra functionality, in case we have to work with created  instances.

This function will inject methods from `mixin_class` into `instance` assuring that method is properly bound to the instance.


```python
import types

def mixin(instance, mixin_class):
    """Dynamic mixin of methods into instance - works only for new style classes"""
    for name in mixin_class.__dict__:
        if name.startswith('__') and name.endswith('__') \
        or not  type(mixin_class.__dict__[name])==types.FunctionType:
            continue

        instance.__dict__[name]=mixin_class.__dict__[name].__get__(instance)
```


<span id="more-626"></span>We use here python descriptor protocol (`__get__`)  to get bound method (same thing is actually happening when instance is getting a method from its super class). Alternatively a bound method could be created by this expression (python 2.7):


```sh
import types

instance.x=types.MethodType(SomeClass.x.im_func, instance)
```

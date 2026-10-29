+++
title = "Django tests auto-discover"
path = "/django-tests-auto-discover/"
date = "2013-09-05T10:47:18"
include_in_feeds = true
[extra]
wordpress_id = 622
kind = "post"
node_key = "622"
author = "admin"
source_url = "http://zderadicka.eu/django-tests-auto-discover/"
source_guid = "http://zderadicka.eu/?p=622"
source_date_gmt = "2013-09-05 09:47:18"
categories = ["Programming"]
tags = ["django", "python", "unit testing"]
+++
Django framework  provides integrated tests runner, which can be started by `./manage/py test` (see <a href="https://docs.djangoproject.com/en/1.5/topics/testing/overview/#running-tests">docs</a> for more details, key advantage of this runner is that it'll create new empty database for tests, so they do not interfere with each other or your development instance).   This tests runner runs unit tests from `tests.py` or `models.py` modules in active projects.  However in larger projects we would like to have other organization of tests code -   have for instance special test package within project that  contains many testing modules, each focused on particular aspect of the application.<span id="more-622"></span>

This simple code in tests.py will assure that test cases are auto-discovered from `test_cases` package within the project:


```python
import os
import re
import importlib
import unittest
from django import test

TESTS_DIR='test_cases'

curr_dir=os.path.split(__file__)[0]
tests_dir=os.path.join(curr_dir, TESTS_DIR)

def is_test_case(cls):
    return issubclass(cls, unittest.TestCase ) and cls!= unittest.TestCase and cls!=test.TestCase

files=os.listdir(tests_dir)
for f in files:
    m=re.match('^test.*\.py$', f, re.IGNORECASE)
    mod_name=os.path.splitext(f)[0]

    if m:
        mod=importlib.import_module(os.path.basename(curr_dir)+'.'+TESTS_DIR+'.'+mod_name)
        for name in dir(mod):
            mbr=getattr(mod, name)
            if isinstance(mbr, type) and is_test_case(mbr):
                globals()[name]=mbr
                print 'Found test case', name
```


This code imports all test cases (classes that inherit from `unittest.TestCase`) from any module that starts with "test" (within test\_cases package)  into the tests module, so django runner can find them here.

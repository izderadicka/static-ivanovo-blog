+++
title = "Python packages distribution"
path = "/python-packages-distribution/"
date = "2014-01-15T10:39:08"
include_in_feeds = true
[extra]
wordpress_id = 718
kind = "post"
node_key = "718"
author = "admin"
source_url = "http://zderadicka.eu/python-packages-distribution/"
source_guid = "http://zderadicka.eu/?p=718"
source_date_gmt = "2014-01-15 09:39:08"
[taxonomies]
category = ["Programming"]
tag = ["python"]
+++
Currently python options for code distribution  are bit messy as [described here](http://python-notes.boredomandlaziness.org/en/latest/pep_ideas/core_packaging_api.html).   I spent some time to find right way how to create setup script, which will install external dependencies,   so here is the recipe for python3:<span id="more-718"></span>

Create virtual virtual environment for your project:

<code>virtualenv -p /usr/bin/python3 .&#10;</code>

Then create setup.py file - two important things:


```python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
```


Import setup function from setuptools,   this l enables to specify dependencies, which should be installed  automatically by `pip` or `easy_setup`.


```python
setup(name='packageX',
      version='1.0',
      description='Sample package',
      packages=['x'],
      author='Your name',
      author_email='your email',
      requires= ['six (>=1.4.1)', 'bitarray (>=0.8.1)'],
      install_requires=['six>=1.4.1', 'bitarray>=0.8.1'],
      provides=['x']
      )
```


It is important that <strong><code>install&#95;requires</code></strong> keyword is  included. Also note different syntax of version requirements  - `requires` vs `install_requires` . (requires and provides are probably not necessary ).

Test files,  readme, license  files etc.   specify them in MANIFEST.in file in root of distribution - something like this:


```sh
recursive-include tests *.txt *.py
exclude tests/something_temp.py
include README.md
```


Once all code is ready you can create distribution with command:

`python setup.py sdist`

This will create packed distribution in `dist` subdirectory  and then you can try to install in another virtual environment by:

`pip install path/to/dist/packageX-1.0.0.tar.gz`

+++
title = "OpenShift Experiencies"
path = "/openshift-experiencies/"
date = "2015-08-01T18:13:33"
include_in_feeds = true
[extra]
wordpress_id = 1056
kind = "post"
node_key = "1056"
author = "admin"
source_url = "http://zderadicka.eu/openshift-experiencies/"
source_guid = "http://zderadicka.eu/?p=1056"
source_date_gmt = "2015-08-01 17:13:33"
categories = ["Admin", "Programming"]
tags = ["PaaS", "python"]
+++
<a href="https://en.wikipedia.org/wiki/Platform_as_a_service">PaaS</a> is happily buzzing in the <a href="https://en.wikipedia.org/wiki/Cloud_computing">Cloud</a> and it seems to be hottest topic in the infrastructure  services today,  so I decided to test <a href="https://www.openshift.com">Openshift</a> \-  PaaS  offering  from Red Hat.  Couple of reasons make this platform interesting - firstly it's open source solution, so we can use it to build your own private solution, secondly on public service we  get 3 gears ( linux containers with predefined configuration) for free forever, so it's easy to experiment with this platform. As a sample project we will create very simple Python <a href="http://flask.pocoo.org/">Flask</a> web application with <a href="https://www.mongodb.org/">MongoDb</a>.<span id="more-1056"></span>


## Intial Setup


After creating account, few actions is required:


<ul>
<li>Install client tool <code>rhc</code> (it's Ruby based - so we need also ruby interpreter and gem package manager to be installed)</li>
<li>We also need git and python virtualenv  (our example is  for python 3)</li>
<li>register ssh key with  our account  (this can be done as part of nest step)</li>
<li>run<code> rhc setup</code></li>
</ul>


Now we are ready for our first application.


## Create And Deploy Application


We create application template using  sample application <a href="https://github.com/izderadicka/openshift-test">availabe here at github</a> :


```sh
rhc app create testpy python-3.3 --from-code https://github.com/izderadicka/openshift-test.git
#beware there is also app-create command, but it will not create local git repo by default
rhc cartridge add mongodb-2.4 -a testpy

```


Openshift provides base template for many common web application development platforms like python (with django, flask ...), php, node.js,  java (tomcat, jboss) etc.   Also for each web application we can add additional 'catridges', which are additional services like database, cron, etc.  In our case we add MongoDb cartridge.

First we need to create virtual environment so we can test application locally:


```sh
cd testpy
virtualenv -p python3 .
source bin/activate

```


Next we need to install required python libraries - they should be listed in file <a href="https://github.com/izderadicka/openshift-test/blob/master/requirements.txt">requirements.txt</a>. They are installed automatically during Openshift deployment,  however there is one issue there - it looks like by default  Openshift is installing packages from its own mirrors of python repositories and it could not find some packages for this application or right versions ( it also caused troubles in another project - where it installed older versions of django  and django-registration and application was not working then)-  <strong>enforcing official repository in requirements.txt</strong> helped:


```sh
--index-url https://pypi.python.org/simple/
```


Locally we can install dependencies with:


```sh
pip install -r requirements.txt
```


For Openshift deployment there are two other important files:
<a href="https://github.com/izderadicka/openshift-test/blob/master/setup.py">setup.py</a>, which is a standard python setup file, here we should edit metadata for our application and add any additional setup tasks (like creating database).  setup.py is also run automatically during deployment.  Here is for instance code to create postgresql database (if we choose postgresql instead of mongo) :


```python
from setuptools import setup
from setuptools import Command
import os.path

class InitDbCommand(Command):
    user_options = []

    def initialize_options(self):
        """Abstract method that is required to be overwritten"""

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""

    def run(self):
        from flaskapp import db
       
        res=db.engine.execute("""
SELECT EXISTS (
   SELECT 1
   FROM   information_schema.tables 
   WHERE  table_schema = 'public'
   AND    table_name = 'thought'
);
""")
        
        exists=list(res)[0][0]
        if exists:
            print('Table already exists, skipping creation')
        else:
            print('Will create table')
            db.create_all() 


setup(name='random_thoughts',
      version='0.1',
      description='Very simple flask app to test Openshift deployment',
      author='Ivan',
      author_email='ivan@zderadicka.eu',
      url='https://testpy-ivanovo.rhcloud.com/',
      cmdclass={'initdb': InitDbCommand},
     )

```


<a href="https://github.com/izderadicka/openshift-test/blob/master/wsgi.py">wsgi.py</a> \-  Openshift is using <a href="https://modwsgi.readthedocs.org/en/master/">mod_wsgi</a> to run python code,  by default it's looking for file wsgi.py in the root directory of our code.  For us it's just enough, to import  flask application, which is WSGI compatible:


```python
from flaskapp import app as application
```


Openshift also allows us to define custom scripts, which can run at different stages of deployment - so called <a href="https://docs.openshift.org/origin-m4/oo_user_guide.html#action-hooks">action hooks</a>. Action hooks can be added to directory .openshift/action\_hooks. In our case we  add <a href="https://github.com/izderadicka/openshift-test/blob/master/.openshift/action_hooks/deploy">deploy</a> script, which  enables fulltext in MongoDb configuration.

When our code is ready and works OK locally:


```sh
python flaskapp.py
```


we can deploy to Openshift easily with git:


```sh
git push origin master
# we may need to restart app first time due to mongodb config change to enable fulltext
rhc app restart testpy
```




##  Scalable Application


Openshift enables automatic <a href="https://developers.openshift.com/en/managing-scaling.html">scaling of applications</a> \-  when number of connections reaches certain threshold additional  gears with our web application are automatically  created and web traffic is load balanced between  them (Openshift is using HAProxy, installed in the first gear  - it's so called  Web Load Balancer cartridge).

When application is created it must be explicitly enabled for scaling.   Existing applications cannot be enabled for scaling after creation. So we first need to delete our exiting non-scalable application:


```sh
cd ..
rhc app delete testpy
rm -rf testpy
```


And recreate it as a scalable application ( with -s argument):


```sh
rhc app create testpy python-3.3  -s
cd testpy
```


We try something bit different to get code from github:


```sh
git rm -r wsgi.py setup.py .openshift
git commit -a -m 'clean'
# lets use differend branch for deployment
git checkout -b scaled
rhc app configure --deployment-branch scaled
git add remote github https://github.com/izderadicka/openshift-test.git
git pull github scaled
rhc push origin scaled
```


In this scenario we need shared MongoDb database,  we can use MongoLab from <a href="https://marketplace.openshift.com/home">Openshift Marketplace</a>.  Just order MongoLab Free service there and then add it to this application via marketplace UI.  Now our application looks like:


```sh
rhc app show testpy
testpy @ http://testpy-ivanovo.rhcloud.com/ (uuid: ...)
----------------------------------------------------------------------------
  Domain:     ivanovo
  Created:    7:49 AM
  Gears:      1 (defaults to small)
  Git URL:    ssh://...@testpy-ivanovo.rhcloud.com/~/git/testpy.git/
  SSH:        ...@testpy-ivanovo.rhcloud.com
  Deployment: auto (on git push)

  haproxy-1.4 (Web Load Balancer)
  -------------------------------
    Gears: Located with python-3.3

  python-3.3 (Python 3.3)
  -----------------------
    Scaling: x1 (minimum: 1, maximum: available) on small gears

  mongolab-mongolab-1.0 (MongoLab)
  --------------------------------
    From:  https://marketplace.openshift.com/api/custom/openshift/v1/accounts/...
    Gears: none (external service)
```


And we have environment variable to connect to MongoDb:


```sh
rhc env list
MONGOLAB_URI=mongodb://xxx:zzz.mongolab.com:37447/openshift_zzzz
```


So we just need to modify our application to use this connection URL:


```python
app.config['MONGO_URI'] = os.environ.get('MONGOLAB_URI', 'mongodb://localhost/test')
```


Scaling is configured by environment variable OPENSHIFT\_MAX\_SESSIONS\_PER\_GEAR (default is 16), which is maximum number of connections that HAProxy passes to one backend application.  According to the documentation, if number of total connections is sustained at 90% of capacity (max\_connections x num\_of\_gears) for some period, new gear is added (if free gears are available).  Web application is copied to the new gear, deployed, started and added as another backend to HAProxy load balancer.

For better demonstration of scaling we can decrease value of OPENSHIFT\_MAX\_SESSIONS\_PER\_GEAR:


```sh
rhc env set OPENSHIFT_MAX_SESSIONS_PER_GEAR=8
```


We can try how application scales -  we use Apache HTTP benchmark tool `ab` to put some load on our application:


```sh
ab -n 100000 -c 100 http://testpy-ivanovo.rhcloud.com/
```


After a while new gear is added, which we can see with command `rhc app show` (Scaling: x2).  It still takes quite some time (minutes), before new gear is ready and is added as new backend to HAProxy -   we can see HAProxy status at URL:  http://testpy-your-domain.rhcloud.com/haproxy-status.   Little bit later another gear (last remaining) is added.  Again it takes some time for it to be ready,  then if we again take a look  HAProxy status, we can see that the backend in the first gear is taken down (highlighted in brown) - this is an intended functionality -  according to documentation: '<em>'Once you scale to 3 gears, the web gear that is collocated with HAProxy is turned off, to allow HAProxy more resources to route traffic.</em>"

Results from ab may look like:


```sh
Server Software:        Apache/2.2.15
Server Hostname:        testpy-ivanovo.rhcloud.com
Server Port:            80

Document Path:          /
Document Length:        2866 bytes

Concurrency Level:      100
Time taken for tests:   1032.052 seconds
Complete requests:      100000
Failed requests:        0
Total transferred:      314133754 bytes
HTML transferred:       286600000 bytes
Requests per second:    96.89 [#/sec] (mean)
Time per request:       1032.052 [ms] (mean)
Time per request:       10.321 [ms] (mean, across all concurrent requests)
Transfer rate:          297.24 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:      105  142  65.6    131    3137
Processing:   127  889 504.0    774    3597
Waiting:      127  885 501.5    772    3596
Total:        249 1031 503.7    912    4016

Percentage of the requests served within a certain time (ms)
  50%    912
  66%   1049
  75%   1182
  80%   1300
  90%   1887
  95%   2104
  98%   2352
  99%   2540
 100%   4016 (longest request)

```


Actually when I was observing behaviour of the scalable application, above mentioned rule was not obviously demonstrated (I got around 100 connections to backend, OPENSHIFT\_MAX\_SESSIONS\_PER\_GEAR=16, but application was still scaled to 2 gears),  so maybe the scaling is bit more complex.

Finally after a while. when traffic is down, application returns back to 1 gear.  (Application restart will not reset scaling).

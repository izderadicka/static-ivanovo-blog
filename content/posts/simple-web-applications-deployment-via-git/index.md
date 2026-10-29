+++
title = "Simple Web Applications Deployment via Git"
path = "/simple-web-applications-deployment-via-git/"
date = "2015-09-15T15:48:55"
include_in_feeds = true
[extra]
wordpress_id = 1085
kind = "post"
node_key = "1085"
author = "admin"
source_url = "http://zderadicka.eu/simple-web-applications-deployment-via-git/"
source_guid = "http://zderadicka.eu/?p=1085"
source_date_gmt = "2015-09-15 14:48:55"
categories = ["Admin", "Programming"]
tags = ["devops", "git"]
+++
<a href="https://git-scm.com/">Git</a> is not only great version control tool,  but can be easily used for web application deployment to testing or production environmenst.  For more complex projects some continuous integration (CI), tools/services can be more appropriate  (like <a href="https://jenkins-ci.org/">Jenkins</a>), but for smaller project we can do just fine with Git , SSH and simple script installed as <a href="https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks">git hook</a>. Below is the scenario I'm using for one Python <a href="http://flask.pocoo.org/">Flask</a> web application.<span id="more-1085"></span>

Flask application is deployed on Debian server (running in VM), in <a href="https://uwsgi-docs.readthedocs.org/en/latest/">uwsgi</a> container behind <a href="http://nginx.org/">nginx</a> frontend (nginx is also serving static files).   We have two VMs -  one production and one testing. If necessary production instance can be easily scaled horizontally  by adding more uwsgi instances behind nginx frontend.


## Git Flow


We have two long running branches in Git:
<strong>devel</strong> \- for latest development version
<strong>master</strong> \- for production version

Developers work on feature branches, which they can run locally (with Flask embedded WSGI server),  when  features are ready, they are merged to `devel` branch and  `devel` branch is then pushed to test instance, where all new features are tested by users.  When we are fine with new functionality,  `devel` branch is merged to master branch and master branch is pushed to production instance.


## Server Setup


This is setup for testing server,  same is for production server,  only that branch for production is master.

1\. Install Git


```sh
apt-get update
apt-get install git
```


2\. Create bare repo


```sh
mkdir -p /var/repo/app.git
cd /var/repo/app.git
git init --bare
```


3\. Add remote


```sh
git remote add origin https://our.repo.server.com/repo/app.git
```


4\. Fetch branch and check it out


```sh
git fetch origin devel:devel
mkdir /opt/app
git --work-tree=/opt/app --git-dir=/var/repo/app.git checkout -f devel
```


Now we are ready to run the Flask application, just need an usual setup for Flask:


## Server setup - specific for Flask and Python


1\. Install base dependencies


```sh
apt-get install -y build-essential python python-dev python-pip uwsgi uwsgi-plugin-python nginx-full python-nose 
# optionally you might like to get newer uwsgi - compile it from source
```


2\. Create  uwsgi configuration for your application `/etc/uwsgi/apps-available/app.ini`


```sh
[uwsgi]
buffer-size=32768
socket = /tmp/app.uwsgi
plugin = python
chdir = /opt/app/src #whatever is your main Flask module
master=true
workers=1
threads=2
module = server # whatever is main module name
callable = app
enable-threads=true
```


And symlink it to `/etc/uwsgi/apps-enabled`.  Indeed for production configuration you might need other parameters, especially workers and threads.

3\. Create site configuration for nginx -`  /etc/nginx/sites-available/app-nginx `


```sh
server {
	listen   80 default_server; ## listen for ipv4; this line is default and implied
	listen   [::]:80 default_server ipv6only=on; ## listen for ipv6

	root /opt/app/src;
	index index.html index.htm;

	# Optionally server name
	# server_name some.server.com;

	location /static/ {   # assuming this is location of static files
		# static app files
		try_files $uri $uri/ 404;
	}

	location / {
		include uwsgi_params;
		uwsgi_pass unix:/tmp/app.uwsgi;
	}
}
```


Remove default nginx site and symlink this to`  /etc/nginx/sites-enabled `.

4\. Install necessary python dependencies for you application


```sh
# assuming that your project has all dependencies in requirements.txt file
# which is the best practice
pip install -r /opt/app/requirements.txt
```


5\. Restart servers


```sh
service uwsgi restart
service nginx restart
```




##  Server Setup - Git hook


Create following file in /var/repo/app.git/hooks/post-receive


```sh
#!/bin/bash
set -x -e

BRANCH=devel
WD=/opt/app

REFS=`cat`

if [[  $REFS =~ "refs/heads/"$BRANCH ]] ; then
	git --work-tree=$WD --git-dir=/var/repo/app.git checkout -f $BRANCH
	pip install -r $WD/requirements.txt
	cd $WD
	nosetests
	uwsgi --reload /var/run/uwsgi/app/app/pid
	service nginx  reload
	echo "Succesfully deployed $BRANCH branch"
else
	echo "This is not our branch: $REFS"
        exit 0
fi

```


This script checks if correct branch is pushed. Eventually it can be easily extended to deploy different branches to different locations.


## Client setup


Assuming you already have cloned devel branch to your computer and worked on it.

1\. Assure that your SSH public key is set on server


```sh
cat .ssh/id_dsa.pub | ssh root@test.server.com "cat >> .ssh/authorized_keys"
```


2\. Add remote repository to your cloned repo


```sh
git remote add test-server ssh://root@test.server.com/var/repo/app.git
```


3\. When you finished you can just push changes to test server


```sh
git push test-server devel
```


and they will be automatically deployed.

+++
title = "CI/CD Environment for A Smaller Project"
path = "/cicd-environment-for-a-smaller-project/"
date = "2017-12-16T12:31:02"
include_in_feeds = true
[extra]
wordpress_id = 1804
kind = "post"
node_key = "1804"
author = "admin"
source_url = "http://zderadicka.eu/cicd-environment-for-a-smaller-project/"
source_guid = "http://zderadicka.eu/?p=1804"
source_date_gmt = "2017-12-16 11:31:02"
categories = ["Admin", "Programming"]
tags = ["docker", "git"]
+++
Advantages of<strong> Continuous Integration (CI)</strong> and <strong>Continuous Delivery (CD)</strong> are obvious even for small projects with few contributors and are easily achievable with help of  free cloud tools - like for instance with mighty combo of <a href="https://github.com/">Github</a> plus <a href="https://travis-ci.org/">Travis</a>. But what if we want to achieve similarly convenient  environment inside of our private network, available only to our internal teams. Luckily open source is here again to help us with another great tool - <a href="https://about.gitlab.com/">GitLab</a> \-  GitLab  is a similar platform to GitHub, but the code is open source and we can easily install it in our environment. In this article I'll summarize my experiences and guidelines how to build convenient environment for a small project  with automatic testing and deployment.<span id="more-1804"></span>


## What we what to achieve


Our goals are:


<ul>
<li>Central code repository for our projects with friendly Web interface - similar to GitHub, but hosted by ourselves</li>
<li>Developers can use their existing credentials to log into this central repository</li>
<li>For projects we can setup CI, where for each push to central repository code is built and tested automatically</li>
<li>If build  and tests are successful web application  (we are talking about web applications) in deployed automatically for current branch in the  projects repository, so we can have numerous "feature" versions, where developers, QA and operations can test new features.</li>
<li>All this have to be rather simple and be able to run in couple of VMs - as our project is also rather small and we do not need complex architectures line <a href="https://kubernetes.io/">Kubernetes</a> for this project.</li>
</ul>




## Setup


<strong>1st VM (Debian, Ubuntu, CentOS ...)
</strong>


<ul>
<li>Size it appropriately 2 cores, 4GB mem 16GB free disk space should be enough for smaller projects.</li>
<li>Install here <a href="https://about.gitlab.com/installation/">Gitlab - Omnibus package</a></li>
<li>For authentication Gitlab can integrate with your corporate <a href="https://docs.gitlab.com/ee/administration/auth/ldap.html">LDAP</a> or through <a href="https://docs.gitlab.com/ee/integration/omniauth.html">OmniAuth</a> service  enable any popular SSO methods, including SAMLv2 (which I'm using)</li>
<li>Create project(s) and push code to them</li>
</ul>


<strong>2nd VM (Debian, Ubuntu, CentOS ...)</strong>


<ul>
<li>Size it appropriately - as you'll run there multiple containers you'll need more resources - say 4 cores, 16GB memory, 80 GB fee disk space (but it depends very much on your projects).</li>
<li>Install here<a href="https://docs.gitlab.com/runner/install/linux-repository.html"> Gitlab Runner</a>, <a href="https://docs.docker.com/engine/installation/">Docker CE</a>, eventually <a href="https://docs.docker.com/compose/install/">Docker Compose</a></li>
<li><a href="https://docs.gitlab.com/runner/register/">Register</a> two Gitlab <a href="https://docs.gitlab.com/runner/executors/">executors </a>(yes you can register several executors with one runner):
<ul>
<li>Docker executor - will be used for running builds and  tests -  be sure to give it  a tag -  docker</li>
<li>Shell executor - will run instances of our application in Docker container - again give it distinguishing tag - shell</li>
</ul>
</li>
<li>If you want to share easily links to running application instances install <a href="https://www.nginx.com/resources/admin-guide/installing-nginx-open-source/#prebuilt">nginx</a>, <a href="http://uwsgi-docs.readthedocs.io/en/latest/Install.html#installing-from-a-distribution-package">uwsgi</a> and <a href="https://github.com/izderadicka/dockerfp">this small application of mine</a></li>
<li>If you want to use local docker images for test tasks edit docker runner pull policy to <code>pull&#95;policy = "if-not-present"</code>  in file <code>/etc/gitlab-runner/config.toml</code> and restart runner</li>
</ul>




## How to use in a project


Here is the example how to use previous setup in a project ( my project is Python based so no special build tasks were needed, just to test and deploy).   In order to use CI/CD in Gitlab two preconditions are required:


<ol>
<li>Gitlab must have available runners that can be used for your project (in our case we registered runners for all projects)</li>
<li><code>.gitlab-ci.yml</code> script in root of your project directory</li>
</ol>


Here is sample script for our python project:


```yaml
image: my-base-image-for-testing

variables:
  MY_PREFIX: my_app

test:
  tags:
  - docker
  script:
  - pip install -r requirements.txt
  - pip install nose
  - nosetests

deploy_in_docker:
  stage: "deploy"
  tags:
    - shell
  script:
    - docker build -t ${MY_PREFIX}-${CI_BUILD_REF_NAME} --build-arg BRANCH_NAME=${CI_BUILD_REF_NAME} .
    - docker rm -f ${MY_PREFIX}-${CI_BUILD_REF_NAME} || true
    - docker run -d -P --name ${MY_PREFIX}-${CI_BUILD_REF_NAME} ${MY_PREFIX}-${CI_BUILD_REF_NAME}

```


 

Now with this setup  each push to central repository will run test and deploy tasks and if they are successful we will have an instance of our application running in container and out team can quickly check new features in that branch.

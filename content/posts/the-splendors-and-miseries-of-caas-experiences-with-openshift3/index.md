+++
title = "The Splendors and Miseries of CaaS - Experiences with Openshift3"
path = "/the-splendors-and-miseries-of-caas-experiences-with-openshift3/"
date = "2017-09-26T16:35:01"
include_in_feeds = true
[extra]
wordpress_id = 1702
kind = "post"
node_key = "1702"
author = "admin"
source_url = "http://zderadicka.eu/the-splendors-and-miseries-of-caas-experiences-with-openshift3/"
source_guid = "http://zderadicka.eu/?p=1702"
source_date_gmt = "2017-09-26 15:35:01"
[taxonomies]
category = ["Admin", "Tools"]
tag = ["docker", "kubernetes", "openshift3"]
+++
Container as a Service (CaaS) is increasingly popular cloud service (usually categorized under Platform as a Service family of cloud services). It can provide easy ways how to deploy web applications leveraging Linux container technologies usually most popular [Docker](https://www.docker.com/) containers.  Recent addition to this family is Openshift v3 from [RedHat](https://www.redhat.com).   Openshift is available as an open source  software ([Openshift Origin](https://www.openshift.org/)) or as a hosted service ([OpenShift Online](https://www.openshift.com/)).  I already used previous version of Openshift service (v2), as described in [my previous article](/openshift-second-thoughts/). In this article I'll share my recent experiences with Openshift v3 service (also called NextGen).<span id="more-1702"></span>


## Openshift NextGen Generally


Epithet NextGen was probably given to stress that new version of Openshift is radically different form the previous version. That's absolutely true, while previous version was basically proprietary solution, NextGen is based on more common technologies - Docker and [Kubernetes](https://kubernetes.io/) particularly,  so one can expect to enjoy all goodies of Docker ecosystem. Apart of basic support to run Docker containers, Openshift provides a set of PaaS services, based on pre-configured templates for most common web application technologies (Node.js, Python WSGI, Java  Servlets, PHP, ...) and Continuous Integration & Deployment ([Jenkins ](https://jenkins.io/)pipelines , or more simple Openshift "Source to Image(S2I)" build, which is described later).

Currently Openshift Online is offered in two variants Starter(free, but limited to 1GB memory and 2 virtual CPUs and forced hibernation of containers) and Pro. But you can easily test Openshift also locally on you computer with [Minishift ](https://github.com/minishift/minishift)or run Openshift locally in Docker container.  I found Minishift  particularly useful, when I played with it.

Basic unit of deployment in Openshift is a **pod**, which contains one or more Docker containers, which run together. Pod is then abstracted as a **sevice.** Service can run several pod instances load balanced (through [HAProxy](http://www.haproxy.org/)) - e.g. service enables horizontal scaling of pods.

There are many possibilities how to get Docker images to be run in pods:


<ul>
<li>Easiest way is to use existing image available in some registry ( e.g. Docker Hub).  Such image can be imported into Openshift as an **image-stream**, which is then deployed in a pod using defined **deployment** configuration (memory, cpus, volumes, environment variables, ...). But not every docker image will run in Openshift out of hand, there are some limitations of which I'll speak later.</li>
<li>Build an image and then deploy it. Openshift is quite flexible in ways how to create new image:
<ul>
<li>Dockerfile build -  use 'classic' docker build from Dockerfile</li>
<li>Source to Image (S2I) build - use special base image (builder) to create new image using  provided source code (from git repo)</li>
<li>Custom build - similar to Source to Image but even more flexible</li>
<li>Pipeline build -  building image using Jenkins pipeline</li>
</ul>
</li>
</ul>


Openshift can be managed either from web UI or console application `oc`. Both require a bit of understanding of Openshift architecture to get started with them.

Openshift has a [good documentation](https://docs.openshift.org/latest/welcome/index.html), so I refer reader to it for details.


## Deploying Apps from Docker Image


Disregarding all fanciness of PaaS finally it's about four basic things:
a) get my  application, which is running fine  locally in my development environment, to the Web quickly and painlessly
b) have it running there reliably and securely
c) scale easily as traffic grows (ideally automatically within some given limits)
d) have possibility to update it easily and instantly (possibly automatically)

I did have a couple of applications, that did run locally in Docker container, so I was quite exited that I can easily just push the existing Docker images to Openshift and they will happily run there forever.  Unfortunately ( or maybe fortunately because I did learn  quite few things) it was naive expectation and it was not so straightforward. Locally in my containers I did not care very much about security, so all apps run as root in local containers. But Openshift is much more careful, not only that you cannot run containers as root, but basically they are run [with arbitrary uid](https://docs.openshift.org/latest/creating_images/guidelines.html#openshift-origin-specific-guidelines).  So basically it meant for me to rewrite completely Docker files. And I needed quite a few iterations to finds where access rights can cause problem for arbitrary user. For these experiments Minishift was quite valuable as I can quickly push images to it (enable access to Minishift Docker registry as [described here](https://github.com/minishift/minishift/blob/master/docs/source/openshift/openshift-docker-registry.adoc)).

So my recommended flow for preparing images for Openshift is:



1. Create and image that runs as non-root user and test it in local Docker
1. Now run it  as arbitrary user (random uid and 0 as guid) - fix any access issues
1. Optionally test locally in Minishift
1. Deploy to Openshift



Most resistant to run as arbitrary user was [Postgresql](https://www.postgresql.org/) ( Openshift has it's own great image for Postgresql, but unfortunately it's missing [Postgis](http://postgis.net/), which one of my applications required, so no shortcut here either).

Concerning application updates Openshift deployment is updated automatically when new images is available (in image-stream, for remote repository it means triggering update of the image-stream) . Default is rolling deployment -   olds pods continue running until new pods are ready to take over, then old pods are deleted. If deployment fails it can be rolled out to previous working deployment.

Openshift also provides manual and automatic scaling - by adding pods to services either as result of admin actions or as results of reaching some load threshold.


## Deploying Apps from Source


Building and deploying apps from source works great for "standard" applications (like Python Flask)  with already available "Source to Image" builders or templates.  In this case new deployment means just linking git repository to appropriate builder (with Add to project in web UI or `oc new-app builder_image~repo_url`). In my case none of  my applications was "standard" so pre-built Docker images were easiest approach (although I thing I could make my python app to build and run with default S2I builder image with some more tweaking).

If default S2I builders are not enough (for instance we do not have one for Rust), we can relatively easily create our own, which I have done here as an exercise for my [toy Rust application](/in-rust-we-trust/) .

S2I build is running these steps (bit simplified):


<ol>
<li>Inject source code into builder image (download from repo, tar and then untar in the image)</li>
<li>With builder image run <code>assemble</code> command</li>
<li>Commit resulting container to new image</li>
<li>Run that new image with <code>run</code> command</li>
</ol>


So the S2I builder image is basically a Docker image with 2 shell scripts - assemble and run.

So here is an example of S2I builder image for toy Rust project:


```sh
# rust-builder
FROM scorpil/rust:nightly
MAINTAINER ivan.zderadicka@gmail.com

# TODO: Rename the builder environment variable to inform users about application you provide them
ENV BUILDER_VERSION 1.0

# Set labels used in OpenShift to describe the builder image
LABEL io.k8s.description="Rust Build for langgen" \
      io.k8s.display-name="Rust Builder 1.0" \
      io.openshift.expose-services="8080:http" \
      io.openshift.tags="builder,rust"


# Install required packages here:
RUN apt-get update &&\
    apt-get install -y wget &&\
    apt-get clean


# Copy the S2I scripts to /usr/local/bin, 
LABEL io.openshift.s2i.scripts-url=image:///usr/local/bin
COPY ./s2i/bin/ /usr/local/bin

# Drop the root user and make the content of /opt/app-root owned by user 1001

RUN adduser --uid 1001 appuser &&\
 mkdir /opt/app &&\
 chown -R 1001:1001 /opt/app

WORKDIR /opt/app

# This default user is created in the openshift/base-centos7 image
USER 1001

# Set the default port for applications built using this image
EXPOSE 8080

# Set the default CMD for the image
CMD ["/usr/local/bin/usage"]
```


with this `assemble` script:


```sh
#!/bin/bash -e
#
# S2I assemble script for the 'rust-builder' image.
# The 'assemble' script builds your application source so that it is ready to run.
#
# For more information refer to the documentation:
#	https://github.com/openshift/source-to-image/blob/master/docs/builder_image.md
#

# If the 'rust-builder' assemble script is executed with the '-h' flag, print the usage.
if [[ "$1" == "-h" ]]; then
	exec /usr/local/bin/usage
fi

# Restore artifacts from the previous build (if they exist).
#
if [ "$(ls /tmp/artifacts/ 2>/dev/null)" ]; then
  echo "---> Restoring build artifacts..."
  mv /tmp/artifacts/. ./
fi

echo "---> Installing application source..."
cp -Rf /tmp/src .
cd ./src

echo "---> Building application from source..."
# TODO: Add build steps for your application, eg npm install, bundle install, pip install, etc.
cargo build --release &&\
cargo test --release &&\
cd ..
cp src/target/release/serve .
cp -Rf src/web .
rm -rf src
wget https://sherlock-holm.es/stories/plain-text/cano.txt
```


and this `run` script:


```sh
#!/bin/bash -e
#
# S2I run script for the 'rust-builder' image.
# The run script executes the server that runs your application.
#
# For more information see the documentation:
#	https://github.com/openshift/source-to-image/blob/master/docs/builder_image.md
#

exec ./serve -a 0.0.0.0 -p 8080 ./cano.txt
```


Once we have builder image we can deploy application - locally in minishift we just need to push builder image to Minishift Docker repository (above is the link how to enable access to this repository), for hosted service we should push image to Docker Hub and then import it to Openshift with:


```sh
oc import-image your_namespace/rust-builder --confirm
```


and then create new application with oc command:


```sh
oc new-app rust-builder~https://github.com/izderadicka/langgen --name=langgen

```


This will create build configuration, run a build and deploy new application image created by the build.

Later if application source changes in git repo, we can either manually trigger rebuild or create a webhook in git repo that will start rebuild ( webhook will work only in hosted Openshift as public hook URL is needed).

If we change build image, again application will be automatically rebuild and re-deployed.


## Deploying Apps from Template


For complex applications a template can be created, that deploys application. Template is YAML or JSON files that defines objects to be deployed and parameters that should be supplied during deployment. Here is example of template for Django application with  Postgresql database:


```yaml
apiVersion: v1
kind: Template
labels:
  template: django-psql-persistent
message: |-
  The following service(s) have been created in your project: ${NAME}, ${DATABASE_SERVICE_NAME}.

  For more information about using this template, including OpenShift considerations, see https://github.com/openshift/django-ex/blob/master/README.md.
metadata:
  annotations:
    description: An example Django application with a PostgreSQL database. For more
      information about using this template, including OpenShift considerations, see
      https://github.com/openshift/django-ex/blob/master/README.md.
    iconClass: icon-python
    openshift.io/display-name: Django + PostgreSQL (Persistent)
    tags: quickstart,python,django
    template.openshift.io/documentation-url: https://github.com/openshift/django-ex
    template.openshift.io/long-description: This template defines resources needed
      to develop a Django based application, including a build configuration, application
      deployment configuration, and database deployment configuration.
    template.openshift.io/provider-display-name: Red Hat, Inc.
    template.openshift.io/support-url: https://access.redhat.com
  creationTimestamp: 2017-09-08T07:50:44Z
  name: django-psql-persistent
  namespace: openshift
  resourceVersion: "903"
  selfLink: /oapi/v1/namespaces/openshift/templates/django-psql-persistent
  uid: 6b1eaa09-946a-11e7-a11a-ee58d12b9e23
objects:
- apiVersion: v1
  kind: Secret
  metadata:
    name: ${NAME}
  stringData:
    database-password: ${DATABASE_PASSWORD}
    database-user: ${DATABASE_USER}
    django-secret-key: ${DJANGO_SECRET_KEY}
- apiVersion: v1
  kind: Service
  metadata:
    annotations:
      description: Exposes and load balances the application pods
      service.alpha.openshift.io/dependencies: '[{"name": "${DATABASE_SERVICE_NAME}", "kind": "Service"}]'
    name: ${NAME}
  spec:
    ports:
    - name: web
      port: 8080
      targetPort: 8080
    selector:
      name: ${NAME}
- apiVersion: v1
  kind: Route
  metadata:
    annotations:
      template.openshift.io/expose-uri: http://{.spec.host}{.spec.path}
    name: ${NAME}
  spec:
    host: ${APPLICATION_DOMAIN}
    to:
      kind: Service
      name: ${NAME}
- apiVersion: v1
  kind: ImageStream
  metadata:
    annotations:
      description: Keeps track of changes in the application image
    name: ${NAME}
- apiVersion: v1
  kind: BuildConfig
  metadata:
    annotations:
      description: Defines how to build the application
    name: ${NAME}
  spec:
    output:
      to:
        kind: ImageStreamTag
        name: ${NAME}:latest
    postCommit:
      script: ./manage.py test
    source:
      contextDir: ${CONTEXT_DIR}
      git:
        ref: ${SOURCE_REPOSITORY_REF}
        uri: ${SOURCE_REPOSITORY_URL}
      type: Git
    strategy:
      sourceStrategy:
        env:
        - name: PIP_INDEX_URL
          value: ${PIP_INDEX_URL}
        from:
          kind: ImageStreamTag
          name: python:3.5
          namespace: ${NAMESPACE}
      type: Source
    triggers:
    - type: ImageChange
    - type: ConfigChange
    - github:
        secret: ${GITHUB_WEBHOOK_SECRET}
      type: GitHub
- apiVersion: v1
  kind: DeploymentConfig
  metadata:
    annotations:
      description: Defines how to deploy the application server
    name: ${NAME}
  spec:
    replicas: 1
    selector:
      name: ${NAME}
    strategy:
      type: Recreate
    template:
      metadata:
        labels:
          name: ${NAME}
        name: ${NAME}
      spec:
        containers:
        - env:
          - name: DATABASE_SERVICE_NAME
            value: ${DATABASE_SERVICE_NAME}
          - name: DATABASE_ENGINE
            value: ${DATABASE_ENGINE}
          - name: DATABASE_NAME
            value: ${DATABASE_NAME}
          - name: DATABASE_USER
            valueFrom:
              secretKeyRef:
                key: database-user
                name: ${NAME}
          - name: DATABASE_PASSWORD
            valueFrom:
              secretKeyRef:
                key: database-password
                name: ${NAME}
          - name: APP_CONFIG
            value: ${APP_CONFIG}
          - name: DJANGO_SECRET_KEY
            valueFrom:
              secretKeyRef:
                key: django-secret-key
                name: ${NAME}
          image: ' '
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            timeoutSeconds: 3
          name: django-psql-persistent
          ports:
          - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 3
            timeoutSeconds: 3
          resources:
            limits:
              memory: ${MEMORY_LIMIT}
    triggers:
    - imageChangeParams:
        automatic: true
        containerNames:
        - django-psql-persistent
        from:
          kind: ImageStreamTag
          name: ${NAME}:latest
      type: ImageChange
    - type: ConfigChange
- apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    name: ${DATABASE_SERVICE_NAME}
  spec:
    accessModes:
    - ReadWriteOnce
    resources:
      requests:
        storage: ${VOLUME_CAPACITY}
- apiVersion: v1
  kind: Service
  metadata:
    annotations:
      description: Exposes the database server
    name: ${DATABASE_SERVICE_NAME}
  spec:
    ports:
    - name: postgresql
      port: 5432
      targetPort: 5432
    selector:
      name: ${DATABASE_SERVICE_NAME}
- apiVersion: v1
  kind: DeploymentConfig
  metadata:
    annotations:
      description: Defines how to deploy the database
    name: ${DATABASE_SERVICE_NAME}
  spec:
    replicas: 1
    selector:
      name: ${DATABASE_SERVICE_NAME}
    strategy:
      type: Recreate
    template:
      metadata:
        labels:
          name: ${DATABASE_SERVICE_NAME}
        name: ${DATABASE_SERVICE_NAME}
      spec:
        containers:
        - env:
          - name: POSTGRESQL_USER
            valueFrom:
              secretKeyRef:
                key: database-user
                name: ${NAME}
          - name: POSTGRESQL_PASSWORD
            valueFrom:
              secretKeyRef:
                key: database-password
                name: ${NAME}
          - name: POSTGRESQL_DATABASE
            value: ${DATABASE_NAME}
          image: ' '
          livenessProbe:
            initialDelaySeconds: 30
            tcpSocket:
              port: 5432
            timeoutSeconds: 1
          name: postgresql
          ports:
          - containerPort: 5432
          readinessProbe:
            exec:
              command:
              - /bin/sh
              - -i
              - -c
              - psql -h 127.0.0.1 -U ${POSTGRESQL_USER} -q -d ${POSTGRESQL_DATABASE}
                -c 'SELECT 1'
            initialDelaySeconds: 5
            timeoutSeconds: 1
          resources:
            limits:
              memory: ${MEMORY_POSTGRESQL_LIMIT}
          volumeMounts:
          - mountPath: /var/lib/pgsql/data
            name: ${DATABASE_SERVICE_NAME}-data
        volumes:
        - name: ${DATABASE_SERVICE_NAME}-data
          persistentVolumeClaim:
            claimName: ${DATABASE_SERVICE_NAME}
    triggers:
    - imageChangeParams:
        automatic: true
        containerNames:
        - postgresql
        from:
          kind: ImageStreamTag
          name: postgresql:9.5
          namespace: ${NAMESPACE}
      type: ImageChange
    - type: ConfigChange
parameters:
- description: The name assigned to all of the frontend objects defined in this template.
  displayName: Name
  name: NAME
  required: true
  value: django-psql-persistent
- description: The OpenShift Namespace where the ImageStream resides.
  displayName: Namespace
  name: NAMESPACE
  required: true
  value: openshift
- description: Maximum amount of memory the Django container can use.
  displayName: Memory Limit
  name: MEMORY_LIMIT
  required: true
  value: 512Mi
- description: Maximum amount of memory the PostgreSQL container can use.
  displayName: Memory Limit (PostgreSQL)
  name: MEMORY_POSTGRESQL_LIMIT
  required: true
  value: 512Mi
- description: Volume space available for data, e.g. 512Mi, 2Gi
  displayName: Volume Capacity
  name: VOLUME_CAPACITY
  required: true
  value: 1Gi
- description: The URL of the repository with your application source code.
  displayName: Git Repository URL
  name: SOURCE_REPOSITORY_URL
  required: true
  value: https://github.com/openshift/django-ex.git
- description: Set this to a branch name, tag or other ref of your repository if you
    are not using the default branch.
  displayName: Git Reference
  name: SOURCE_REPOSITORY_REF
- description: Set this to the relative path to your project if it is not in the root
    of your repository.
  displayName: Context Directory
  name: CONTEXT_DIR
- description: The exposed hostname that will route to the Django service, if left
    blank a value will be defaulted.
  displayName: Application Hostname
  name: APPLICATION_DOMAIN
- description: Github trigger secret.  A difficult to guess string encoded as part
    of the webhook URL.  Not encrypted.
  displayName: GitHub Webhook Secret
  from: '[a-zA-Z0-9]{40}'
  generate: expression
  name: GITHUB_WEBHOOK_SECRET
- displayName: Database Service Name
  name: DATABASE_SERVICE_NAME
  required: true
  value: postgresql
- description: 'Database engine: postgresql, mysql or sqlite (default).'
  displayName: Database Engine
  name: DATABASE_ENGINE
  required: true
  value: postgresql
- displayName: Database Name
  name: DATABASE_NAME
  required: true
  value: default
- displayName: Database Username
  name: DATABASE_USER
  required: true
  value: django
- displayName: Database User Password
  from: '[a-zA-Z0-9]{16}'
  generate: expression
  name: DATABASE_PASSWORD
- description: Relative path to Gunicorn configuration file (optional).
  displayName: Application Configuration File Path
  name: APP_CONFIG
- description: Set this to a long random string.
  displayName: Django Secret Key
  from: '[\w]{50}'
  generate: expression
  name: DJANGO_SECRET_KEY
- description: The custom PyPi index URL
  displayName: Custom PyPi Index URL
  name: PIP_INDEX_URL
```


 


## Conclusion


I only explored few basic possibilities of the Openshift platform,  it's promising, but not without surprises for unaware user. Platform is relatively complex and requires good understanding of  underlying concepts.  Naive reuse of  locally working Docker image is not enough, one must think ahead about security related limitations of the platform. Building from source works like charm for standard web application, but for more complex application individual approach (creating own builder images or templates or using Jenkins pipelines) is needed. This requires more efforts and deeper dive into the platform, but can fully automate deployment of any complex application.

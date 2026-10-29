+++
title = "Run and monitor tasks via WebSocket with ASEXOR"
path = "/run-and-monitor-tasks-via-websocket-with-asexor/"
date = "2017-03-28T11:21:50"
include_in_feeds = true
[extra]
wordpress_id = 1556
kind = "post"
node_key = "1556"
author = "admin"
source_url = "http://zderadicka.eu/run-and-monitor-tasks-via-websocket-with-asexor/"
source_guid = "http://zderadicka.eu/?p=1556"
source_date_gmt = "2017-03-28 10:21:50"
categories = ["Programming"]
tags = ["asyncio", "python", "Websocket"]
+++
Many modern web applications require more then just displaying data in the browser.  Data may need to be processed and transformed in various ways, which require intensive processing tasks on server side. Such processing is best done asynchronously outside of web application server, as such tasks can be relatively  long running. There are already many existing solutions for asynchronous task scheduling, some of them are quite sophisticated general frameworks like <a href="http://www.celeryproject.org/">Celery</a>, <a href="https://kafka.apache.org/">Kafka</a>, others are build in features of application servers ( like <a href="http://uwsgi-docs.readthedocs.io/en/latest/Mules.html">mules</a> and <a href="http://uwsgi-docs.readthedocs.io/en/latest/Spooler.html">spoolers</a> in <a href="http://uwsgi-docs.readthedocs.io/en/latest/index.html">uWSGI</a>).  But what if we need something simpler, which can work  directly with Javascript clients and is super simple to use in a project.  Meet <a href="https://github.com/izderadicka/asexor">asexor</a> \- ASynchronous EXecuOR,  a small project of mime.<span id="more-1556"></span>

Asexor was initially created as supporting project for Mybookshelf2,  but recently I refactored it and extended it to make it more general. Asexor is written in Python  leveraging heavily asyncio module. The key function of Asexor is to run tasks in separate processes and for this purpose it contains three main parts:

<strong>Tasks </strong>\- tasks are defined as simple Python wrapper around  program to be executed - just to validate and prepare command line arguments and parsing results returned by the program.  The is a special kind of task - MultiTask - that can generate and schedule other new tasks.

<strong>Scheduler </strong>\- schedules tasks using priority queue, executes them concurrently assuring  that number of tasks running  in parallel is limited ( to defined value). Scheduler also contains authentication (based on user tokens) and authorization functions, assuring that only authorized users can run tasks.

<strong>Protocols </strong>\- communication protocols to submit a task and receive feedback about task status (scheduled, started, finished, error ...). The primary focus in Asexor was to WebSocket protocol - so tasks can be easily controlled directly from web Javascript client. However additional protocols are available for more flexibility (HTTP long poll, raw socket TCP protocol, <a href="http://wamp-proto.org/">WAMP</a>), so tasks can be scheduled efficiently also from backend components.

Below is simple block schema of asexor:

<a href="/wp-content/uploads/Asexor.png"><img alt="Asexor" class="alignnone size-full wp-image-1585" decoding="async" height="384" loading="eager" sizes="(max-width: 1017px) 100vw, 1017px" src="/wp-content/uploads/Asexor.png" srcset="/wp-content/uploads/Asexor.png 1017w, /wp-content/uploads/Asexor-300x113.png 300w" width="1017"/></a>


## Asexor coding


So let's look now at code to give you an idea how easily a solution with asexor can be created (code is only fractional to demonstrate key features of asexor):

First we need to create some task(s),  for demonstration purposes let's create dummy task running linux `date` command:


```python
class DateTask(BaseSimpleTask):
    NAME = 'date'
    COMMAND = 'date'
    ARGS = [BoolArg('utc', '-u'), Arg(0)]
    MAX_TIME = 5

    async def validate_args(self, fmt, **kwargs):
        return await super().validate_args('+' + fmt, **kwargs)

    async def parse_result(self, data):
        logger.debug('Result for date task executed for user %s', self.user)
        return data.decode(self.output_encoding).strip()
```


As you can see task is simply calling  `date` program with two arguments - mandatory  argument format (which is prefixed with + in `validate_args` method as required by program) and optional argument -u  (for UTC time output).  The result of the task is just output of date  command as unicode string. So nothing special, but should give you an idea how to create asexor tasks - for some real application tasks could be more complex and use for instance conversion programs like ffmpeg, image-magic ... Notice that methods of the task class are defined as coroutines  (`  async def `).

Next we need to run asexor backend with this task (and any other tasks we would like to handle):


```python
load_tasks_from('simple_tasks')

Config.WS.AUTHENTICATION_PROCEDURE = dummy_authenticate_simple
protocols =[(WsAsexorBackend, {'port':8484, 'static_dir':client_dir})]

runner = Runner(protocols)
runner.run()
```


First we need to load supported tasks -   this can be done easily with function `load_tasks_from`, which loads all tasks from given module. Then we need to update asexor configuration ( with at least authentication function or coroutine, which takes a token sent by user and returns authenticated user id and optionally user roles).
We also need to define protocols, which asexor backend will support ( each protocol is a tuple of protocol class/factory and protocol parameters) and finally run  the instance of Runner class ( which runs asexor backend indefinitely until terminated by OS signal) .

Now the only thing that is left is some code in Javascript for web client, it's also fairly simple.  We can use <a href="https://github.com/izderadicka/asexor_js_client">asexor_js_client</a> library and with its help skeletal code for our client will look like below (using ES6 and jQuery):


```javascript
let client = new AsexorClient(window.location.host, USER_TOKEN);
client.connect()
  .then(()=> {
      console.log('Client ready');
      });

let task_updated = function (task_id, data) {
    console.log('Task update', task_id, data);
    // show task results or errors
}
client.subscribe(task_updated);

$('#run-task').on('click', function (evt) {
    let args=[$('#date-format').val()];
    let kwargs={utc:$('#date-utc').prop('checked')};
    client.exec('date', args, kwargs)
       .then(function(res) {
            console.log('Task id is '+ res);
            // show that task was submitted and remember task id
        })
})
```


Interacting with asexor from Javascript client consists of 3 main actions:


<ol>
<li>Connect to asexor - create <code>AsexorClient</code> class instance and connect</li>
<li>Submit task - using<code> client.exec</code> method, which takes task name and its positional and named parameters.   Method returns task id ( to be used to match further task updates) or throws an error, if anything went wrong.</li>
<li>Process updates for given task - via the function that must be registered with <code>client.subscribe</code></li>
</ol>


For bit more detailed demos of asexor look into<a href="https://github.com/izderadicka/asexor/tree/master/test"> asexor/test</a> directory for dummy\_\* files.


## Deployment


Asexor is basically a toolkit, so for deployment you should first build your own backend server module.  This module should run as a daemon process,  possibly  behind reverse proxy (<a href="https://www.nginx.com/">nginx</a>, <a href="http://www.haproxy.org/">haproxy</a>) that can also provide SSL offloading or load balancing in case that horizontal scaling of asexor is needed.

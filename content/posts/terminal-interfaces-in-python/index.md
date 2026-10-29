+++
title = "Terminal Interfaces in Python"
path = "/terminal-interfaces-in-python/"
date = "2015-08-21T09:15:50"
include_in_feeds = true
[extra]
wordpress_id = 1077
kind = "post"
node_key = "1077"
author = "admin"
source_url = "http://zderadicka.eu/terminal-interfaces-in-python/"
source_guid = "http://zderadicka.eu/?p=1077"
source_date_gmt = "2015-08-21 08:15:50"
categories = ["Programming"]
tags = ["python", "terminal"]
+++
Although there is a fair choice of GUI libraries for Python (good overview of Python GUI libraries is <a href="http://pythoncentral.io/introduction-python-gui-development/">here</a>), sometimes we need just a little bit more enhanced terminal interface, like in my recent project -  <a href="https://github.com/izderadicka/xmpp-tester">XMPP test client</a>  - where requirements were quite simple - just to split terminal screen into two areas -  main screen where messages are displayed (possibly asynchronously) and bottom line, where commands/messages can  be entered:

<a href="/wp-content/uploads/layout.png"><img alt="layout" class="alignnone size-full wp-image-1079" decoding="async" height="308" loading="eager" sizes="(max-width: 350px) 100vw, 350px" src="/wp-content/uploads/layout.png" srcset="/wp-content/uploads/layout.png 350w, /wp-content/uploads/layout-300x264.png 300w" width="350"/></a><span id="more-1077"></span>

In Python we have couple of options for terminal UI programming:


<ul>
<li><a href="https://docs.python.org/2/howto/curses.html">curses</a> - curses library is part of standard python distribution, it provides lower level access to terminal programming and terminal control sequences.  Many things are left to users - like resizing UI, event loops etc.</li>
<li><a href="http://urwid.org/">urwid</a> - is an excellent external library, which provides higher level interfaces for programming terminal UIs. It's a bit similar to above mentioned GUI kits, providing widgets, layout managers, event loop etc.  And many common tasks missing in curses are already included.</li>
</ul>


I decided to use urwid, because it looked easier to start with and many required functionalities  were already provided (like already mentioned resizing, which I think would be pretty tedious to re-implement in curses).  I've created simple <a href="https://github.com/izderadicka/xmpp-tester/blob/master/commander.py">commander</a> module, which provides interface similar to build-in <a href="https://docs.python.org/2/library/cmd.html">cmd.Cmd</a>, but with UI layout as shown above.   With this module we can create simple tools very easily:


```python
if __name__=='__main__':
    class TestCmd(Command):
        def do_echo(self, *args):
            '''echo - Just echos all arguments'''
            return ' '.join(args)
        def do_raise(self, *args):
            raise Exception('Some Error')
        
    c=Commander('Test', cmd_cb=TestCmd())
    
    #Test asynch output -  e.g. comming from different thread
    import time
    def run():
        while True:
            time.sleep(1)
            c.output('Tick', 'green')
    t=Thread(target=run)
    t.daemon=True
    t.start()
    
    #start main loop
    c.loop()
```


Which creates tool like this:

<a href="/wp-content/uploads/ui.png"><img alt="ui" class="alignnone size-full wp-image-1081" decoding="async" height="500" loading="lazy" sizes="(max-width: 742px) 100vw, 742px" src="/wp-content/uploads/ui.png" srcset="/wp-content/uploads/ui.png 742w, /wp-content/uploads/ui-300x202.png 300w" width="742"/></a>

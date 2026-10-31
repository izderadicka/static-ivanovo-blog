+++
title = "TheTool - Quick Actions for Desktop"
path = "/projects/python/thetool-quick-actions-for-desktop/"
date = "2012-11-13T13:53:52"
include_in_feeds = false
[extra]
wordpress_id = 344
kind = "page"
node_key = "344"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/thetool-quick-actions-for-desktop/"
source_guid = "http://zderadicka.eu/?page_id=344"
source_date_gmt = "2012-11-13 12:53:52"
menu_order = 0
parent = "/projects/python/"
+++
TheTool is a small tool enabling one to quickly do some tasks (tasks that relate to everyday usage) in Linux desktop. This tool is rebuild of <a href="http://old.zderadicka.eu/toshtool.php">older toshtool utility</a>, which I used for years, now completely rewritten with GTK3 framework and python (using GObject Introspection in python). The tool sits in the tray (or indicator panel - depends on desktop) and actions are just a click away.



<div class="tabset" data-tabs="" id="tabs_344_0">



<section class="tab-panel" id="tabs-344-0-0">



## Features



Recently it enables these tasks:


<ul>
<li>Immediately turn off display</li>
<li>Schedule computer suspend (shut down or hibernate) in given interval in very quick way. Also possibility to cancel planned suspend by just one click.</li>
<li>Suspend (shut down or hibernate)  when a player (with DBus  MPRIS MediaPlayer2 interface enabled) finishes playing</li>
<li>Automatic detection of network (based on name and subnet for wired connection) and then running some actions</li>
<li>Flexible system of actions - new actions can be easily written as plugins</li>
<li>Currently actions include:
<ul>
<li>setting and resetting proxy</li>
</ul>
</li>
<li>Any action can be set for quick access via tray icon menu</li>
</ul>


<strong>How actions works</strong>:


<ol>
<li>Define your own actions via <strong>Settings / Define Actions /Add</strong></li>
<li>To define an action select it's type and set right parameters</li>
<li>Define your known networks so you can assign actions to be  executed when you connect to the network (and that network is default interface for you computer - e.g. if you are connected both to wired Ethernet and Wi-Fi, wired connection is the default).  Use <strong>Settings / Configure Known Networks / Add</strong> to add network - easiest way is to use "<strong>Set from current networ</strong>k" button.</li>
<li>Assign actions to the network you are adding or assign actions to unknown network (<strong>Settings / Configure Unknown Network</strong>).</li>
<li>You can also assign actions to tray icon menu -<strong> Settings/ Configure Quick Actions</strong></li>
</ol>


Since I’m using my computer to listen music , audio books at evening I want to set some time-out, so computer suspends after I fall asleep. I missed some easy tool to enable this in few clicks, so I built this one. Another problem was connecting with notebook to different networks, some require proxy some not - automatic proxy configuration do not work well (a bit for browser, but not for other programs - shell, pidgin ...) so this was another function that I added to the tool.

I plan also to add more features:


<ul>
<li>More actions - change any setting via GSettings, call any DBUS method, launch programs, disable/enabe ports</li>
<li>One click disabling of screensaver ( not all video player have support for disabling screensaver)</li>
<li>Any other idea for quick task that need to be accessible very quickly</li>
</ul>


Will see what plans I can realize.



</section>




<section class="tab-panel" id="tabs-344-0-1">



## Screenshots




<div class="gallery" data-gallery="" id="metaslider_773"><figure><a href="/wp-content/uploads/tt-1-menu.png"><img alt="" decoding="async" height="600" loading="eager" src="/wp-content/uploads/tt-1-menu-297x223.png" width="800"/></a><figcaption>Menu</figcaption></figure><figure><a href="/wp-content/uploads/tt-2-settings.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/tt-2-settings-507x380.png" width="800"/></a><figcaption>Settings Dialog</figcaption></figure><figure><a href="/wp-content/uploads/tt-3-action.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/tt-3-action-645x484.png" width="800"/></a><figcaption>Action detail dialog</figcaption></figure><figure><a href="/wp-content/uploads/tt-4-net.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/tt-4-net-349x261.png" width="800"/></a><figcaption>Network detail dialog</figcaption></figure></div>




</section>




<section class="tab-panel" id="tabs-344-0-2">



## Download



TheTool is licensed under GPL v3 - <a href="http://www.gnu.org/licenses/gpl.html">http://www.gnu.org/licenses/gpl.html</a>
<a href="https://github.com/izderadicka/thetool">Source</a> available on GitHib.

<strong>To install:</strong>
<a href="https://github.com/izderadicka/thetool/archive/master.zip">Download</a> and extract source, go to extracted folder and run:

`sudo ./setup.py install`

and run `the-tool` command

If you want to observe it first or develop, you can run from source - but you must first
compile GSettings schema in thetool directory:

` glib-compile-schemas --strict thetool  `
`./the-tool`



</section>




<section class="tab-panel" id="tabs-344-0-3">



## Extend



TheTool can be easily extended with other actions -  new action can be written as a plugin in Python:


```python
class DummyAction(Action):
    PARAMS_DEFINITION=(('string1', True, basestring),
                       ('string2', False, str),
                       ('string3', True, unicode),
                       ('int1', True, int),
                       ('list1', True, list),
                       ('bool1', False, bool),
                       ('restricted1', True, str, ('opt1', 'opt2', 'opt3')),
                       ('restricted2', True, list, ['opt1', 'opt2', 'opt3']),
                       ('float1', True, float),
                       ('dict1', True, dict),
                       ('reg1', True, str, re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'))
                       )
    def execute(self):
        bool1=self.get_param('bool1')
        list1=self.get_param('list1')
        #Do something

register_type(DummyAction, 'My Dummy Action')
```


Plugin defines new class, that extends `Action` class . New class has to have `  PARAMS_DEFINITION ` class property - a list of  tuples with 3-4 items:

parameter name,   is parameter mandatory,   type (using python type),  optionally some restrictions on the parameter value (either list of  allowed values or regular expression that value must match)

Parameters are then available in GUI, when defining action there.

The new class the has to have method execute, which does the work. Within method you can get parameter values (already with correct type) by calling `self.get_param('parameter name')`.

The new class has to be registered by calling function`  register_type(NewActionClass, "Name of this type of action") `.

Both `Action` and`  register_type ` are already available in global context, when pluging is loaded and executed.

Plugins has to be put either in  `where_code_is_installed/thetool/actions` directory, or in `~/.config/thetool/actions` directory.



</section>




</div>

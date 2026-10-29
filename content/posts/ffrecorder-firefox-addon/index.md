+++
title = "ffrecorder - Firefox Addon"
path = "/projects/firefox-add-ons/ffrecorder-firefox-addon/"
date = "2013-01-08T11:29:11"
include_in_feeds = false
[extra]
wordpress_id = 480
kind = "page"
node_key = "480"
author = "admin"
source_url = "http://zderadicka.eu/projects/firefox-add-ons/ffrecorder-firefox-addon/"
source_guid = "http://zderadicka.eu/?page_id=480"
source_date_gmt = "2013-01-08 10:29:11"
menu_order = 0
parent = "/projects/firefox-add-ons/"
+++
The plugin will disable input change events (only DOM 0 level ), but it will record changes and you can replay them later in bulk operation. Assumes that input change initiates page reload. Generally very specific use-case - created to ease work with one specific application in mind, but addon is generic and should work with any form, where change in inputs resubmits form (or it part - but not with Ajax - main page needs to be posted)


### <strong>How to use it:</strong>




<ol>
<li>Install plugin (Firefox 17+ is recommended)</li>
<li>Go to page, where you would like to record changes.</li>
<li>Assure Add-on bar is visible (Ctrl+/ or in menu View/Toolsbars/Add-on Bar)</li>
<li>Click on the ffrecorder icon  <img alt="ffrecorder1.png" decoding="async" loading="eager" src="https://sun-center.cz.oracle.com/@api/deki/files/901/=ffrecorder1.png"/>  and choose "Start Recording" - the icon will become active <img alt="ffrecorder2.png" decoding="async" loading="lazy" src="https://sun-center.cz.oracle.com/@api/deki/files/902/=ffrecorder2.png"/> (for huge formss it can take a while so wait until icon is red, before starting to edit).</li>
<li>Update all necessary fields on page</li>
<li>Click again ffrecorder icon and choose "Apply changes"</li>
<li>The dialogue will appear with number of changes and progress with their upload</li>
<li>You can leave the browser page,  but do not close that tab!</li>
<li>You can check progress of changes application later- you can display again progress dialogue by click the ffrecorder icon and choosing "Application Progress". This dialog will hide when you leave the page or click outside of it.</li>
<li>When all changes are applied ffrecorded icon will again turn to grey. Changes were all applied.</li>
<li>Double check that changes were applied as expected.</li>
</ol>




### <strong>Troubleshooting:</strong>


In case of any troubles check first error console - Tools/ Web Developer / Error Console. Scroll down and see if there are any error messaged relates to ffrecorder.

Application of changes got stuck - e.g. you cannot see any progress and also page did not reload for significant time.   Try Cancel Recording, remember what changes we already applied and start again with unappliead changes.

 

Dual licensed GPL v3 or MPL 2.0

<a href="https://github.com/izderadicka/ffrecorder">Source and XPI</a> is available on Github.

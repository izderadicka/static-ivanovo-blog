+++
title = "Timezones and DST in Oracle APEX"
path = "/timezones-and-dst-in-oracle-apex/"
date = "2013-01-11T14:18:18"
include_in_feeds = true
[extra]
wordpress_id = 485
kind = "post"
node_key = "485"
author = "admin"
source_url = "http://zderadicka.eu/timezones-and-dst-in-oracle-apex/"
source_guid = "http://zderadicka.eu/?p=485"
source_date_gmt = "2013-01-11 13:18:18"
[taxonomies]
category = ["Programming"]
tag = ["Apex", "Javascript", "PL/SQL"]
+++
Almost all APEX applications I've been working with recently are used across multiple timezones, where many timezones uses DST (Daylight Saving Time) - that is basically almost all Europe and North America. The natural requirement is that users can see date+time information in their timezone time, reflecting if DST is active or not. Timezones and time conversions are always bit of mess and APEX is not supporting this completely out of box, but with small effort we can make our applications really global.<span id="more-485"></span>


## Prerequisites


Oracle 11 has extensive support for working with dates in multiple timezones, the key trick is to use data type TIMESTAMP WITH LOCAL TIMEZONE for all columns that contain date+time that needs to be globalized.  This data type  always storea timestamp with a timezone of the server (I strongly recommend to use GMT as server timezone), but when send to clients,  timestamps are always converted to a timezone of client db session. So all problem now reduces to provide correct timezone setting for users db session.

APEX leverages  this database functionality and you can set APEX session timezone (via APEX\_UTILS.SET\_SESSION\_TIME\_ZONE Procedure) that is then used for all db sessions within that APEX session.    Also for APEX application you can set "Automatic Time Zone" in the Application Properties / Globalization, however this is not working correctly for DST timezones (as of version 4.2)- see below.


## Why APEX  "Automatic Time Zone" is not working properly


If "Automatic Time Zone" is set to yes, APEX tries to set APEX session timezone according to user browser setting.  When entering an application APEX automatically redirects to a special page, which has following Javascript:


```javascript
function detectTimeZone(){
var lGmtHours = -(new Date()).getTimezoneOffset();
var lHours = parseInt(lGmtHours/60);
var lMinutes = lGmtHours%60;
window.location.href="f?p=301:1:0:&tz="+lHours+":"+(lMinutes<10?"0"+lMinutes:lMinutes);
}
```


As you can see this script  redirecta back to original page and it adds tz query parameter to the URL,   tz parameter is set to current hours offset  of local time from GMT and after redirection is used to set APEX session timezone to this offset.  And this is the source of problems for timezones with DST, because this offset is different in summer (when DST is on) and in winter.   So if you are using Automatic Time Zone enabled application in winter for instance,   all displayed timestamps from summer will be shifted by one hour from an expected time.


## Proper DST handling


In order to handle DST timezones properly we have to set them in APEX session by their name (Europe/Berlin), which  assures that timestamp is converted with DST  in mind.   To help us detect user timezone name we can use [jsTimezoneDetect library](https://bitbucket.org/pellepim/jstimezonedetect).

Here are steps how to assure proper automatic detection of user timezone name, that will work with DST zones (assuming that application is using login and is based on default 101 login page):


<ol>
<li>Disable Automatic Time Zone in the Application Properties / Globalization</li>
<li>Upload this JS script  https://bitbucket.org/pellepim/jstimezonedetect/downloads/jstz-1.0.4.min.js
to Shared Components /Static files - file should not be attached to any application</li>
<li>Modify 101 Login page :
<ol>
<li>Add  hidden page item - P101_TZ to Login region,   set Protect Value to No (important!)</li>
<li>Add this code to Login Region Header
<pre class="code-highlight" data-language="html"><code><span class="code-line"><span class="p">&lt;</span><span class="nt">script</span> <span class="na">type</span><span class="o">=</span><span class="s">&quot;text/javascript&quot;</span> <span class="na">src</span><span class="o">=</span><span class="s">&quot;#WORKSPACE_IMAGES#jstz-1.0.4.min.js&quot;</span><span class="p">&gt;&lt;/</span><span class="nt">script</span><span class="p">&gt;</span></span>&#10;<span class="code-line"><span class="p">&lt;</span><span class="nt">script</span> <span class="na">type</span><span class="o">=</span><span class="s">&quot;text/javascript&quot;</span><span class="p">&gt;</span></span>&#10;<span class="code-line"><span class="nx">$</span><span class="p">(</span><span class="kd">function</span><span class="w"> </span><span class="p">()</span><span class="w"> </span><span class="p">&#123;</span></span>&#10;<span class="code-line"><span class="kd">var</span><span class="w"> </span><span class="nx">tz</span><span class="w"> </span><span class="o">=</span><span class="w"> </span><span class="nx">jstz</span><span class="p">.</span><span class="nx">determine</span><span class="p">();</span><span class="w"> </span><span class="c1">// Determines the time zone of the browser client</span></span>&#10;<span class="code-line"><span class="nx">$s</span><span class="p">(</span><span class="s2">&quot;P101_TZ&quot;</span><span class="p">,</span><span class="w">  </span><span class="nx">tz</span><span class="p">.</span><span class="nx">name</span><span class="p">());</span></span>&#10;<span class="code-line"><span class="p">});</span></span>&#10;<span class="code-line"><span class="p">&lt;/</span><span class="nt">script</span><span class="p">&gt;</span></span></code></pre>
 </li>
<li>Create page a Page Process just after Login process, named "Set TZ", type PL/SQL anonymous block, with this code
<pre class="code-highlight" data-language="sh"><code><span class="code-line">APEX_UTIL.SET_SESSION_TIME_ZONE<span class="o">(</span>:P101_TZ<span class="o">)</span><span class="p">;</span></span></code></pre>
 </li>
</ol>
</li>
</ol>


The only small issue with this approach is that JS library chooses one  default name for each timezone, which may be different from ideal choice for user ( because there is no geo-location and one timezone can have many names according to major cities within that timezone). So for instance for Europe it always chooses Europe/Berlin for CET timezone, even if user might prefer Europe/Paris.

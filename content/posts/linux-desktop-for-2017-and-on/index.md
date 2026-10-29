+++
title = "Linux Desktop for 2017 and on"
path = "/linux-desktop-for-2017-and-on/"
date = "2017-10-08T10:12:14"
include_in_feeds = true
[extra]
wordpress_id = 1735
kind = "post"
node_key = "1735"
author = "admin"
source_url = "http://zderadicka.eu/linux-desktop-for-2017-and-on/"
source_guid = "http://zderadicka.eu/?p=1735"
source_date_gmt = "2017-10-08 09:12:14"
categories = ["Admin"]
tags = ["gnome 3", "linux"]
+++
<a href="/wp-content/uploads/Screenshot-from-2017-10-08-08-38-43.png"><img alt="Screenshot from 2017-10-08 08-38-43" class="alignleft wp-image-1743 size-thumbnail" decoding="async" height="150" loading="eager" src="/wp-content/uploads/Screenshot-from-2017-10-08-08-38-43-150x150.png" width="150"/></a>As Canonical has <a href="https://insights.ubuntu.com/2017/04/05/growing-ubuntu-for-cloud-and-iot-rather-than-phone-and-convergence/">announced</a> the end of Unity desktop I thought it's time to look again around at Linux desktops. In past years I have been using mainly Gnome 2 (or <a href="https://mate-desktop.org/">Mate</a> recently), <a href="https://xfce.org/">XFCE</a>, <a href="http://developer.linuxmint.com/projects/cinnamon-projects.html">Cinnamon</a> and <a href="https://wiki.ubuntu.com/Unity">Unity</a> (yes I did and experience was after all rather positive). I've tried <a href="https://www.gnome.org/">Gnome 3</a> few years ago, but really never gave it longer try and never really find attraction for <a href="https://www.kde.org/">KDE</a>. So in this article I'll look a bit at those desktops again and especially at the recent Gnome Shell and it's customization to my needs (which is indeed based on very individual preferences).<span id="more-1735"></span>

For computers with limited resources I'm using XFCE for years and have to say I'm quite happy with it. It's has quite good look, good usability and it's wary about resources. Definitely XFCE will remain one of my choices for future.

But if we have more resources we can get more fancy and use more demanding desktop. I've used Unity recently with some reservations, but generally worked well. What I particularly liked were  search in the Dash (but of course with disabled stupid commercial and media searches) and the Launcher panel on left hand side. I learned to prefer keyboard for navigation - so effective search is a must, but still liked the Launcher panel if I get lost.

So I was looking for desktop with good search capabilities and possibility to have an intelligent 'dock' panel on left.

I know that Mate and Cinnamon are sticking by default to 'Windowish' layout with main panel at bottom and 'Start here' button with some type of main menu. It's fine however I think we can move behind that paradigm after all that years, it not mandate neither so brilliant, it's just a habit . I tested quickly recent Mint with Cinnamon and it did not impress me especially - the search in main menu was rather poor (maybe it can be improved).

I also tried <a href="https://elementary.io/">ElementaryOS</a> with default Pantheon desktop. It looks really good and I think it's excellent choice for a basic user (this might be distro I can install to my wife). I was bit concerned by lack of further customizations and too much 'Macish' look.

I tried quickly KDE Plasma too - surely it's advanced desktop - looks good and is very much customizable, however since I never used KDE systematically, it feels bit strange - I have to admit I'm rather used to Gnome or it's derivatives.

So final try went to Gnome 3 (or have to say rather Gnome Shell), because I somehow expected I'll finally end up there. The key difference comparing to years ago experience  is now really tons of extensions for every aspect of the desktop, so Gnome Shell can be now customized to very different look and functionality then it has out of box. Search functionality is quite good and I read that it should be even improved in 3.26.  Concerning look and feel I've done following customizations:


<ul>
<li>Changed GTK3 and shell themes to <a href="https://github.com/adapta-project/adapta-gtk-theme">Adapta</a>  and icons to Moka icons (providing nice clean modern look):
Install:
<pre class="code-highlight" data-language="sh"><code><span class="code-line">sudo<span class="w"> </span>apt-add-repository<span class="w"> </span>ppa:tista/adapta</span>&#10;<span class="code-line">sudo<span class="w"> </span>apt-get<span class="w"> </span>update</span>&#10;<span class="code-line">sudo<span class="w"> </span>apt-get<span class="w"> </span>install<span class="w"> </span>adapta-gtk-theme<span class="w"> </span>adapta-backgrounds<span class="w"> </span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line">sudo<span class="w"> </span>add-apt-repository<span class="w"> </span>ppa:moka/daily</span>&#10;<span class="code-line">sudo<span class="w"> </span>apt-get<span class="w"> </span>update</span>&#10;<span class="code-line">sudo<span class="w"> </span>apt-get<span class="w"> </span>install<span class="w"> </span>moka-icon-theme<span class="w"> </span>faba-icon-theme</span>&#10;</code></pre>
Then set appropriate themes in Gnome Tweak Tool (need to enable User Themes extension before changing shell theme).</li>
<li>Change desktop fonts to Noto Sans Regular as recommended  by Adapta theme.</li>
<li>In Gnome Tweak tool disable paste by middle mouse button (as I'm using it to scroll) and change acceleration profile to Adaptive</li>
<li>Make cursor bigger - in dconf editor go to /org/gnome/desktop/interface/cursor-size  increase to 32</li>
<li>Install and enable following <a href="https://extensions.gnome.org/">gnome extensions</a>:
<ul>
<li>Dash to Dock - excellent extension, displays dash panel in regular screen (much like Unity launcher, but even more customizable).</li>
<li>Notifications Alert -  blinks date in top panel, if there are any new notifications. I set blinking period to 0, so it'll just turn date red, which is enough for me.</li>
<li>Places status indicator - quick navigation to key places/directories from top panel.</li>
<li>TopIcons Plus - puts legacy tray icons onto top panel (otherwise they are in a tray in bottom left corner, which if terrible).</li>
<li>Workspace Indicator - shows current workspace in top panel</li>
<li>Refresh wifi connections - adds refresh button to wifi network selection</li>
</ul>
</li>
<li>And of course setup favorite background</li>
</ul>


With these few customizations desktop looks like this:
<a href="/wp-content/uploads/Screenshot-from-2017-10-08-08-38-43.png"><img alt="Screenshot from 2017-10-08 08-38-43" class="alignnone size-large wp-image-1743" decoding="async" height="553" loading="lazy" sizes="(max-width: 884px) 100vw, 884px" src="/wp-content/uploads/Screenshot-from-2017-10-08-08-38-43-1024x640.png" srcset="/wp-content/uploads/Screenshot-from-2017-10-08-08-38-43-1024x640.png 1024w, /wp-content/uploads/Screenshot-from-2017-10-08-08-38-43-300x188.png 300w, /wp-content/uploads/Screenshot-from-2017-10-08-08-38-43.png 1440w" width="884"/></a>

and provides nice looking and hopefully effective working environment.

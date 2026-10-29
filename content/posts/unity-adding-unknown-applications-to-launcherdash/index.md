+++
title = "Unity - adding unknown applications to Launcher/Dash"
path = "/unity-adding-unknown-applications-to-launcherdash/"
date = "2014-08-04T15:32:52"
include_in_feeds = true
[extra]
wordpress_id = 831
kind = "post"
node_key = "831"
author = "admin"
source_url = "http://zderadicka.eu/unity-adding-unknown-applications-to-launcherdash/"
source_guid = "http://zderadicka.eu/?p=831"
source_date_gmt = "2014-08-04 14:32:52"
categories = ["Admin"]
tags = ["linux", "ubuntu", "unity"]
+++
It's described in numerous posts how to add new application to Unity so it's searchable in Dash.   Unity works with .<a href="http://standards.freedesktop.org/desktop-entry-spec/latest/">desktop</a> files, which define how applications should be launched from Unity - these files are located in `/usr/share/applications` (system wide definitions) or `~/.local/share/applications` (user specifics application). So if you add well formated .desktop file to any of these locations Unity will be aware of it (may need to restart unity).

Recently I found one more interesting behavior of Unity - if you start unknown application from terminal it will appear in Launcher (in 'Running applications' section), Unity even makes some effort to find correct icon for it.  Now you can lock it to Launcher (right click and chose 'Lock to Launcher' from menu).   On background Unity creates new .desktop entry for this program in `~/.local/share/applications`, so it can stay locked to Launcher in future.   This new .desktop file contains title of the application from window title (in which application is running) executable path and parameters are taken from process properties, even icon path is stored if Unity was able to find one.  And when you unlock application from launcher, .desktop file will still remain in users applications - so you can search it in Dash.   So this approach can make adding new unknown application easier - just run, then lock and unlock from Launcher and you'll have new entry in `~/.local/share/application`. You can then edit it a bit manually to make it perfect and this is it.

+++
title = "AppIndicator3 - how to use custom icons"
path = "/appindicator3-how-to-use-custom-icons/"
date = "2013-06-03T11:20:02"
include_in_feeds = true
[extra]
wordpress_id = 555
kind = "post"
node_key = "555"
author = "admin"
source_url = "http://zderadicka.eu/appindicator3-how-to-use-custom-icons/"
source_guid = "http://zderadicka.eu/?p=555"
source_date_gmt = "2013-06-03 10:20:02"
[taxonomies]
category = ["Programming"]
tag = ["gtk3", "python"]
+++
Recently I've updated <a href="/projects/python/thetool-quick-actions-for-desktop/" title="TheTool – Quick Actions for Desktop">TheTool</a> to support also AppIndicator3 interface so it can show icon in Unity panel.   Although the [documentation](http://developer.ubuntu.com/api/ubuntu-12.04/python/AppIndicator3-0.1.html) is not saying it, you can<span style="text-decoration: underline;"> use absolute path to PNG image as icon-name</span> ( apart of stock icon name).   I was trying to add application specific stock icons, but is somehow did not work well (only possibility is to use `  xdg-icon-resource install --novendor --size 32  picture.png icon-name `,   but python code for creating application specific icons with Gtk.IconFactory was not working for me - see [this post](http://stackoverflow.com/questions/16881050/creating-application-specific-stock-icons-in-gtk3) on stackoverflow). <span id="more-555"></span>And here is some snippet how to use AppIndicator3:


```python
try:
    from gi.repository import AppIndicator3  # @UnresolvedImport
    HAS_INDICATOR=True
except:
    HAS_INDICATOR=False

class Indicator(object):    
    def __init__(self, menu):
        self.ind = AppIndicator3.Indicator.new (
                          "thetool",
                          "",
                          AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status (AppIndicator3.IndicatorStatus.ACTIVE)
        self.ind.set_icon(os.path.join(_curr_dir, 'pics', 'tools.png'))
        self.ind.set_attention_icon (os.path.join(_curr_dir, 'pics', 'tools-active.png'))
        self.ind.set_menu(menu)

    def set_labelt(self, txt):
        self.ind.set_label(txt, txt)

    def set_attention(self, attention):
        if attention:
            self.ind.set_status (AppIndicator3.IndicatorStatus.ATTENTION)
        else:
            self.ind.set_status (AppIndicator3.IndicatorStatus.ACTIVE)
```


 

For platform that do not have AppIndicator3, you can still alternatively use Gtk.StatusIcon, which provides similar possibilities - [here](https://github.com/izderadicka/thetool/blob/master/thetool/tray.py) in GitHub is example - a factory function creates duck-typed wrapper - which uses either AppIndicator3 or Gtk.StatusIcon - according to what is available.

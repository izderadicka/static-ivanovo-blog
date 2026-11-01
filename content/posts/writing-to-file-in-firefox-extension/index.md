+++
title = "Writing to file in Firefox Extension"
path = "/writing-to-file-in-firefox-extension/"
date = "2012-12-20T14:17:24"
include_in_feeds = true
[extra]
wordpress_id = 395
kind = "post"
node_key = "395"
author = "admin"
source_url = "http://zderadicka.eu/writing-to-file-in-firefox-extension/"
source_guid = "http://zderadicka.eu/?p=395"
source_date_gmt = "2012-12-20 13:17:24"
[taxonomies]
category = ["Programming"]
tag = ["Firefox Add-on", "Firefox Extension", "Javascript"]
+++
Mozilla has provided nice high level API in its[ Add-On SDK](https://addons.mozilla.org/en-us/developers/builder), where one can relatively easily write an extension, without need for any special knowledge about internals of Firefox - the general knowledge of Javascript, HTML and CSS plus very nice and detailed documentation of the SDK are basically enough.

However there are some functionalities, that are not available in SDK and then more effort is needed and  XPCOM components have to be used via their JS interfaces.  This requires bit more  research, so I'd like to share one useful snippet of code  - how to save string to file, which user has chosen via standard file picker dialogue:<span id="more-395"></span>

 


```javascript
        var {Cc, Ci} = require("chrome");
        var file = require("file"); 
        var picker = Cc["@mozilla.org/filepicker;1"].createInstance(Ci.nsIFilePicker);
	var win = require("window/utils").getMostRecentBrowserWindow();

	picker.init(win, "Save as", Ci.nsIFilePicker.modeSave);
	picker.appendFilter("Text (CSV)", "*.csv");
	var rv = picker.show();
	if (rv == Ci.nsIFilePicker.returnOK || rv == Cif.nsIFilePicker.returnReplace) {
		var path = picker.file.path;
		console.debug("Saving to file", path);
		var writer = file.open(path, 'w');
		writer.write(data);
		writer.close();

	}
```

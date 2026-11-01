+++
title = "ffscrap - Firefox Add-on"
path = "/projects/firefox-add-ons/ffscrap-firefox-addon/"
date = "2012-12-31T09:57:42"
include_in_feeds = false
[extra]
wordpress_id = 399
kind = "page"
node_key = "399"
author = "admin"
source_url = "http://zderadicka.eu/projects/firefox-add-ons/ffscrap-firefox-addon/"
source_guid = "http://zderadicka.eu/?page_id=399"
source_date_gmt = "2012-12-31 08:57:42"
menu_order = 0
parent = "/projects/firefox-add-ons/"
+++
ffscrap is a Firefox addon that enables to extract  data (in CSV format) easily from any page and save them or paste them  to a spreadsheet.



<div class="tabset" data-tabs="" id="tabs_399_0">



<section class="tab-panel" id="tabs-399-0-0">



## Features



Many times in past I needed to get data from a HTML page into a spreadsheet -  sometimes it worked  fine  just by cut&paste, but many times HTML code was more complex and it did not work very well.   So I decided to write a Firefox extension that will help to extract data ( the term 'scrap' is also used in this context) into some useful form that can be easily used in a spreadsheet or in other applications (CSV format seemed to be best choice due to its simplicity and wide support).  I used [Mozilla Add-on SDK](https://addons.mozilla.org/en-us/developers/builder), which enables to write extensions with high level API.

**Features of the extension:**



- Define data on the page using easy to understand JSON script/recipe.
- When scraping JSON script is defined you can extract data just by one click.
- Maintains scraping scripts for pages.
- Share scraping scripts easily within your community (scripts can be automatically downloaded from given URL).



You can test extension and its scraping function easily on this page - <a href="http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp">http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.jsp</a>

Assure that Addon Bar is visible (Ctrl+/) and right-click on ffscrap icon  <img alt="" class="size-full wp-image-403 alignnone" decoding="async" height="22" loading="eager" src="/wp-content/uploads/inactive_icon.png" title="inactive_icon" width="24"/>  on the  bar (in bottom right of the screen).  The "Define Scrapping Script" dialogue  pops up.

Input "CNB Exchage Rate" as Name of the script and paste this to Scraping Specification replacing text there:


```javascript
{"selector":"table.kurzy_tisk",
"rowsRange":[1,0,1],
"row":{"selector":"tr",
"fields":[
{"selector":"td:eq(0)","name":"country"},
{"selector":"td:eq(1)","name":"currency"},
{"selector":"td:eq(2)","name":"quatity","type":"int"},
{"selector":"td:eq(3)","name":"code"},
{"selector":"td:eq(4)","name":"rate","preprocess":"numberNormalizeCZ","type":"float"}
]}}
```


Then click "Apply to This Page" button.   "Scraping Result" dialogue will appear and you can copy CSV data to clipboard or save it to file.



</section>




<section class="tab-panel" id="tabs-399-0-1">



## Usage



In order to use this addon you have to:



1. Install it in Firefox browser ( ver. 17+) - see Download tab.
1. Define scraping script (right-click ffscrap icon - more details below)
1. Extract data (left-click ffscrap icon) and save them or copy them to clipboard
1. Optionally you can share your scraping scripts within your community





## Defining Scraping Script


On any page you can define your own scraping script - just right-click ffscrap icon  <img alt="" decoding="async" height="22" loading="lazy" src="/wp-content/uploads/inactive_icon.png" title="inactive_icon" width="24"/>  on the Add-on  Bar (to make this toolbar visible use View/ToolBars/Add-on Bar or Ctrl+/ ).  This will open a pop up dialogue "Define Scraping Script" , where you can define new script - for the initial definition I recommend to move this dialogue to a new tab by pressing "To Tab" button (dialogue will close when you click outside of it or window looses focus - this is a feature of FF add-on panels).

In "Define Scrapping Script"  dialogue enter:

**Name** \- arbitrary name for your script, just be aware that this name should be unique - if you use name of an existing script, it will be overwritten by this new definition. Name cannot be changed once script is saved for first time.

**URL Pattern** \-   URL or partial URL for which this script should be applied.  Just leave enough of URL to identify this page, but leave out dynamic components which vary with different page views - like query strings etc.  Star (\*) can be user as "wild character" to match group of any characters.

**Scraping Specification** \-   JSON script defining  data scraping.   There is a skeleton/sample script shown initially so you can start with it and modify it.

When done with the script click "Apply to Page"  to test the script (it'll be also saved) or "Save Only" just to save it for later.

When some script is defined for a page ffscrap icon on Add-on Bar will change to <img alt="" class="alignnone size-full wp-image-407" decoding="async" height="23" loading="lazy" src="/wp-content/uploads/icon_active.png" title="icon_active" width="24"/>  and you can extract data from this page just by left-clicking on this icon.


### Scraping script details




```javascript
{"selector":"root element selector (mand)",
 "rowsRange": "[start], end], step] (opt)", 
"row": {
"selector":"row element selector (mand)", 
"fields":[{
 "selector":"field selector (mand)",
 "name":"column name (mand)",
 "type":"string|int|float|boolean", 
 "source":"text|attr:xxx|input|input_or_text",   
 "preprocess": "function_name (opt)"  }
 ]}}
```


Script uses [JSON](http://www.json.org/)  syntax, so stick to it exactly - unfortunately parser is not very particular about syntax errors.

Script uses CSS **selectors**, with jQuery extensions -  for available selectors and their usage refer to [JQuery documentation](http://api.jquery.com/category/selectors/?rdfrom=http%3A%2F%2Fdocs.jquery.com%2Fmw%2Findex.php%3Ftitle%3DSelectors%26redirect%3Dno). Selectors are always evaluated in the context of their parent ( row in root context, field in row context). In order to identify right selectors you might need some other FF addon that will enable to browse page HTML code - I personally prefer [Firebug](https://getfirebug.com/).

Script identifies  root element - an element which contains all required data (table, ul, div ...), then repeating row elemets (tr, div, li, ..) and finally individual fields/column elements (td, div, span, input ...).

**rowsRage** \- for selected set of rows you can define its subset by defining starting index (zero based), ending index (can be negative, -2 means two before last) and step.  rowsRage is optional, if not used all rows identified by selector are used.

You can define as many fields as needed  within **fields** array(they need to be separated by comma). For each field on a row, apart of its selector,  you define:

**name** \- name is mandatory and is used as column header in CSV format.

**type** \- *string* is the default type , *int* and *float* are numeric types (parsed by [parseInt](https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Global_Objects/parseInt) and [parseFloat](https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Global_Objects/parseFloat) JavaScript functions), *boolean* has values true (for 'true' or 'yes'or  'y' or  '1') or false (for everything else).

**source** \- determines what is used from selected element(s):
*text*  - all  text  within selected element(this is default, if source is not specified)
*attr:xxx* \- value of xxx attribute from  first selected element
*input* \- value of first input found within selected element(s)
<em>input_or_text</em> \- value of first input found within selected element(s), if there is none, then all  text within selected element

**preprocess** \- function to pre-process text of a field before converting it  to given type - currently there are 2 functions `numberNormalize` and `numberNormalizeCZ`, which  remove all non digit characters (numberNormalizeCZ also replaces , with .).


## Sharing Scraping Scripts


Extension has possibility to load scripts for an URL - there is a parameter "URL of remote source of scrapers" in the  extension preferences.  This URL should refer to a JSON file, which contains an array of scraping scripts definitions (JSON objects). To get full scraping script JSON object use "Copy Script" button on  "Define Scraping Script" dialogue.  When this extension parameter is filled correctly, scraping scripts are downloaded and set up and  also with each new start of the browser scripts they are updated.


## Troubleshooting


In case of problems check Error Console (Tools/Web Developer/Error Console or Ctrl+Shift+J), extension logs there various messages.



</section>




<section class="tab-panel" id="tabs-399-0-2">



## Screenshots




<div class="gallery" data-gallery="" id="metaslider_770"><figure><a href="/wp-content/uploads/scraper_def.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/scraper_def-539x404.png" width="800"/></a><figcaption>Scraping script/recipe definition panel</figcaption></figure><figure><a href="/wp-content/uploads/choose_edit.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/choose_edit-303x227.png" width="800"/></a><figcaption>Choose scraper to edit</figcaption></figure><figure><a href="/wp-content/uploads/result.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/result-540x405.png" width="800"/></a><figcaption>Results panel</figcaption></figure><figure><a href="/wp-content/uploads/prefs.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/prefs-592x444.png" width="800"/></a><figcaption>Add-on preferences</figcaption></figure></div>




</section>




<section class="tab-panel" id="tabs-399-0-3">



## Download



Install from [here](https://addons.mozilla.org/en-US/firefox/addon/ffscrap/).

Source is available on [GitHub](https://github.com/izderadicka/ffscrap).

Dual licensed under[ MPL 2.0](http://www.mozilla.org/MPL/2.0/) or[ GPL v3](http://www.gnu.org/licenses/gpl.html).



</section>




</div>

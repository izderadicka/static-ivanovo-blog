+++
title = "APEX - Dynamic Actions with Report Region "
path = "/apex-dynamic-actions-with-report-region/"
date = "2012-10-05T16:48:07"
include_in_feeds = true
[extra]
wordpress_id = 220
kind = "post"
node_key = "220"
author = "admin"
source_url = "http://zderadicka.eu/apex-dynamic-actions-with-report-region/"
source_guid = "http://zderadicka.eu/?p=220"
source_date_gmt = "2012-10-05 15:48:07"
[taxonomies]
category = ["Programming"]
tag = ["Ajax", "Apex", "Javascript", "PL/SQL"]
+++
In many scenarios it would be nice if we can provide some dynamic actions to report (classical) region, which can be handled via Ajax calls, rather then submitting a whole page  - these actions could include:


<ul>
<li>Delete a line in report</li>
<li>Edit a one item on one line</li>
<li>Adding a line  from other pop-up page</li>
<li>Change order of lines</li>
<li>And and many others similar<span id="more-220"></span></li>
</ul>


Consider report like this one:

<a href="/wp-content/uploads/rep1.png" rel="attachment wp-att-222"><img alt="" class="alignnone size-full wp-image-222" decoding="async" height="284" loading="eager" sizes="(max-width: 420px) 100vw, 420px" src="/wp-content/uploads/rep1.png" srcset="/wp-content/uploads/rep1.png 420w, /wp-content/uploads/rep1-300x202.png 300w" title="rep1" width="420"/></a>

Here we want two have two Ajax actions: first when '<span style="color: #ff0000; font-weight: bold; text-transform: uppercase;">X</span>'  is clicked then we want this  line to be deleted; second, when we change quantity on a line, this action should be stored to the  database.

For Column QTY we will use custom column formatting (**Column Format/Html Expression**), rather then predefined column display type (Display As):


```html
<input id="QTY-#ROWNO#" onchange="updateQty(this, #ID#)" onkeypress="disableSubmit(this,event)" value="#QTY#" size="3"/>
```


Last column in the table will have a link displaying <span style="color: #ff0000; font-weight: bold; text-transform: uppercase;"> X</span> (**Link Tex**t: X,** Link Attributes**: `style="color:red; font-weight:bold; text-decoration:none"`  ) and linked to ** URL**: `javascript:removeItem(#ID#)`.

Then we have do define 2 hidden page items (used to submit values in Ajax calls), and also Ajax Callback processes as shown below:

<a href="/wp-content/uploads/rep2.png" rel="attachment wp-att-225"><img alt="" class="alignnone wp-image-225" decoding="async" height="362" loading="lazy" sizes="(max-width: 1002px) 100vw, 1002px" src="/wp-content/uploads/rep2.png" srcset="/wp-content/uploads/rep2.png 1002w, /wp-content/uploads/rep2-300x108.png 300w" title="rep2" width="1002"/></a>

The Ajax Callback processes are fairly straightforward - they should be of **Type**: "PL/SQL anonymous block" , with  **Process Point :** "OnDemand ...".   "Update Quantity" process just runs simple update query:


```sql
update your_table set qty=:P3_NEW_QTY where id= :P3_LINE_ID;
```


And "Delete line" process runs simple delete query:


```sql
delete from your_table where id= :P3_LINE_ID;
```


Last piece is  Javascript code to glue this all together - JS should be put in region definition in **Header and Footer/ Header Region**


```javascript
<script type="text/javascript">
function disableSubmit(elem,event) {
if ( event.which == 13 ) { 
event.preventDefault();
$(elem).blur()
return false
}
}

function updateQty(elem,id) {
var regId= '#REGION_STATIC_ID#'.substr(1);
var req=new htmldb_Get(null, $v('pFlowId'), 'APPLICATION_PROCESS=Update Quantity', $v('pFlowStepId'));
    req.add('P3_NEW_QTY', $(elem).val());
    req.add('P3_LINE_ID', id);
    req.GetAsync(function () {
	if (p.readyState==4) {
	$a_report(regId);
	}
    });
}

function removeItem(id) {
var regId= '#REGION_STATIC_ID#'.substr(1);
var req=new htmldb_Get(null, $v('pFlowId'), 'APPLICATION_PROCESS=Delete line', $v('pFlowStepId'));
    req.add('P3_LINE_ID', id);
    req.GetAsync(function () {
	if (p.readyState==4) {
	$a_report(regId);
	}
    });
}
</script>
```


Some details about this JS code:

**lines 2-6** \- since we want to update just individual lines via Ajax calls,   we want to prevent default behaviour of input, that all form is submitted (if there are aby visible page items on page then there is a form element encapsulated in a form). However we want to keep possibility to fire change event by pressing Enter. The only easy way I can think of was firing blur event - **line 5**\- if you know better way how to do it. please leave a comment here.

**lines 12 and 24** \- this initiates Ajax requests to our processes - note that name of the process has to be specified in 3rd parameter in form 'APPLICATION\_PROCESS=Process name'.  Any page items needed for page process has to be submitted with that requests - `add` method should be used.

**lines 17 and 28** \- when Ajax call is done we need to reload report - this can be done easily by APEX JS function $a\_report, however we need to know id of region, where report is rendered.  If  we render script in region header, like in this case, we can use replacement string #REGION\_STATIC\_ID# as done on **lines 11 and 23**.

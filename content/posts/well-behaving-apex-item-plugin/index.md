+++
title = "Well Behaving APEX Item Plugin "
path = "/well-behaving-apex-item-plugin/"
date = "2012-09-27T06:55:54"
include_in_feeds = true
[extra]
wordpress_id = 171
kind = "post"
node_key = "171"
author = "admin"
source_url = "http://zderadicka.eu/well-behaving-apex-item-plugin/"
source_guid = "http://zderadicka.eu/?p=171"
source_date_gmt = "2012-09-27 05:55:54"
categories = ["Programming"]
tags = ["Apex", "Javascript", "PL/SQL"]
+++
I 've recently created <a href="/projects/oracle-application-express-and-plsql/" title="Oracle Application Express and PL/SQL"> multiselect plugin</a> for APEX 4.1 -  there is still little information about how exactly write APEX plugins,  and some aspects - like cascading LOV, I have not found explained anywhere, so I'd like to share my experiences here:


### What You Need


To write plugin you will need:


<ul>
<li>Oracle Database and APEX running somewhere -   the<a href="http://download.oracle.com/docs/cd/E23903_01/doc/doc.41/e21673/toc.htm"> installation manual</a> for APEX is very good and you can go step by step  according to it</li>
<li>Knowledge of  PL/SQL - it is good to have <a href="http://docs.oracle.com/cd/E11882_01/appdev.112/e25519/toc.htm">PL/SQL Reference</a> at your hand</li>
<li><a href="http://download.oracle.com/docs/cd/E23903_01/doc/doc.41/e21676/toc.htmhttp://">Reference documentation for APEX 4.1 API</a></li>
<li>Some knowledge of APEX and also some basic knowledge of plugins - try some available tutorials you can find on web - this article will focus on rather specific issues within Item plugin.</li>
<li>Oracle SQL/Developer (or other development tool)- to write PL/SQL  - optional, if you are PL/SQL god and can write correct code by heart - if you struggling with PL/SQL like me this is an invaluable helper.</li>
<li>Web server running on your local machine - to help to develop  Javascript part of plugin</li>
<li>Firefox with <a href="http://getfirebug.org">Firebug</a> - to debug Javascript (or Chrome, if you prefer)<span id="more-171"></span></li>
</ul>




### Creating plugin


Create plugin in APEX -   follow usual steps - plug-in type has to be <em>Item</em>.
For Cascading  LOV, Read-Only and other  features you should enable Standard Attributes like this:

<a href="/wp-content/uploads/attrs.png" rel="attachment wp-att-174"><img alt="" class="alignnone size-full wp-image-174" decoding="async" height="194" loading="eager" sizes="(max-width: 825px) 100vw, 825px" src="/wp-content/uploads/attrs.png" srcset="/wp-content/uploads/attrs.png 825w, /wp-content/uploads/attrs-300x70.png 300w" title="attrs" width="825"/></a>

Save and also add any plug-in custom attributes, that you need.


### Coding PL/SQL part - rendering


Develop you PL/SQL code in a separate package in SQL Developer.  It is really hard to write more complex code directly in APEX.   You can then reference <em>Render function name</em> as package\_name.function\_name.  Only when coding is done and plugin is tested and working fine, copy body of the package to plugin definition.

Start with rendering function:


```sql
function render_multiselect(
    p_item                in apex_plugin.t_page_item,
    p_plugin              in apex_plugin.t_plugin,
    p_value               in varchar2,
    p_is_readonly         in boolean,
    p_is_printer_friendly in boolean )
    return apex_plugin.t_page_item_render_result

    is

l_result apex_plugin.t_page_item_render_result;

c_title_param apex_application_page_items.attribute_01%type:=nvl(p_item.attribute_01, 'Select one or more items');
c_style apex_application_page_items.attribute_02%type:=p_item.attribute_02;

BEGIN

if apex_application.g_debug then
apex_plugin_util.debug_page_item( p_plugin, p_item, p_value, p_is_readonly, p_is_printer_friendly);
end if;

if p_is_readonly or p_is_printer_friendly then
apex_plugin_util.print_hidden_if_readonly(p_item.name, p_value, p_is_readonly, p_is_printer_friendly);
--todo change to custom procedure, which will display list of selected diaplay values
render_readonly(p_item, p_plugin,  p_value);
return l_result;
end if;

apex_javascript.add_library (
    p_name                  => 'jquery.selectlist',
    p_directory             => p_plugin.file_prefix
     );

apex_javascript.add_library (
    p_name                  => 'ms_init',
    p_directory             => p_plugin.file_prefix
     );

apex_javascript.add_onload_code (
    p_code => 'MultiSelectInit('||
                  '"#'||p_item.name||'",'||
                  '{'||
                  apex_javascript.add_attribute('ajaxIdentifier',      apex_plugin.get_ajax_identifier)||
                  apex_javascript.add_attribute('dependingOnSelector', apex_plugin_util.page_item_names_to_jquery(p_item.lov_cascade_parent_items))||
                  apex_javascript.add_attribute('optimizeRefresh',     p_item.ajax_optimize_refresh)||
                  apex_javascript.add_attribute('pageItemsToSubmit',   apex_plugin_util.page_item_names_to_jquery(p_item.ajax_items_to_submit))||
                  apex_javascript.add_attribute('nullValue',           p_item.lov_null_value, false, false)||
                  '});',
                  p_key => 'multiselect_init_'||p_item.name);

if c_style is null then    
apex_css.add_file (
    p_name => 'selectlist',
    p_directory => p_plugin.file_prefix,
    p_version => null);
else
apex_css.add( p_css=>c_style, 
              p_key=> 'multiselect_style');
end if;

htp.p('<select name="'||apex_plugin.GET_INPUT_NAME_FOR_PAGE_ITEM(true)||
'" id="'||p_item.name||'"  multiple="multiple" title="'||c_title_param||'">');    

render_options(p_item, p_value);
htp.p('</select>');
return l_result;
END;
```


<strong> lines 18 -20</strong> \- It is always good to add  this debugging function, you can then see some info in Apex debug page - but do not expect too much - I did not find it  very appealing, but at least it shows with what parameters plugin was started.

<strong>lines 22-27</strong> \- Each good page item should be able to render itself as read only.   For standard read only rendering you can use API function `apex_plugin_util.print_display_only`, which will render something like this `<span>item_value</span>`. If more sophisticated rendering is needed - like in my case - custom functions is needed.
Also it is need to render hidden input element for read-only - so it's value is available to page processes after posting page. This is done by `apex_plugin_util.print_hidden_if_readonly` function.

<strong>lines 29-38, 51-59</strong> \- Adding javascript and css - for development I highly recommend  to host files on your desktop, where you can easily edit it.   Just then set `p_direcory` parameter as 'http://localhost/your\_dir'. Also reminding that `p_name` has to be without extensions.

<strong>lines 39-49</strong> \-  The item will have some Javascript code, which needs to get started on the page. Best practice is to have one function for this into which you'll supply all necessary parameters:
<em>item selector</em> \-   this is id of HTML element representing item - should be '#'||p\_item.name
<em>ajaxIdentifier</em> \- this will be used in ajax calls to get new LOV values - or refresh item value in other cases
<em>dependingOnSelector</em> \- <a tabindex="999">Cascading LOV Parent Item(s)</a> \- e.g. when they change, LOV has to be updated in this item via ajax call. In Javascript we will need their jQuery selectors - so there is convenient function`  apex_plugin_util.page_item_names_to_jquery `, which  creates list of selectors from array of item names.
<em>optimizeRefresh</em> \- not used in this case
<em>pageItemsToSubmit</em> \- selectors of  all other items, this item depends on - value of these must be posted with ajax request.
<em>nullValue</em> \- the value that should be used when page item is null.

<strong>lines 61-65</strong> \- HTML code for your item should be outputted -  the name of input element has to created by `apex_plugin.GET_INPUT_NAME_FOR_PAGE_ITEM(true)` function and id has to be `p_item.name`.

 

One specific topic for multi-select  items -  Apex maintains value of multi-select item as a string that contains values separated by colon - VAL1:VAL2:VAL3.
For rendering we have to decode item value to be able to correctly identify selected options.   There is a function in API `apex_util.string_to_table`, which converts string to PL/SQL associative array, the only issue is that one cannot use convenient operators for associative array like IN, CONTAIN - so  easiest way how to find if it contains some values is to write small function like this:


```sql
function in_arr(p_val varchar2,   p_selected_arr APEX_APPLICATION_GLOBAL.VC_ARR2) return boolean
is
begin
for i in 1..p_selected_arr.count loop
if p_val=p_selected_arr(i) then 
return true;
end if;
end loop;
return false;
end;
```


With this function we can easily render selected options with this function:


```sql
procedure render_options( p_item  in apex_plugin.t_page_item,  p_value  in varchar2) 
is
l_column_value_list   apex_plugin_util.t_column_value_list;
l_selected_arr APEX_APPLICATION_GLOBAL.VC_ARR2;
begin

l_column_value_list :=
        apex_plugin_util.get_data (
            p_sql_statement    => p_item.lov_definition,
            p_min_columns      => 2,
            p_max_columns      => 2,
            p_component_name   => p_item.name);

l_selected_arr:=apex_util.string_to_table(p_value);

 for i in 1 .. l_column_value_list(1).count
    loop
        sys.htp.p(
            '<option value="'||
            sys.htf.escape_sc(l_column_value_list(2)(i))|| -- value column
            '"'||selected_attr(l_column_value_list(2)(i),l_selected_arr)||'>'||
            sys.htf.escape_sc(l_column_value_list(1)(i))|| -- display column
            '</option>');
    end loop;
end;
```


And one more useful API function: `apex_plugin_util.get_data`, it  gives you LOV as an array - see <strong>line 8-12</strong> \- through which you can easily iterate as shown above.

Now you can put new item based on this new plugin on some page  and see how it renders in HTML (use Firebug to see details).


### Coding Javascript part


Much functionality of Apex page item is happening at client side, so Javascript code is as important as PL/SQL code.  As I have written, when developing, have Javascript code hosted on you local machine so you can edit it and test it easily.  It is also important to switch application to DEBUG mode, when developing Javascript, otherwise your script is loaded minified, so it is impossible to debug.

Here is Javascript code for my plugin, and I'll explain some key parts below:


```javascript
function MultiSelectInit(id, optionsIn) {
	var ms = $("select#" + id);
	var widget = ms.selectList({
		instance : true,
		//somehow addAnimate/removeAnimate interfers with setValue function if adding same item as already in the list
		// I think this is because remove will call remove function, only after animation,
		// when new items are added, thus it'll remove items from select list'
		addAnimate: false, 
		removeAnimate: false,
		onAdd: fireChange,
		onRemove: fireChange
	});
	var dropdown = ms.next('select.selectlist-select');
	var list = dropdown.next('ul.selectlist-list');

	var options = $.extend({
		dependingOnSelector : null,
		optimizeRefresh : true,
		pageItemsToSubmit : null,
		optionAttributes : null,
		nullValue : ""
	}, optionsIn)

//registers with apex item framework
//TODO: implement  toggle? 
	ms.each(function() {
		apex.widget.initPageItem(this.id, {
			nullValue : options.nullValue,
			hide:hide,
			show:show,
			enable:enable,
			disable:disable,
			setValue:setValue
		});

	});

//fires change event on hidden select
function fireChange() {
ms.trigger('change');
};
//clears all options that have values - e.g. leaves title option
function clear() {
	$('option[value]',dropdown).remove();
}

function ajaxData() {
	// initialize the AJAX call parameters
    var lData = { p_request: "NATIVE="+options.ajaxIdentifier,
                  p_flow_id: $v('pFlowId'),
                  p_flow_step_id: $v('pFlowStepId'),
                  p_instance: $v('pInstance')
                };

    // add all page items we are depending on and the one we always have to submit to the AJAX call
    apex.jQuery(options.dependingOnSelector+','+options.pageItemsToSubmit).each(function(){
      var lIdx;
      if (lData.p_arg_names===undefined) {
        lData.p_arg_names  = [];
        lData.p_arg_values = [];
        lIdx = 0;
      } else {
        lIdx = lData.p_arg_names.length;
      }
      lData.p_arg_names [lIdx] = this.id;
      lData.p_arg_values[lIdx] = $v(this);
    });
    return lData;
}
function refresh() {
	ms.trigger('apexbeforerefresh');
	clear();
	dropdown.after('<span class="loading-indicator"></span>');
	$.ajax({
		url:'wwv_flow.show',
		type:'post',
		dataType:'json',
		traditional: true,
		success: setOptions,
		data: ajaxData(),
		//This is for ajaxQueue - aborting previous requests from same source - port
		mode:'abort',
		port: "multiselect"+id,	
	});

}

function setOptions(data) {
	 // remove loading indicator

    // check for errors first
    if (data.error) {
      alert(data.error);
      return false;
    }
	var selected=ms.val();
	var found=new Array();
	var html="";
	$.each(data, function(){
		var attr="";
		if (selected && selected.indexOf(this.r)>=0) {
			attr=' selected="selected" disabled="disabled"';
			found.push(this.r)
		}
		html+='<option value="'+this.r+'"'+attr+'>'+this.d+'</option>\n';
	});
	dropdown.append(html);
	//set it back to title option
	dropdown.val("");
	//remove values that are not in current options
	if (selected) selected.forEach(function(val) {
		if (found.indexOf(val)<0) widget.remove(val);
	});
	dropdown.next('.loading-indicator').remove();
	ms.trigger('apexafterrefresh');

}

function hide() {
	dropdown.hide();
	list.hide();
}

function show() {
	dropdown.show();
	list.show();
}

function disable() {
	dropdown.attr('disabled', 'disabled');
	widget.setOptions({clickRemove:false});
	$('li', list).addClass('disabled');
}

function enable() {
	dropdown.removeAttr('disabled');
	widget.setOptions({clickRemove:true});
	$('li', list).removeClass('disabled');

}

function setValue(val, displayVal) {
	console.log(val);
	widget.remove();
	var values=val.split(':');
	for (i=0;i<values.length;i++) {
		existing_option=$('option[value="'+values[i]+'"]', dropdown);
		if (existing_option.length>0)		widget.add(values[i]);

	}

}

if (options.dependingOnSelector) {
	$(options.dependingOnSelector).change(refresh);
}
ms.bind("apexrefresh", refresh)
}
```


<strong> line 1</strong> \- we will have one function to initialize our plugin on page - we need its unique selector (from id) and some options

<strong>lines 8-9 and lines 39-40</strong> \- the plugin item has to trigger change event on  element with id equal to item name (PXX\_...). In complex plugin, this might not be automatic - like in this one because the element is hidden select - thus we have to fire change event automatically.   Change event is require for this item to serve as cascading source (see below comment for receiving change event from cascading items - lines )

<strong>lines 16-22</strong> \- these are options we set in rendering method and which are crucial for javascript.

<strong>lines 27-33</strong> \-  we need to register our page item with Apex JS framework - this will assure that it  behaves correctly and reacts on all appropriate client side events.
Especially we can register JS functions, which  handle some aspects of an interactive interface - hide and show item,  enable and disable item,  set or get value via Apex JS API - functions `$v` and `$s` .

<strong>line 48-70</strong> \- ajax call to Apex is basically HTTP POST request, which has to contain many mandatory parameters:
<em>p_request</em>:  means request type - for plugin ajax call it has to be `"NATIVE="+options.ajaxIdentifier`, where ajaxIdentifier is generated by PL/SQL API function  `apex_plugin.get_ajax_identifier`.
<em>p_flow_id</em>:  is numeric id of the application - provided by application item <em>pFLowId</em> via `$v('pFlowId')` Apex JS API function
<em>p_step_id</em> : is numeric page id - provided by application item <em>pStepId</em>
<em>p_instance</em>: current session id - provided by application item <em>pInstance</em>
<em>p_arg_name</em>: is an array of names of all page items that has to be submitted within this ajax request( their actual values are necessary to get new LOV for this item). They are taken from options we provided, when rendered call to our JS function - `options.dependingOnSelector` \- all cascading parent items, `options.pageItemsToSubmit` \- any other relevant items.
<em>p_arg_values</em>: is an array of their values

<strong>line 70</strong> \- this function is used to get and update LOV for this item, if any cascading parent item has changed.

<strong>lines 71 and 115</strong> \- we should trigger Apex specific events apexbeforerefresh and apexafterrefresh, when refreshing LOV

<strong>lines 154-155</strong> \- in order to react on changes in cascading parents, we have to subscribe to their change event.

<strong>line 157</strong> \- and also to bind to apex specific apexrefresh event


###  Ajax call and final steps


The only piece left is now to handle ajax call on server side (on JS side we expect LOV items as JSON objects with x.r for return value and x.d for display value). To generate fresh LOV we need PL/SQL function like this:


```sh
function multiselect_ajax(p_item   in apex_plugin.t_page_item,
                          p_plugin in apex_plugin.t_plugin )
    return apex_plugin.t_page_item_ajax_result

as
l_ret apex_plugin.t_page_item_ajax_result;
begin

apex_plugin_util.print_lov_as_json(p_item.lov_definition,
                                  p_item.name,
                                  true);
return l_ret;
end;
```


As you can see for all the work we can just leverage API function `apex_plugin_util.print_lov_as_json`. Our ajax function should be referenced in field AJAX Function Name in Callbacks section of plugin definition.

To test LOV cascading add another item on page and make it cascading parent of this one.  When the other item changes, there should be a ajax call on background, fetching updated LOV for the plugin item. This can be observed in detail with Firebug (in  Net section - filter XHR request types only - to see only ajax calls).

Remaining final touches are to remove development set-up - e.g. copy body of our PL/SQL development package into plugin definition <em>Source/PL/SQL Code</em> field, rename callbacks (remove package prefix). And load all JS and CSS files to plugin and change their location in PL/SQL code - parameter `p_directory` in functions `apex_javascript.add_library` and `apex_css.add_file` should be set as `p_plugin.file_prefix`.

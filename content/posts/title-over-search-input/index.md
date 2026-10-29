+++
title = "Title Over Search Input"
path = "/title-over-search-input/"
date = "2012-09-22T07:44:49"
include_in_feeds = true
[extra]
wordpress_id = 69
kind = "post"
node_key = "69"
author = "admin"
source_url = "http://zderadicka.eu/title-over-search-input/"
source_guid = "http://zderadicka.eu/?p=69"
source_date_gmt = "2012-09-22 06:44:49"
categories = ["Web Design"]
tags = ["web design", "wordpress"]
+++
One of customization I've done for this WordPress  theme was to put label text over search input.   I've found that quite nice design element and space saving optimization.

Basically there are 2 main approaches:<span id="more-69"></span>


### a) Use HTML5


This is very straightforward, but I did not like  usability of the solution - the problem is that label disappears only after you write your first letter, which I have to say I found bit annoying.
But solution is super-simple, just add attribute  <strong>placeholder</strong>


```html
<input id="s" type="text" placeholder="Search This Site ..." name="s">
```




### b) Use \<label\> tag, plus style, plus javascript


HTML:


```html
<label for="s">Search This Site ...</label>
<input id="s" type="text" name="s" value="">
```


CSS:


```css
nav #search-inputs label {
 display: inline;
 cursor: text;
 position: absolute;
 top: 5px;
 left: 5px;
}
```


Javascript (requires JQuery library):


```javascript
jQuery(function () {
var $input=jQuery('nav #search-inputs #s');
var $label=jQuery('nav #search-inputs label');
if (! $input.val() ) {
$label.show();
}
else {
$label.hide();
}
$input.focus( function () {
$label.hide()
});
$input.blur( function () {
if (! this.value) $label.show();
});
$label.click( function () {
$input.trigger('focus');
});
});
```


For WordPress theme it is recommended to have JavaScript in A separate file - the proper way to load code on page is using PHP function <strong>wp_enqueue_script</strong>:


```php
wp_enqueue_script(
        'search-script',
        get_template_directory_uri() . '/scripts/search.js',
        array('jquery')
    );
```


The best place to put this code is <strong>functions.php</strong> in the theme - the function which is called on <strong>wp_enqueue_scripts</strong> action.

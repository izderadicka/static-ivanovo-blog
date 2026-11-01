+++
title = "LOB As A Link in Apex"
path = "/lob-as-a-link-in-apex/"
date = "2012-11-08T10:10:32"
include_in_feeds = true
[extra]
wordpress_id = 332
kind = "post"
node_key = "332"
author = "admin"
source_url = "http://zderadicka.eu/lob-as-a-link-in-apex/"
source_guid = "http://zderadicka.eu/?p=332"
source_date_gmt = "2012-11-08 09:10:32"
[taxonomies]
category = ["Programming"]
tag = ["Apex"]
+++
APEX 4.1 enables to include a download link to LOB object in standard or interactive repors.   Documentation is available  [here](http://docs.oracle.com/cd/E23903_01/doc/doc.41/e21674/advnc_blob.htm#BCGBCHBD), however the approach is not so obvious from it.  So here is quick recap, how it works:


<ol>
<li>In report query you must have column that contains** LOB length**  (not LOB itself!) -  so something like<code> select dbms&#95;lob.getlength(MY&#95;LOB) my&#95;lob&#95;lenght from MY&#95;TABLE</code></li>
<li>The report column corresponding to LOB length should be set as:
**Display As: Display As Text (escape special characters, does not save state)**
<strong> Number/Date Format: DOWNLOAD:TABLE_NAME:LOB_COLUMN_NAME:ROW_PRIMARY_KEY_COLUMN</strong>
(beware names are case sensitive here)</li>
<li>When more sophisticated download behaviour is needed you should also include  columns for MIME type of data, file name and modification timestamp.   Once you store basic DOWNLOAD format you can edit it with masked edit link **"BLOB Download Format Mask"**</li>
<li>Download link is only shown when LOB length &gt; 0 and is not null.</li>
</ol>


<span id="more-332"></span>

Screenshot of column definition with DOWNLOAD format masked edit:

<a href="/wp-content/uploads/apex_downlink.png" rel="lightbox[download_screenshot1]"><img alt="" class="alignleft wp-image-336" decoding="async" height="271" loading="eager" sizes="(max-width: 640px) 100vw, 640px" src="/wp-content/uploads/apex_downlink-1024x434.png" srcset="/wp-content/uploads/apex_downlink-1024x434.png 1024w, /wp-content/uploads/apex_downlink-300x127.png 300w, /wp-content/uploads/apex_downlink.png 1269w" title="apex_downlink" width="640"/></a>

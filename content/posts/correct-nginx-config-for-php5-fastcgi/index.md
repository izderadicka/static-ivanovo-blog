+++
title = "Correct nginx config for PHP5 fastCGI"
path = "/correct-nginx-config-for-php5-fastcgi/"
date = "2014-11-22T18:30:18"
include_in_feeds = true
[extra]
wordpress_id = 953
kind = "post"
node_key = "953"
author = "admin"
source_url = "http://zderadicka.eu/correct-nginx-config-for-php5-fastcgi/"
source_guid = "http://zderadicka.eu/?p=953"
source_date_gmt = "2014-11-22 17:30:18"
categories = ["Admin"]
tags = ["nginx", "php"]
+++
It's surprising how much incorrect informations  are available on web for this topic.   I was struggling to get correct configuration for <a href="https://simplesamlphp.org/">simpleSAMLphp</a> package (on Ubuntu 14.04). This is finally correct config (inside server section):<span id="more-953"></span>


```sh
        rewrite ^(/simplesaml/?)(.*) /saml/www/$2 break;
	
	location / {
		# First attempt to serve request as file, then
		# as directory, then fall back to displaying a 404.
		try_files $uri $uri/ =404;
		
	}

	location ~ \.php$ {
        	fastcgi_split_path_info ^(.+\.php)(/.+)$;
        	fastcgi_pass unix:/var/run/php5-fpm.sock;
        	fastcgi_index index.php;
        	include fastcgi_params;
        	fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    		fastcgi_param PATH_INFO       $fastcgi_path_info;
	}

```


Key insight is to set additionally two CGI parameters SCRIPT\_FILENAME and PATH\_INFO,   but <span style="text-decoration: underline;">after</span>  `include fastcgi_params` (this configuration also sets SCRIPT\_FILENAME).

Also I had to change php.ini:


```
cgi.fix_pathinfo=0

```

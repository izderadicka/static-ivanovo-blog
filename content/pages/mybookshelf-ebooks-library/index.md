+++
title = "MyBookshelf - EBooks Library"
path = "/projects/python/mybookshelf-ebooks-library/"
date = "2012-10-07T17:32:50"
include_in_feeds = false
[extra]
wordpress_id = 209
kind = "page"
node_key = "209"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/mybookshelf-ebooks-library/"
source_guid = "http://zderadicka.eu/?page_id=209"
source_date_gmt = "2012-10-07 16:32:50"
menu_order = 0
parent = "/projects/python/"
+++
<span style="color: #ff0000;">MYBOOKSHELF WAS SUPERSEDED WITH NEW APPLICATION</span> [MYBOOKSHELF2](/projects/python/mybookshelf2-ebooks-management-and-sharing/)

MyBookshelf  is web based program to manage your library of ebooks. It is fully web based, with simple, yet powerful interface. It's written in python language and django web framework offers great flexibility and extensibility. Ideal for sharing ebooks within a group of people.



<div class="tabset" data-tabs="" id="tabs_209_0">



<section class="tab-panel" id="tabs-209-0-0">



## Description



This project started because my collection of ebooks grew bit larger and I need some way how to manage them.  I look at Calibre, it is a great program with many features, but has one significant issue from my perspective -  ebook can have only one file for given format.   However I do have for some ebooks  many files for one format (as I can get them from various sources) and do want to store them all.  So I decided to create my own solutions, which also should be bit exercise for me in modern web interfaces.

Key design decisions were that it is web based (django), with MySql database backend,  store only small set of ebooks metadata, no covers (purpose is  to find ebook quickly - any extensive metadata can be found on internet), Linux platform, intended to run on my home server and provide services to all my family.

Key features:


<ul>
<li> Modern web interface with AJAX features (autocomplete etc).</li>
<li>Easy search and browing in various dimensions (Author, Title, Category ...)</li>
<li>Multiple formats supports and<span style="text-decoration: underline;"> multiple files in same format</span></li>
<li>One-click conversion to ebook format (epub, mobi, fb2), even <span style="text-decoration: underline;">from doc or docx</span> (using LibreOffice and ebook-convert)</li>
<li>Ebooks lists (bookshelves) to organize books. Bookshelves can be  created easily as private or shared.</li>
<li>Guided ebook upload (minimizes duplications)</li>
<li>Can upload compressed files (zip or rar) - will be decompressed automatically</li>
<li>Mass import from disk (using command like utility)</li>
<li>Extensive user and access rights possibilities (thanks to Django)</li>
<li>Admin features (both inline and through Django Admin app)</li>
</ul>




</section>




<section class="tab-panel" id="tabs-209-0-1">



## Screenshots




<div class="gallery" data-gallery="" id="metaslider_775"><figure><a href="/wp-content/uploads/mbs1.png"><img alt="" decoding="async" height="600" loading="eager" src="/wp-content/uploads/mbs1-776x582.png" width="800"/></a><figcaption>Search results</figcaption></figure><figure><a href="/wp-content/uploads/mbs2.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/mbs2-775x581.png" width="800"/></a><figcaption>Ebook detail with admin menu</figcaption></figure><figure><a href="/wp-content/uploads/mbs3.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/mbs3-782x586.png" width="800"/></a><figcaption>Browsing by category</figcaption></figure><figure><a href="/wp-content/uploads/mbs4.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/mbs4-776x582.png" width="800"/></a><figcaption>Bookshelf detail (custom list of ebooks)</figcaption></figure><figure><a href="/wp-content/uploads/mbs5.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/mbs5-714x536.png" width="800"/></a><figcaption>Converted ebooks (can be loaded in a single zip file)</figcaption></figure><figure><a href="/wp-content/uploads/mbs6.png"><img alt="" decoding="async" height="600" loading="lazy" src="/wp-content/uploads/mbs6-775x581.png" width="800"/></a><figcaption>Uploading ebook</figcaption></figure></div>




</section>




<section class="tab-panel" id="tabs-209-0-2">



## Download



Mybookshelf can be installed from source only. Code is hosted on [launchpad](https://launchpad.net/mybookshelf), easiest way to get it is :

`bzr checkout --lightweight lp:mybookshelf`

this will get just trunk version without history, if you plan to develop, should get rather full branch with history:

`bzr branch lp:mybookshelf`

All code is available as open source under GPL v3 license.

Bugs should be reported on [launchpad](https://bugs.launchpad.net/mybookshelf).



</section>




<section class="tab-panel" id="tabs-209-0-3">



## Installation



Mybookshelf will run only on Linux. Installation is manual, here are installation steps (Ubuntu/Debian):


<ol>
<li>**Install dependencies:**
<code>sudo apt-get install apache2 mysql-server python-django python-mysqldb libapache2-mod-wsgi libreoffice libxt6 bzr</code>
<code># calibre installed from latest version rather then from distro packages</code>
<pre class="code-highlight" data-language=""><code><span class="code-line">sudo python -c "import sys; py3 = sys.version_info[0] &gt; 2; u = __import__('urllib.request' if py3 else 'urllib', fromlist=1); exec(u.urlopen('http://status.calibre-ebook.com/linux_installer').read()); main()"</span></code></pre>
</li>
<li>**Install Mybookshelp source:**
<pre class="code-highlight" data-language=""><code><span class="code-line">bzr checkout --lightweight http://bazaar.launchpad.net/~ivan-zderadicka/mybookshelf/trunk/</span></code></pre>
(if you consider development of code use<code> bzr brach</code> instead)
Move file to final destination - like /opt/mybookshelf
<code>sudo mv mybookshelf/ /opt</code></li>
<li>**Create database:**
<code>mysql -u root </code>
<code>mysql&gt; create database ebooks;</code>
<code>Query OK, 1 row affected (0.00 sec)</code>
<code>mysql&gt; grant all on ebooks.&#42; to 'ebooks'@'localhost' identified by 'ebooks';</code>
<code>Query OK, 0 rows affected (0.05 sec)</code>
<code>mysql&gt; flush privileges;</code>
<code>Query OK, 0 rows affected (0.00 sec)</code>
<code>exit</code></li>
<li>**Create directories for ebooks:**
<code>mkdir ebooks</code>
<code>mkdir ebooks/library</code>
<code>mkdir ebooks/converted</code>
<code>mkdir ebooks/recon</code>
<code>chmod -R 0777 ebooks</code>
last command is to assure that web server user will have write access - if you are concerned about security, you can consider different setup - special security group or something like this</li>
<li>**Edit /opt/mybookshelf/settings.py**
Set database parameters:
<code>DATABASE&#95;NAME = 'ebooks'            </code>
<code>DATABASE&#95;USER = 'ebooks'            </code>
<code>DATABASE&#95;PASSWORD = 'ebooks'</code>
Set ebook directories:
<code>BOOKS&#95;BASE&#95;DIR="/home/ivan/ebooks/library"</code>
<code>BOOKS&#95;RECON&#95;DIR="/home/ivan/ebooks/recon"</code>
<code>BOOKS&#95;CONVERTED&#95;DIR="/home/ivan/ebooks/converted"</code>
And disable debug toolbar (in MIDDLEWARE_CLASSES and INSTALLED APPS )
<code>#'debug&#95;toolbar.middleware.DebugToolbarMiddleware', </code>
<code>#'debug&#95;toolbar',</code></li>
<li>**Now sync database - e.g. create tables and initial data**
<code>cd /opt/mybookshelf/</code>
<code>./manage.py syncdb # also create an admin user!</code>
<code>./manage.py loaddata data.xml</code></li>
<li>**Test it**
<code>./manage.py runserver your&#95;ip:5555</code>
this runs emended server and try to connect with browser to it. Login as your admin user. Try to upload ebook and convert it.  Then stop this command.</li>
<li>**Edit django.wsgi**
set <code>path = '/opt/mybookshelf'</code></li>
<li>**Create new virtual server configuration **in /etc/apache2/sites-available:
<pre class="code-highlight" data-language="apache"><code><span class="code-line"><span class="nt">&lt;VirtualHost</span><span class="w"> </span><span class="s">*:5555</span><span class="nt">&gt;</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">ServerName</span><span class="w"> </span>localhost</span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">ServerAlias</span><span class="w"> </span>localhost</span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">ServerAdmin</span><span class="w"> </span>ivan</span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">DocumentRoot</span><span class="w"> </span><span class="sx">/opt/mybookshelf</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">Alias</span><span class="w"> </span><span class="sx">/robots.txt</span><span class="w"> </span><span class="sx">/opt/mybookshelf/robots.txt</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">Alias</span><span class="w"> </span><span class="sx">/favicon.ico</span><span class="w"> </span><span class="sx">/opt/mybookshelf/favicon.ico</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">Alias</span><span class="w"> </span><span class="sx">/media/</span><span class="w"> </span><span class="sx">/usr/share/pyshared/django/contrib/admin/media/</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">Alias</span><span class="w"> </span><span class="sx">/site_media/</span><span class="w"> </span><span class="sx">/opt/mybookshelf/site_media/</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="w">    </span><span class="nt">&lt;Directory</span><span class="w"> </span><span class="s">/opt/mybookshelf</span><span class="nt">&gt;</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">Order</span><span class="w"> </span>allow,deny</span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">Allow</span><span class="w"> </span>from<span class="w"> </span><span class="k">all</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nt">&lt;/Directory&gt;</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="w">   </span><span class="nt">&lt;Directory</span><span class="w"> </span><span class="s">/usr/share/pyshared/django/contrib/admin/media</span><span class="nt">&gt;</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">Order</span><span class="w"> </span>allow,deny</span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">Allow</span><span class="w"> </span>from<span class="w"> </span><span class="k">all</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nt">&lt;/Directory&gt;</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">WSGIScriptAlias</span><span class="w"> </span>/<span class="w"> </span><span class="sx">/opt/mybookshelf/django.wsgi</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="nt">&lt;/VirtualHost&gt;</span></span></code></pre>
And configure also <code>/etc/apache2/ports.conf</code> and put there <code>Listen 5555</code>.
Also:
<code>sudo ln -s /etc/apache2/sites-available/mybookshelf /etc/apache2/sites-enabled/</code>
<code> sudo apache2ctl restart</code>
and test again in the browser</li>
</ol>




</section>



 



</div>

+++
title = "Oracle DB - Compression of LOBs"
path = "/oracle-db-compression-of-lobs/"
date = "2014-06-11T11:27:39"
include_in_feeds = true
[extra]
wordpress_id = 818
kind = "post"
node_key = "818"
author = "admin"
source_url = "http://zderadicka.eu/oracle-db-compression-of-lobs/"
source_guid = "http://zderadicka.eu/?p=818"
source_date_gmt = "2014-06-11 10:27:39"
categories = ["Admin"]
tags = ["oracle 11g"]
+++
We have some APEX applications for our colleagues, where people can attach files (usually MS Word documents or PDF files).  A straightforward way to implement it was to use a table with BLOB field and connect it with the file item in an upload form.  All works well,  but as times goes on BLOBs are starting to take significant amount of space.    I have been looking for some solution, how to reduce space taken by attached documents and explored Oracle 11g compression capabilities.
For LOBs 11g (Enterprise Edition)  provides new feature called <a href="http://www.oracle.com/technetwork/articles/sql/11g-securefiles-084075.html">SecureFiles</a>, which also enables compression of LOB data. We have migrated our tables to use SecureFiles and saved approximately  50% of space.<span id="more-818"></span>

By default LOBs are still saved by usual way (BasicFiles),  a table must be created  with special options to enable SecureFiles and compression of data.   So I had to migrate our existing BLOB tables to use SecureFiles. Unfortunately this cannot be done easily by `ALTER TABLE` command.  There are basically two possibilities:


<ul>
<li>Create new table with same structure, migrate data and then rename it back to original name -
This has to be done offline. Advantage of this approach is that you do not need any special additional rights for the database and steps are quite straightforward.  Obvious disadvantage is that you must close you application for a while, until you recreate appropriate tables.</li>
<li><a href="http://docs.oracle.com/cd/B28359_01/appdev.111/b28393/adlob_smart.htm#BABDIEGE">Online table redefinition</a> -  is Oracle recommended method, where package DBMS_REDEFINITION is used.</li>
</ul>


However I do not have experiences with this package and it was no problem to bring applications down for a while, so I decided to do it manually step by step.

Here are steps I used to migrate tables:


<ol>
<li>Choose which table(s) to migrate -  you can check how much space each table is occupying with this query:
<pre class="code-highlight" data-language="sql"><code><span class="code-line"><span class="k">SELECT</span><span class="w"> </span><span class="k">table_name</span><span class="p">,</span><span class="w"> </span><span class="k">sum</span><span class="p">(</span><span class="n">bytes</span><span class="p">)</span><span class="o">/</span><span class="mi">1024</span><span class="o">/</span><span class="mi">1024</span><span class="w"> </span><span class="n">size_mb</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="k">FROM</span><span class="w"> </span><span class="p">(</span><span class="k">SELECT</span><span class="w"> </span><span class="n">s</span><span class="p">.</span><span class="n">segment_name</span><span class="w"> </span><span class="k">AS</span><span class="w"> </span><span class="k">table_name</span><span class="p">,</span></span>&#10;<span class="code-line"><span class="w">                 </span><span class="n">s</span><span class="p">.</span><span class="n">bytes</span></span>&#10;<span class="code-line"><span class="w">          </span><span class="k">FROM</span><span class="w"> </span><span class="n">user_SEGMENTS</span><span class="w"> </span><span class="n">s</span></span>&#10;<span class="code-line"><span class="w">          </span><span class="k">WHERE</span><span class="w"> </span><span class="n">s</span><span class="p">.</span><span class="n">segment_type</span><span class="w"> </span><span class="o">=</span><span class="w"> </span><span class="s1">&#39;TABLE&#39;</span></span>&#10;<span class="code-line"><span class="w">          </span><span class="k">UNION</span><span class="w"> </span><span class="k">ALL</span></span>&#10;<span class="code-line"><span class="w">          </span><span class="k">SELECT</span><span class="w"> </span><span class="n">l</span><span class="p">.</span><span class="k">table_name</span><span class="w"> </span><span class="k">AS</span><span class="w"> </span><span class="k">table_name</span><span class="p">,</span></span>&#10;<span class="code-line"><span class="w">                 </span><span class="n">s</span><span class="p">.</span><span class="n">bytes</span></span>&#10;<span class="code-line"><span class="w">          </span><span class="k">FROM</span><span class="w"> </span><span class="n">user_SEGMENTS</span><span class="w"> </span><span class="n">s</span><span class="p">,</span></span>&#10;<span class="code-line"><span class="w">               </span><span class="n">user_lobs</span><span class="w"> </span><span class="n">l</span></span>&#10;<span class="code-line"><span class="w">          </span><span class="k">WHERE</span><span class="w"> </span><span class="n">s</span><span class="p">.</span><span class="n">segment_name</span><span class="w"> </span><span class="o">=</span><span class="w"> </span><span class="n">l</span><span class="p">.</span><span class="n">segment_name</span><span class="p">)</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="k">group</span><span class="w"> </span><span class="k">by</span><span class="w"> </span><span class="k">table_name</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="k">order</span><span class="w"> </span><span class="k">by</span><span class="w"> </span><span class="n">size_mb</span><span class="w"> </span><span class="k">desc</span><span class="p">;</span></span></code></pre>
</li>
<li>Get SQL DDL for your table</li>
<li>Create new table, with same structure:
<pre class="code-highlight" data-language="sql"><code><span class="code-line"><span class="k">CREATE</span><span class="w"> </span><span class="k">TABLE</span><span class="w">  </span><span class="ss">&quot;NEW_TABLE&quot;</span><span class="w"> </span></span>&#10;<span class="code-line"><span class="w">   </span><span class="p">(</span><span class="w">	</span><span class="c1">-- some column definitions  etc.</span></span>&#10;<span class="code-line"><span class="w">	</span><span class="ss">&quot;DATA&quot;</span><span class="w"> </span><span class="nb">BLOB</span><span class="p">,</span><span class="w"> </span></span>&#10;<span class="code-line"><span class="w">   </span><span class="p">)</span></span>&#10;<span class="code-line"><span class="n">lob</span><span class="w"> </span><span class="p">(</span><span class="k">data</span><span class="p">)</span><span class="w"> </span></span>&#10;<span class="code-line"><span class="n">store</span><span class="w"> </span><span class="k">as</span><span class="w"> </span><span class="n">securefile</span></span>&#10;<span class="code-line"><span class="p">(</span><span class="n">compress</span><span class="w"> </span><span class="n">high</span></span>&#10;<span class="code-line"><span class="n">deduplicate</span><span class="p">);</span></span></code></pre>
Basically this is usual CREATE TABLE command, but you have to add lob definition to the end.   For SecureFiles you must explicitly enable compression (with appropriate compression level -   I used high, because attached files are accessed rarely, so space was main concern).   Another nice feature is <a href="http://www.oracle.com/technetwork/database/sfe-092218.html"><strong>deduplication</strong></a>, which you can enable too. Deduplication basically assures that each file is stored only once, even if uploaded many times by different users ( for each LOB a hash of data is calculated,   If another LOB is inserted with same hash,  it is not stored rather it only references the existing one).</li>
<li>Insert data into new table:
<pre class="code-highlight" data-language="sql"><code><span class="code-line"><span class="k">INSERT</span><span class="w"> </span><span class="k">INTO</span><span class="w"> </span><span class="n">NEW_TABLE</span><span class="w"> </span><span class="k">SELECT</span><span class="w"> </span><span class="o">*</span><span class="w"> </span><span class="k">FROM</span><span class="w"> </span><span class="n">OLD_TABLE</span><span class="p">;</span></span></code></pre>
</li>
<li>Drop old table :
<pre class="code-highlight" data-language="sql"><code><span class="code-line"><span class="k">DROP</span><span class="w"> </span><span class="k">TABLE</span><span class="w"> </span><span class="n">OLD_TABLE</span><span class="p">;</span></span></code></pre>
</li>
<li>Rename new table to original name:
<pre class="code-highlight" data-language="sql"><code><span class="code-line"><span class="k">RENAME</span><span class="w"> </span><span class="n">NEW_TABLE</span><span class="w"> </span><span class="k">to</span><span class="w"> </span><span class="n">OLD_TABLE</span><span class="p">;</span></span></code></pre>
</li>
<li>Recreate any constrains, triggers, indexes etc.</li>
<li>Now you can check again space occupied by tables and see how much space you spared - use script from step 1.  Or you can check free space in tablespace(s) by this script:
<pre class="code-highlight" data-language="sql"><code><span class="code-line"><span class="k">select</span><span class="w"> </span><span class="n">tablespace_name</span><span class="p">,</span><span class="w"> </span><span class="k">sum</span><span class="p">(</span><span class="n">bytes</span><span class="p">)</span><span class="o">/</span><span class="mi">1024</span><span class="o">/</span><span class="mi">1024</span><span class="w"> </span><span class="ss">&quot;Free_MB&quot;</span><span class="w"> </span><span class="k">from</span><span class="w"> </span><span class="n">user_free_space</span></span>&#10;<span class="code-line"><span class="k">group</span><span class="w"> </span><span class="k">by</span><span class="w"> </span><span class="n">tablespace_name</span></span></code></pre>
 </li>
</ol>

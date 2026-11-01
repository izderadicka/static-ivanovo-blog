+++
title = "Not Always PyPy Is Faster"
path = "/not-always-pypy-is-faster/"
date = "2014-09-05T07:43:43"
include_in_feeds = true
[extra]
wordpress_id = 860
kind = "post"
node_key = "860"
author = "admin"
source_url = "http://zderadicka.eu/not-always-pypy-is-faster/"
source_guid = "http://zderadicka.eu/?p=860"
source_date_gmt = "2014-09-05 06:43:43"
[taxonomies]
category = ["Admin", "Programming"]
tag = ["python"]
+++
[PyPy](http://pypy.org/) is an alternative Python interpreter, which is known for it's speed.  However it does not have to be always faster as 'classic' Python interpreter (called here CPython). For one small project of mine - [PDF Checker](https://github.com/izderadicka/pdf-checker) \- I was testing PyPy hoping to speed up PDF document processing (basically parsing to extract text - [pdfminer](http://www.unixuser.org/~euske/python/pdfminer/) library is used and document parsing takes majority of time).  Below are results from running program for two different files and in CPython interpreter or in PyPy (with JIT and without JIT compilation):


<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table style="font-size: 110% !important;">
<tbody>
<tr>
<td></td>
<td>CPython</td>
<td>PyPy</td>
<td>PyPy with JIT disabled</td>
</tr>
<tr>
<td>Small PDF (110kB)</td>
<td> 1.1 s</td>
<td> 2.4 s</td>
<td> 2.5 s</td>
</tr>
<tr>
<td>Big PDF (996kB)</td>
<td> 16.6 s</td>
<td> 10.9 s</td>
<td> 36.5 s</td>
</tr>
</tbody>
</table></div>


<span id="more-860"></span>

Clearly for smaller file CPython is notably faster - about 2x. I assume that overhead of JIT is not payed off by achieved speed up.  This starts to show off only for larger files.

Tested with CPython 2.7.6 , PyPy 2.3.1   on Linux (Ubuntu 14.04  64 bit) with Intel Core i5 CPU @ 2.7 GHz and 8GB memory.

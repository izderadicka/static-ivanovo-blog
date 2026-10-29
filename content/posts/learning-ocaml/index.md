+++
title = "Learning OCAML"
path = "/learning-ocaml/"
date = "2014-04-28T13:34:03"
include_in_feeds = true
[extra]
wordpress_id = 782
kind = "post"
node_key = "782"
author = "admin"
source_url = "http://zderadicka.eu/learning-ocaml/"
source_guid = "http://zderadicka.eu/?p=782"
source_date_gmt = "2014-04-28 12:34:03"
categories = ["Programming"]
tags = ["OCaml"]
+++
I decided to increase my perspective in programming and this time to look at some functional language.  Functional languages are here for quite some time,  but never got into mainstream, however recently they are getting more popular.   And some features from functional programming made their way into other languages (first class functions, closures, higher order functions, ... ), so I was curious  to learn a bit more of functional programming. For my exercise I decided to try <a href="http://ocaml.org/">OCAML</a>.
<span id="more-782"></span>


## Why OCAML


OCAML might look as bit obscure language at first look -   (in <a href="http://www.tiobe.com/index.php/content/paperinfo/tpci/index.html">TIOBE</a> index on 50th place), but I've learned few nice things, about it, which convinced me to give it a try:


<ul>
<li>Works well in Linux (which is my primary platform) and  compiles to native code, but it is multi-platform  (compiles on Mac, Win ...). Thanks to compilation to native code OCAML programs can provide good performance.</li>
<li>OCAML is a  base for F# - in fact, with some limitation F# should be able to compile OCAML source.   F# is becoming more and more popular,  so I guess knowledge of ML family language could be useful.</li>
<li>It's said that OCAML has all that is considered essential for true functional programming,  but also has provision for imperative and OO programming, which can be used where it's necessary for program efficiency.</li>
<li>OCAML is learned as universities at advanced programming courses about functional programming.   (for instance at Cornell - <a href="http://www.cs.cornell.edu/courses/CS3110/2014sp/course_info.php">this course</a> and <a href="http://www.cs.cornell.edu/courses/CS6110/2014sp/info.asp">this course</a>)</li>
<li>OCAML was criticized for rather limited standard library and lack of libraries for many common tasks,  but this has changed with availability  <a href="https://opam.ocaml.org/">OPAM </a>- an excellent package manager for OCAML. Many packages are available there including <a href="http://janestreet.github.io/">JaneStreet Core</a> - extended and improved alternative to OCAML standard library.</li>
</ul>




## Learning Resources


Many resources are available online - many for free - you can check them  <a href="http://ocaml.org/learn/books.html">here</a> or <a href="http://index.relegant.com/ocaml/">here</a> or <a href="http://mirror.ocamlcore.org/wiki.cocan.org/training.html">here.</a>

I've chosen to use <a href="https://realworldocaml.org/">Real World OCaml</a> book, which is practical book using Janestreet Core library from beginning and is available online <span style="text-decoration: underline;">for free</span>.  The only thing I was missing there were exercises, because the only way how to learn programming language is to write code and before one is ready to jump into some bigger project some well designed exercises are invaluable.   So I complement reading  this book with exercises from Cornell's university <a href="http://www.cs.cornell.edu/Courses/cs3110/2011sp/lecturenotes.asp">"Data Structures and Functional Programming</a>"  (I've chosen older semester, but also newer semesters are are available).


## Setting Environment


Basically I followed <a href="https://github.com/realworldocaml/book/wiki/Installation-Instructions">this instructions</a> (from the book site),  just be sure to follow all details, especially:


<ul>
<li>Add opam configuration to <code>.bashrc</code>  (this can be chosed during <code>opam init</code>) and restart shell</li>
<li>Set <code>&#126;/.ocamlinit</code>  as described there</li>
</ul>


As Editor I do prefer Eclipse, so there are basically two options:

<a href="http://ocamldt.free.fr">ODT</a> \- OCaml Development Tools - this Eclipse plugin is recommended in the instructions
<a href="http://www.algo-prog.info/ocaide/">OcaIDE</a> \- this is alternative plugin,   seems to have more features then ODT,  this one I've chosen for now. But there are some challenges to make it work with Core and OPAM packages.

In order for OcaIDE to work, Eclipse must be started from environment , where some variables are set -   I use this script to start eclipse:


```sh
#!/bin/bash
# OPAM configuration
. /home/ivan/.opam/opam-init/init.sh > /dev/null 2> /dev/null || true

/opt/eclipse/eclipse $@ &

```


In Eclipse project create project OCAML Project (ocamlbuild),   in project properties set Project/Other Flags:


```sh
-use-ocamlfind -classic-display -syntax camlp4o -pkg core,core_bench,str 
-pkg sexplib.syntax,comparelib.syntax,fieldslib.syntax,variantslib.syntax 
-pkg bin_prot.syntax 
-tag thread -tag debug -tag annot -tag bin_annot -tag short_paths 
-cflags "-w A-4-33-40-41-42-43-34-44" -cflags -strict-sequence
```


This will basically build code same way as `corebuild` script.   For any additional libraries you need add -pkg option.

However I still have <strong>problems with OcaIDE</strong> \-  code completion and  functions help are working only for OCaml standard library, I did not find way how to make them work for Core.Std or for any additional library.   In debugging Variables view is not working if additional libraries are involved.    If anybody has experiences with OcaIDE and know how to get additional/alternative libraries here in play, please let me know.

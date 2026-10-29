+++
title = "Ocaml, Ocsigen, I Ching and Web Applications"
path = "/ocaml-ocsigen-i-ching-and-web-applications/"
date = "2015-01-01T15:06:49"
include_in_feeds = true
[extra]
wordpress_id = 958
kind = "post"
node_key = "958"
author = "admin"
source_url = "http://zderadicka.eu/ocaml-ocsigen-i-ching-and-web-applications/"
source_guid = "http://zderadicka.eu/?p=958"
source_date_gmt = "2015-01-01 14:06:49"
categories = ["Programming"]
tags = ["divination", "OCaml", "ocsigen", "web framework"]
+++
Reading recently great <a href="http://en.wikipedia.org/wiki/Philip_K._Dick">Philip K Dick </a>novel <a href="http://en.wikipedia.org/wiki/The_Man_in_the_High_Castle">The Man in the High Castle</a> I learned about <a href="http://en.wikipedia.org/wiki/I_Ching">I Ching </a>\- ancient Chinese philosophical, cosmological, but mainly divination text. I'm no big fan of divination, so in case of I Ching I would generally agree with <a href="http://www.csicop.org/si/show/whats_wrong_with_the_i_ching_ambiguity_obscurity_and_synchronicity/">this critical review</a>.  However the procedure of divination used within I Ching is quite interesting - <a href="http://en.wikipedia.org/wiki/I_Ching#Hexagrams">hexagrams</a> actually represent one of oldest binary codes.  Idea that one's fortune could be represented by 6 bits (actually it's 12 bits, because for practical divination purpose we use 6 x 4 states) is quite amusing.   So I decided to create online I Ching application as an exercise to learn bit more about <a href="http://ocsigen.org">Ocsigen</a> web framework.  You can check result of my effort <a href="http://iching.zderadicka.eu">here</a>. <span id="more-958"></span>


## Why Ocsigen


I have been playing with OCaml for some time and I was wondering what web frameworks are available there.   Ocsigen is probably most popular,  it's fairly stable, with reasonable documentation,  so I decided to give it a try. Ocsigen is actually a set of projects -   the application server is called Eliom (this is a core for writing web apps),  web server is Ocsigenserver, library for generating HTML is TyXML, etc.

Ocsigen/Eliom has several quite unique features -  the most notable one is that even client (browser) side of application is written in OCaml. Thanks to sub-project <a href="http://ocsigen.org/js_of_ocaml/">Js_of_Ocaml</a>, which provides compiler and runtime to compile and run Ocaml bytecode in browser JS engine.  That sounds  freaky enough to bring my attention.


## How does it feel?


Ocsigen/Eliom is definitely not very easy framework to start with.   Especially for me, while I'm still OCaml beginner,  it was notable effort.  Comparing  it, for instance, with python <a href="http://flask.pocoo.org/">Flask</a>,  which I used recently for some other project (<a href="/projects/python/pdf-checker/" title="PDF Checker">PDF Checker</a>), Eliom required much more time to learn.   With Flask I just read quickly through docs for an hour  and was ready to start and during project never hit an issue, which could not be resolve quickly (provided that I have <a href="https://www.djangoproject.com/">Django</a> background from several other projects).  Eliom I started with few official tutorials and initially  I did not have much idea what I was doing.  I slso had to read thoroughly through docs to grasp key concepts.

Eliom is approaching web development from little bit different perspective,  but when I finally got most of it, I have to say it make very much sense and it's well and carefully designed.

Key surprises for me were:


<ul>
<li><strong>Everything is typed</strong> - even Javascript and HTML (e.g. their respective OCaml libraries)-   for me working mostly with dynamically typed web frameworks that was new experience. It took me some time to get used to it and there is always overhead to use correct types and convert between types. On the other hand all the advantages of static typing are available for all the code - from beginning till the end.
Sometime it was bit struggle to get something right - for instance this JS code
<pre class="code-highlight" data-language="javascript"><code><span class="code-line"><span class="nb">document</span><span class="p">.</span><span class="nx">getElementById</span><span class="p">(</span><span class="s2">&quot;hexa_&quot;</span><span class="o">+</span><span class="nx">no</span><span class="p">).</span><span class="nx">value</span><span class="w"> </span><span class="o">=</span><span class="w"> </span><span class="nx">value</span></span></code></pre>
Has this equivalent in OCaml:
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="nb">let</span><span class="w"> </span><span class="nv">input</span><span class="w"> </span><span class="o">=</span><span class="w"> </span>Js.coerce_opt<span class="w"> </span><span class="o">(</span>Dom_html.document##getElementById<span class="o">(</span>Js.string<span class="o">(</span>Printf.sprintf<span class="w"> </span><span class="s2">&quot;hexa_%d&quot;</span><span class="w"> </span>no<span class="o">)))</span></span>&#10;<span class="code-line"><span class="w">		     </span>Dom_html.CoerceTo.input<span class="w"> </span><span class="o">(</span>fun<span class="w"> </span>_<span class="w"> </span>-&gt;<span class="w"> </span>assert<span class="w"> </span><span class="nb">false</span><span class="o">)</span><span class="w"> </span><span class="k">in</span></span>&#10;<span class="code-line"><span class="w">	</span>input##value<span class="w"> </span>&lt;-<span class="w"> </span><span class="o">(</span>Js.string<span class="w"> </span><span class="o">(</span>string_of_int<span class="w"> </span>value<span class="o">))</span><span class="p">;</span></span></code></pre>
 </li>
<li><strong>No HTML templates</strong> -  Eliom does not have HTML templates.  At first I could not believe that there could be a web framework without templates,  but then I learned that Eliom has other ways -  functional constructors and syntax extension.  When I got used to it, it was not so bad :-).</li>
<li><strong>Mixing server and client code together </strong> - Eliom provides some syntax extensions to mix together code for server and client -  initially I was bit confusing and syntax felt bit messy,  but it was easy to get used to it.</li>
<li><strong>Cooperative multitasking programming </strong>-  actually it was not so big surprise, because I used OCaml <a href="https://janestreet.github.io/guide-async.html">Async</a> library in my <a href="https://github.com/izderadicka/mapred">other learning project</a> and Eliom is using <a href="http://ocsigen.org/lwt/2.4.3/manual/">Lwt</a> library, which is quite similar in concept (monadic interface to asynch programming). As you probably know OCaml executes in one physical thread, because there is a global lock for garbage collector (similar to python GIL). Eliom in order to enable efficient concurrency uses Lwt library for cooperative multitasking (similar concept to  gevent or asyncio in python).  This requires special programming style, which has to be used in all application and usage of blocking IO operations or some other libraries that potentially block calls for significant time should be generally prevented.</li>
<li><strong>No I18N support</strong> -  that was really missed.  Ocaml provides a gettext library, but it'll require additional effort to use it together with Eliom (I rather hacked some small custom I18N functionality for my app).</li>
</ul>




## Cool Stuff


Apart of some initial troubles, described above,  I found some Eliom features that are really great and unique in world of web programming ( at least to me):


<ul>
<li><strong>Functional Reactive Programming</strong> - Eliom implements FRP on client side - where signals can be connected to content of HTML elements and also provides means to send signals and events between client and server.  For instance you can have a signal updated on server and it's value is displayed  as text in a HTML element in client.  It feels so right and elegant! In my I Ching application FRP and signals are used for Yin-Yang counter and progress bar.</li>
<li><strong>Client-server communication</strong>  -  Eliom provides several sophisticated ways for client - sever communication, like buses, channels and before mentioned reactive signals.  It enables to create highly interactive web application ( check  <a href="http://ocsigen.org/tuto/4.0/manual/application">tutorial for cooperative drawing web application</a>).</li>
<li><strong>Continuations based web programming -</strong>  I'm not big expert in this area, so just my two cents.  Technically spoken Eliom is not working with continuations,  but it provides  similar functionality by enabling dynamic creation of new web services/handlers from within running web service/handler, where new dynamic service is provided a closure to running environment. This  enables easy creation of different types of wizard- like interactions.  I did not have time to play with it yet,  but I think it can have great potential.</li>
</ul>




## My I Ching application


There are tons of I Ching applications around (especially for mobiles), so this one probably will not be any break-through.   However it stands solid in comparison with others (I made some small research). Notable features are:


<ul>
<li>Full I Ching oracle -   provides both current and future hexagrams and moving lines.  Text is based on most popular Richard Wilhelm translation of I Ching.</li>
<li>PRNG used for coins throws is seeded from data generated by user actions (mouse moves) -  to best simulate real throwing of coins ( shake, then throw).</li>
<li>Responsible interface design - works well on desktop browsers or  mobiles.</li>
<li>Can be easily localized. (Now English and  Czech, volunteers for translations are welcomed).</li>
</ul>


Code is available <a href="https://github.com/izderadicka/iching">on github</a>.
Online version is <a href="http://iching.zderadicka.eu">here</a>. (retry couple times if you get 503 error because container might be down)

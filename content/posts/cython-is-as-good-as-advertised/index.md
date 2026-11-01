+++
title = "Cython Is As Good As Advertised"
path = "/cython-is-as-good-as-advertised/"
date = "2016-02-01T12:43:19"
include_in_feeds = true
[extra]
wordpress_id = 1229
kind = "post"
node_key = "1229"
author = "admin"
source_url = "http://zderadicka.eu/cython-is-as-good-as-advertised/"
source_guid = "http://zderadicka.eu/?p=1229"
source_date_gmt = "2016-02-01 11:43:19"
[taxonomies]
category = ["Programming"]
tag = ["cython", "numeric calculations", "python"]
+++
I've have been aware of [Cython](http://cython.org/) for a few years but newer had chance to really test it in practice (apart of few dummy exercises).  Recently I've decided to look at it again and test it on my old project [adecapcha](/decoding-audio-captchas-in-python/). I was quite pleased with results, where I was able speed up the program significantly with minimum changes to the code.<span id="more-1229"></span>

I used following **approach** to improve the app performance with Cython:


<ol>
<li>Profile the application (or it's part) -  with [cProfile](https://docs.python.org/2/library/profile.html) and [gprof2dot](https://github.com/jrfonseca/gprof2dot) to give nice graphical view of computing time split across functions. (Alternatively you can use  [pyvmmonitor](http://www.pyvmmonitor.com/), which nicely integrates with PyDev or PyCharms).  Below is the profiling result of adecaptcha before Cython optimalization:
<a href="/wp-content/uploads/original.png"><img alt="original" class="alignnone wp-image-1231 size-medium" decoding="async" height="300" loading="eager" sizes="(max-width: 211px) 100vw, 211px" src="/wp-content/uploads/original-211x300.png" srcset="/wp-content/uploads/original-211x300.png 211w, /wp-content/uploads/original-720x1024.png 720w, /wp-content/uploads/original.png 833w" width="211"/></a>
Here we can see two branches, which took majority on program time - one is for loading audio file, but it's spending most of its time in Python standard module wave (scipy.io provides faster alternative, but not compatible with all wav files) .  However the second branch is completely  under our control.  We can see that a lot of time is spent in <code>twin</code> and <code>wf</code> functions ( triangular window calculations).</li>
<li>Let's look at functions identified by profiling:
<pre class="code-highlight" data-language="python"><code><span class="code-line"><span class="k">def</span> <span class="nf">twin</span><span class="p">(</span><span class="n">start</span><span class="p">,</span><span class="n">stop</span><span class="p">):</span></span>&#10;<span class="code-line">    <span class="k">def</span> <span class="nf">wf</span><span class="p">(</span><span class="nb">len</span><span class="p">):</span></span>&#10;<span class="code-line">        <span class="k">for</span> <span class="n">n</span> <span class="ow">in</span> <span class="n">xrange</span><span class="p">(</span><span class="nb">len</span><span class="p">):</span></span>&#10;<span class="code-line">            <span class="k">yield</span> <span class="mf">1.0</span> <span class="o">-</span> <span class="n">np</span><span class="o">.</span><span class="n">abs</span><span class="p">(((</span><span class="nb">len</span><span class="o">-</span><span class="mi">1</span><span class="p">)</span><span class="o">/</span><span class="mf">2.0</span> <span class="o">-</span><span class="n">n</span><span class="p">)</span><span class="o">/</span> <span class="p">((</span><span class="nb">len</span><span class="p">)</span><span class="o">/</span><span class="mf">2.0</span><span class="p">))</span></span>&#10;<span class="code-line">            </span>&#10;<span class="code-line">    <span class="nb">len</span><span class="o">=</span><span class="n">stop</span><span class="o">-</span><span class="n">start</span></span>&#10;<span class="code-line">    <span class="k">return</span> <span class="n">np</span><span class="o">.</span><span class="n">array</span><span class="p">(</span><span class="nb">list</span><span class="p">(</span><span class="n">wf</span><span class="p">(</span><span class="nb">len</span><span class="p">)))</span></span></code></pre>
This is obviously not very efficient code (could be marginally optimized by using list comprehension expression - but performance will be approximately the same  -  24% of total time vs 27%).</li>
<li>To introduce significant performance change we have to implement this function in Cython:
<pre class="code-highlight" data-language="python"><code><span class="code-line"><span class="n">cdef</span> <span class="n">extern</span> <span class="kn">from</span> <span class="s2">&quot;math.h&quot;</span><span class="p">:</span></span>&#10;<span class="code-line">    <span class="n">double</span> <span class="n">fabs</span><span class="p">(</span><span class="n">double</span> <span class="n">x</span><span class="p">)</span></span>&#10;<span class="code-line">    </span>&#10;<span class="code-line"><span class="n">ctypedef</span> <span class="n">np</span><span class="o">.</span><span class="n">double_t</span> <span class="n">DTYPE_t</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="k">def</span> <span class="nf">twin</span><span class="p">(</span><span class="n">start</span><span class="p">,</span> <span class="n">stop</span><span class="p">):</span></span>&#10;<span class="code-line">    <span class="n">cdef</span><span class="p">:</span> </span>&#10;<span class="code-line">        <span class="n">np</span><span class="o">.</span><span class="n">ndarray</span><span class="p">[</span><span class="n">DTYPE_t</span><span class="p">]</span> <span class="n">arr</span></span>&#10;<span class="code-line">        <span class="nb">int</span> <span class="n">n</span></span>&#10;<span class="code-line">        <span class="nb">int</span> <span class="nb">len</span><span class="o">=</span><span class="n">stop</span><span class="o">-</span><span class="n">start</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line">    <span class="n">arr</span><span class="o">=</span><span class="n">np</span><span class="o">.</span><span class="n">zeros</span><span class="p">(</span><span class="nb">len</span><span class="p">)</span></span>&#10;<span class="code-line">    <span class="k">for</span> <span class="n">n</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="nb">len</span><span class="p">):</span></span>&#10;<span class="code-line">        <span class="n">arr</span><span class="p">[</span><span class="n">n</span><span class="p">]</span><span class="o">=</span> <span class="mf">1.0</span> <span class="o">-</span> <span class="n">fabs</span><span class="p">(((</span><span class="nb">len</span><span class="o">-</span><span class="mi">1</span><span class="p">)</span><span class="o">/</span><span class="mf">2.0</span> <span class="o">-</span><span class="n">n</span><span class="p">)</span><span class="o">/</span> <span class="p">(</span><span class="nb">len</span><span class="o">/</span><span class="mf">2.0</span><span class="p">))</span></span>&#10;<span class="code-line">    <span class="k">return</span> <span class="n">arr</span></span></code></pre>
As you can see the changes are minimal, we just reimplemented twin function, this time with statically typed loop control variable and numpy array.</li>
<li>Profile again to see changes:
<a href="/wp-content/uploads/optimized.png"><img alt="optimized" class="alignnone wp-image-1233 size-medium" decoding="async" height="300" loading="lazy" sizes="(max-width: 185px) 100vw, 185px" src="/wp-content/uploads/optimized-185x300.png" srcset="/wp-content/uploads/optimized-185x300.png 185w, /wp-content/uploads/optimized-631x1024.png 631w, /wp-content/uploads/optimized.png 805w" width="185"/></a>
As you can see <code>twin</code> function is not an issue any more ( all <code>calc&#95;mfcc</code> branch is now basically spend in FFT calculation).</li>
</ol>


Cython can be also used to create Python bindings to C and C++ libraries.  Although the interface has to be written manually (while some other tools like [SWIG](http://www.swig.org/) can generate it automatically) and it requires some  effort,  on the other hand it forces authors to think about the interface design  and it can result in very nice 'pythonic' interfaces, which can save you a lot of time later. Key insight here is that  we do not need to interface all functions and classes in C  or C++ library, but only those, which are important for our needs.  Recently I've created a [binding](https://github.com/izderadicka/pdfparser) to [libpoppler](https://poppler.freedesktop.org/) (PDF parsing library) and found this task fairly easy and quite enjoyable to do.


## Conclusions


Even with few very simple changes into original code I was able to achieve significant performance improvements (run time 0.27s vs 0.41s - for one audio captcha, that's app. 35 % improvement).
Programming in Cython is relatively easy so I was able to implement these changes quickly, without particular issues.  Complication errors were fairly well described, so I was able to fix problems quickly. Building can be defined in setup.py in a straightforward manner or can be even automatic ( with [pyximport](http://docs.cython.org/src/reference/compilation.html#compiling-with-pyximport) \- however pyximport machinery takes some time - so for smaller programs manual compilation is more effective).

However it has to be said that not always path to performance improvements with Cython is so straightforward.  In another project ( [Voronoi diagram in bounded box](/voronoi-diagrams/) a part of [myplaces](/projects/python/myplaces/) project) I've tried too and I was not able to achieve any performance gain ( quite opposite cythonized version  was about 30% slower). I probably should  try harder, but obviously sometimes it's difficult to achieve required improvements.

Cython can be also used to create nice pythonic interfaces to existing C and C++ libraries.

Overall I was quite **impressed** and looking forward to use Cython in future projects.

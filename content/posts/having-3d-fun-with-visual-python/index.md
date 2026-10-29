+++
title = "Having 3D fun with  Visual Python"
path = "/having-3d-fun-with-visual-python/"
date = "2012-09-24T19:30:28"
include_in_feeds = true
[extra]
wordpress_id = 139
kind = "post"
node_key = "139"
author = "admin"
source_url = "http://zderadicka.eu/having-3d-fun-with-visual-python/"
source_guid = "http://zderadicka.eu/?p=139"
source_date_gmt = "2012-09-24 18:30:28"
categories = ["Programming"]
tags = ["3D", "linux", "physics", "python", "simmulation"]
+++
<a href="http://www.vpython.org">Visual Python or vpython</a> is python library for simple 3D animation, especially useful for animation of  simple physical scenes - like pendulum, ball on a spring, movement in gravitational field etc.  It is fairly simple to use and gives quite nice animations, which can demonstrate some  laws of physics.  I actually spot this package, when I saw an article about physics in popular mobile game "Angry Birds - Space". In that article they had been arguing about physics laws in the game and also referred to  vpython, where they made some experiments. I told myself I have to try it myself, so I've created small program using vpython.<span id="more-139"></span>

The <a href="https://github.com/izderadicka/vpython-scripts/blob/master/angry.py">program is here</a> and simulates movement of a ball within gravitational field of a planet, where also atmosphere friction is present . Below is a video from program run:

<a href="/wp-content/uploads/o_vpython.mp4">video_vpython</a>


<video controls="" preload="metadata"><source src="/wp-content/uploads/o_vpython.mp4" type="video/mp4"/><source src="/wp-content/uploads/vpython.webm" type="video/webm"/></video>




### Install Visual Python


Although there is package <em>python-visual</em> in Ubuntu repositories, this package is  fairly ancient and is missing latest features - like tracking of movement etc. So if you want to have most of vpython you should install latest version from sources, however process is not completely straight forward (as authors themselves admit), so I'm recording here for reference my steps(On linux Mint 13/ Ubuntu 12.04):


<ol>
<li>Download source from <a class="download" href="http://www.vpython.org/contents/download_linux.html">http://www.vpython.org/contents/download_linux.html</a></li>
<li>Unpack</li>
<li>Install dependencies - libraries:
<code>sudo apt-get install automake libgtkmm-2.4-dev libglademm-2.4-dev libgtkglextmm-x11-1.2-dev  libboost-dev libboost-python-dev libboost-thread-dev libboost-signals-dev</code></li>
<li>Install also some depended python packages that are not in repository:
<ol>
<li> FontTools - should be installed manually, easy_install does not find them
download from<a href=" http://sourceforge.net/projects/fonttools/files/latest/download"> http://sourceforge.net/projects/fonttools/files/latest/download</a>
unpack and install - <code>sudo python setup.py install</code></li>
<li>ttfquery - <code>sudo easy&#95;install ttfquery</code></li>
<li>Polygon -  again manually, because easy_install get version for python 3.
download from <a href="https://github.com/jraedler/Polygon2/zipball/master">https://github.com/jraedler/Polygon2/zipball/master</a>
unpack and install - <code>sudo python setup.py install</code></li>
</ol>
</li>
<li>In vpython directory run:
<code>./configure</code>
<code>make</code>
<code>sudo make install</code></li>
<li>However install scripts installs package to /usr/local/lib/python2.7/site-packages,  which is not on python path by default, so we have move them (or modify python path):
<code>sudo mv /usr/local/lib/python2.7/site-packages/vis  /usr/local/lib/python2.7/dist-packages/</code>
<code>sudo mv /usr/local/lib/python2.7/site-packages/visual/  /usr/local/lib/python2.7/dist-packages/</code></li>
<li>Run python, try <code>import visual</code> to see that all works</li>
</ol>

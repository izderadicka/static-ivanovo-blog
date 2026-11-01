+++
title = "Media Server For Music And Audio-Books"
path = "/media-server-for-music-and-audio-books/"
date = "2015-09-28T14:00:26"
include_in_feeds = true
[extra]
wordpress_id = 1103
kind = "post"
node_key = "1103"
author = "admin"
source_url = "http://zderadicka.eu/media-server-for-music-and-audio-books/"
source_guid = "http://zderadicka.eu/?p=1103"
source_date_gmt = "2015-09-28 13:00:26"
[taxonomies]
category = ["Admin", "Tools"]
tag = ["media server", "music"]
+++
<a href="/wp-content/uploads/music-7.png"><img alt="music-7" class="size-full wp-image-1117 alignleft" decoding="async" height="128" loading="eager" src="/wp-content/uploads/music-7.png" width="128"/></a>Having updated my mobile  recently (but still staying on Android) to [4G](https://en.wikipedia.org/wiki/4G) device, I thought that it would be about time to make my audio collection available outside of home network.  At home I use [samba](https://www.samba.org/) share, which is quite fine for most of uses, however enabling access from internet required bit more  effort. In following article I'd like to describe options, I've been looking at, and the final solution.<span id="more-1103"></span>


## My requirements:




<ul>
<li>Should be able to handle large collections</li>
<li>Browse by directory structure (my metadata tags are messy)</li>
<li>Clearly separate audio books from music</li>
<li>Some search would be nice</li>
<li>Preferably open source (at least server part)</li>
<li>Linux indeed</li>
<li><span style="text-decoration: underline;">Reliable</span> playback over Internet on mobile</li>
<li>Smart caching on mobile, enabling temporal break-outs in connectivity ( the underground etc.)</li>
<li>Possibility to load content for offline playback</li>
<li>Should be reasonably secure</li>
</ul>




## Options:




## **Some Cloud Storage**


It was not really option for me.  I do not want cloud service for this.


## ASUS AI Cloud


As I'm using ASUS router[ ASUS AiCloud](http://www.asus.com/AiCloud/) is one option. If AiCloud is enabled on router, then Android  application can be used to provide access to all LAN shared disks (SMB).  Additionally there is some support for media playback.
I used it for a while, have some issues with android client, which moved me to look for other solution:



- Unstable - when connection is lost, playback in the client freezes and is not able to continue, when connection is re-established. All application has to be closed and restarted.
- Just current item is cached, so it can not  get over longer connection drop outs
- General quality - player interface is ugly,  resumes from paused state after each incoming call etc.





## SFTP And ES File Explorer


At home I use excellent [ES File Explorer](http://www.estrongs.com/?lang=en) to access shares and it has also SFTP support.
I can access my server via SSH already, so only trick was to enable public/private key use in ES - and it's very easy - openssh generated key can be used in ES.
However SFTP does not seem to be good for media playback,  it looks like  whole file must be downloaded, before playback starts. Also SFTP seems to be unstable when connection is switched between mobile and WiFi, or it's unavailable for a short while.

ES also enables WebDAV remote shares, I did not try them yet, maybe they can be better suited for media then SFTP?


## ownCloud


ownCloud is PHP application for accessing and synchronizing of  files across different  devices. It is written in PHP. For music streaming it's using Ampache,  which can be also used as standalone solution, so as media solution ownCloud does not provide anything interesting. See details of Ampache below.


## Media Servers


So finally I've looked at specialized media servers.   Based on different articles I considered: [Emby](http://emby.media/), [Plex](https://plex.tv/), [Serviio](http://serviio.org/), [UMS](http://www.universalmediaserver.com), [Subsonic](http://www.subsonic.org/pages/index.jsp)/[Madsonic](http://beta.madsonic.org/pages/index.jsp)/[Libresonic](https://github.com/Libresonic/libresonic) /[Airsonic](https://airsonic.github.io/) and [Ampache](http://ampache.org).

**Emby **(former Media Explorer) is an open source project. However the music handling does not suite my needs. Music is sorted only by metatags, which causes problems and music and audio-books are messed together.

**Plex** \- is not an open source. It has good references,  but to enable access over Internet one must register it with their Plex service, which meant hard stop for me, because I'd like to have completely independent solution.

**Serviio** \- is not an open source, so I did not try it.

**UMS** \- is focused only on LAN environment (using DLNA), but I need mainly internet access.

**Subsonic** \- is  media server written in Java. It was open source, but turned to closed source some time ago. It focuses on music and it best met my requirements.  It basically sticks to the way how music is organize in the file system, which is absolutely crucial for me, provides super-fast scanning of music directories and also nice Android applications are available (Subsonic, Ultrasonic ...), which provide smart caching (you can choose how many songs ahead should be  cached in current play list, so you can easily survive some time without connection) and also it very easy to load content to mobile local storage.  Overall it works quite well, however installation required few tweaks - as described below.

**Libresonic **\- is recent Subsonic clone - (based on KANG 5.3 version of Subsonic). Libresonic is addressing fact that recent versions of Subsonic (from version 6) are not open sourced any more. Currently Libresonic seems to be abandoned - no commit in more that half year - looks like active  development moved to Airsonic - see below.

**Airsonic** \- is another Subsonic clone - actually fork of Libresonic, after some developers decided to follow bit different path. Recently it looks much more active than  Libresonic, new features have been added ( like true HTML player). Community is active, responding to issues while Libresonic project seems to be stalled now.

**Madsonic** \-  is Subsonic clone.  It removes dubious shareware like limitations in the program and adds new functionality.  However the interface looks more confusing and the new functions have not been  of interest to me, so I rather stayed with Subsonic (or to be exact it's clone which removes the trial limitations - see below).

<a href="http://booksonic.org">**Booksonic**</a> \- it's another subsonic clone - focused on audiobooks -  however [last commit](https://github.com/popeen/Popeens-Subsonic) is more then a year ago, so it does not seem to have bright future - so for audiobooks I rather followed my own way as explained below ([audioserve](/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/)).

**Ampache** \- open source, PHP server. Installs smoothly to regular LAMP environment. Collection is organized  by metatags, so again no good option for me, it results in messy collection.  Just tried one Android client  Amdroid, which is quite bad - poor interface, alpha quality.


## My Choice


For me **subsonic was a clear winner**,  no other solution gets closer to meet my requirements. Some time ago I replaced subsonic with **libresonic **(which provides same functionality for me), because of subsonic code going to closed mode, and later  replaced it with  **airsonic**, because libresonic is development is stalled.
I particularly liked:



- You can browse media by directory structure (with some enhancements, which do not mind so much)
- Music and Audiobooks can be in separated collections - so it's easy to browse them
- Super fast scanning of music directories
- Smart caching on Android client



Some issues:



- Java is bit resources hungry - especially memory.
- Startup takes several minutes
- Handling of national chars in file names and tags is problematic
- Sorting of files within directory, if metadata/tags are not correct (android clients)
- Using of metadata instead of filename causes sometime problems, if metadata are not correct
- Security (only issue in recent libresonic,  airsonic has resolved them )
- [unauthenticated access to media](https://github.com/Libresonic/libresonic/issues/326) -  media and cover art is basically accessible to anybody. It's easy - for unauthenticated  user  (if he knows URL pattern)  to list and download all media
-[ passwords are stored  in cleartext](https://github.com/Libresonic/libresonic/issues/69)



As I was not completely happy with any solution - especially for audiobooks (for which airsonic is just too overcomplicated), I also started new project [audioserve](https://github.com/izderadicka/audioserve) \- to create super simple audiobooks server - check [this article](/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/). Now I'm using audioserve for audiobooks and airsonic for music - I found that's it easier to have separate solution for audiobooks, then rely on airsonic for this, especially as audioserve is very light weighted.


## Setting Up Libresonic


(airsonic is very similar - just replace libre with air)


<ol>
<li>Download latest release [from here](https://github.com/Libresonic/libresonic/releases).</li>
<li>I'm using this script to run libresonic (optionally could be deployed in [tomcat](http://tomcat.apache.org/)):
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="ch">#!/bin/sh</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="nv">LIBRESONIC_HOME</span><span class="o">=</span>/data/local/libresonic</span>&#10;<span class="code-line"><span class="nv">LIBRESONIC_HOST</span><span class="o">=</span><span class="m">0</span>.0.0.0</span>&#10;<span class="code-line"><span class="nv">LIBRESONIC_PORT</span><span class="o">=</span><span class="m">4040</span></span>&#10;<span class="code-line"><span class="nv">LIBRESONIC_CONTEXT_PATH</span><span class="o">=</span>/libresonic</span>&#10;<span class="code-line"><span class="nv">LIBRESONIC_MAX_MEMORY</span><span class="o">=</span><span class="m">512</span></span>&#10;<span class="code-line"><span class="nv">LIBRESONIC_PIDFILE</span><span class="o">=</span>/tmp/libresonic.pid</span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="c1"># was need in subsonic to handle unicode file names</span></span>&#10;<span class="code-line"><span class="nb">export</span><span class="w"> </span><span class="nv">LC_ALL</span><span class="o">=</span><span class="s2">&quot;en_US.UTF-8&quot;</span></span>&#10;<span class="code-line"><span class="nb">export</span><span class="w"> </span><span class="nv">LANG</span><span class="o">=</span><span class="s2">&quot;en_US.UTF-8&quot;</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="nv">kill</span><span class="o">=</span><span class="m">1</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line">usage<span class="o">()</span><span class="w"> </span><span class="o">&#123;</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">echo</span><span class="w"> </span><span class="s2">&quot;Usage: libresonic.sh [options]&quot;</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">echo</span><span class="w"> </span><span class="s2">&quot;  --help              Prints help.&quot;</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">echo</span><span class="w"> </span><span class="s2">&quot;  --kill		Kills running process&quot;</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">exit</span><span class="w"> </span><span class="m">0</span></span>&#10;<span class="code-line"><span class="o">}</span></span>&#10;<span class="code-line"><span class="c1"># Parse arguments.</span></span>&#10;<span class="code-line"><span class="k">while</span><span class="w"> </span><span class="o">[</span><span class="w"> </span><span class="nv">$#</span><span class="w"> </span>-ge<span class="w"> </span><span class="m">1</span><span class="w"> </span><span class="o">]</span><span class="p">;</span><span class="w"> </span><span class="k">do</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="k">case</span><span class="w"> </span><span class="nv">$1</span><span class="w"> </span><span class="k">in</span></span>&#10;<span class="code-line"><span class="w">        </span>--help<span class="o">)</span></span>&#10;<span class="code-line"><span class="w">            </span>usage</span>&#10;<span class="code-line"><span class="w">            </span><span class="p">;;</span></span>&#10;<span class="code-line"><span class="w">        </span>--kill<span class="o">)</span></span>&#10;<span class="code-line"><span class="w">            </span><span class="nv">kill</span><span class="o">=</span><span class="m">0</span></span>&#10;<span class="code-line"><span class="w">            </span><span class="p">;;</span></span>&#10;<span class="code-line"><span class="w">        </span>*<span class="o">)</span></span>&#10;<span class="code-line"><span class="w">            </span>usage</span>&#10;<span class="code-line"><span class="w">            </span><span class="p">;;</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="k">esac</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">shift</span></span>&#10;<span class="code-line"><span class="k">done</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="k">if</span><span class="w"> </span><span class="o">[</span><span class="w"> </span><span class="nv">$kill</span><span class="w"> </span><span class="o">=</span><span class="w"> </span><span class="m">0</span><span class="w"> </span><span class="o">]</span><span class="p">;</span><span class="w"> </span><span class="k">then</span></span>&#10;<span class="code-line"><span class="k">if</span><span class="w"> </span><span class="o">[</span><span class="w"> </span>-f<span class="w"> </span><span class="nv">$LIBRESONIC_PIDFILE</span><span class="w"> </span><span class="o">]</span><span class="p">;</span><span class="w"> </span><span class="k">then</span></span>&#10;<span class="code-line"><span class="nb">kill</span><span class="w"> </span><span class="sb">`</span>cat<span class="w"> </span><span class="nv">$LIBRESONIC_PIDFILE</span><span class="sb">`</span></span>&#10;<span class="code-line">rm<span class="w"> </span>-f<span class="w"> </span><span class="nv">$LIBRESONIC_PIDFILE</span></span>&#10;<span class="code-line"><span class="nb">exit</span><span class="w"> </span><span class="m">0</span></span>&#10;<span class="code-line"><span class="k">else</span></span>&#10;<span class="code-line"><span class="nb">echo</span><span class="w"> </span>Not<span class="w"> </span>running</span>&#10;<span class="code-line"><span class="nb">exit</span><span class="w"> </span><span class="m">0</span></span>&#10;<span class="code-line"><span class="k">fi</span></span>&#10;<span class="code-line"><span class="k">fi</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="c1"># Use JAVA_HOME if set, otherwise assume java is in the path.</span></span>&#10;<span class="code-line"><span class="nv">JAVA</span><span class="o">=</span>java</span>&#10;<span class="code-line"><span class="k">if</span><span class="w"> </span><span class="o">[</span><span class="w"> </span>-e<span class="w"> </span><span class="s2">&quot;</span><span class="si">$&#123;</span><span class="nv">JAVA_HOME</span><span class="si">}</span><span class="s2">&quot;</span><span class="w"> </span><span class="o">]</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="k">then</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nv">JAVA</span><span class="o">=</span><span class="si">$&#123;</span><span class="nv">JAVA_HOME</span><span class="si">}</span>/bin/java</span>&#10;<span class="code-line"><span class="k">fi</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="c1"># Create Libresonic home directory.</span></span>&#10;<span class="code-line">mkdir<span class="w"> </span>-p<span class="w"> </span><span class="si">$&#123;</span><span class="nv">LIBRESONIC_HOME</span><span class="si">}</span></span>&#10;<span class="code-line"><span class="nv">LOG</span><span class="o">=</span><span class="si">$&#123;</span><span class="nv">LIBRESONIC_HOME</span><span class="si">}</span>/libresonic_sh.log</span>&#10;<span class="code-line">rm<span class="w"> </span>-f<span class="w"> </span><span class="si">$&#123;</span><span class="nv">LOG</span><span class="si">}</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="nb">cd</span><span class="w"> </span><span class="k">$(</span>dirname<span class="w"> </span><span class="nv">$0</span><span class="k">)</span></span>&#10;<span class="code-line"><span class="k">if</span><span class="w"> </span><span class="o">[</span><span class="w"> </span>-L<span class="w"> </span><span class="nv">$0</span><span class="w"> </span><span class="o">]</span><span class="w"> </span><span class="o">&amp;&amp;</span><span class="w"> </span><span class="o">([</span><span class="w"> </span>-e<span class="w"> </span>/bin/readlink<span class="w"> </span><span class="o">]</span><span class="w"> </span><span class="o">||</span><span class="w"> </span><span class="o">[</span><span class="w"> </span>-e<span class="w"> </span>/usr/bin/readlink<span class="w"> </span><span class="o">])</span><span class="p">;</span><span class="w"> </span><span class="k">then</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">cd</span><span class="w"> </span><span class="k">$(</span>dirname<span class="w"> </span><span class="k">$(</span>readlink<span class="w"> </span><span class="nv">$0</span><span class="k">))</span></span>&#10;<span class="code-line"><span class="k">fi</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="si">$&#123;</span><span class="nv">JAVA</span><span class="si">}</span><span class="w"> </span>-Xmx<span class="si">$&#123;</span><span class="nv">LIBRESONIC_MAX_MEMORY</span><span class="si">}</span>m<span class="w"> </span><span class="se">\</span></span>&#10;<span class="code-line"><span class="w">  </span>-Dlibresonic.home<span class="o">=</span><span class="si">$&#123;</span><span class="nv">LIBRESONIC_HOME</span><span class="si">}</span><span class="w"> </span><span class="se">\</span></span>&#10;<span class="code-line"><span class="w">  </span>-Dserver.host<span class="o">=</span><span class="si">$&#123;</span><span class="nv">LIBRESONIC_HOST</span><span class="si">}</span><span class="w"> </span><span class="se">\</span></span>&#10;<span class="code-line"><span class="w">  </span>-Dserver.port<span class="o">=</span><span class="si">$&#123;</span><span class="nv">LIBRESONIC_PORT</span><span class="si">}</span><span class="w"> </span><span class="se">\</span></span>&#10;<span class="code-line"><span class="w">  </span>-Dserver.contextPath<span class="o">=</span><span class="si">$&#123;</span><span class="nv">LIBRESONIC_CONTEXT_PATH</span><span class="si">}</span><span class="w"> </span><span class="se">\</span></span>&#10;<span class="code-line"><span class="w">  </span>-Djava.awt.headless<span class="o">=</span><span class="nb">true</span><span class="w"> </span><span class="se">\</span></span>&#10;<span class="code-line"><span class="w">  </span>-verbose:gc<span class="w"> </span><span class="se">\</span></span>&#10;<span class="code-line"><span class="w">  </span>-jar<span class="w"> </span>libresonic.war<span class="w"> </span>&gt;<span class="w"> </span><span class="si">$&#123;</span><span class="nv">LOG</span><span class="si">}</span><span class="w"> </span><span class="m">2</span>&gt;<span class="p">&amp;</span><span class="m">1</span><span class="w"> </span><span class="p">&amp;</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="nv">rc</span><span class="o">=</span><span class="nv">$?</span></span>&#10;<span class="code-line"><span class="k">if</span><span class="w"> </span><span class="o">[</span><span class="w"> </span><span class="nv">$rc</span><span class="w"> </span><span class="o">=</span><span class="w"> </span><span class="m">0</span><span class="w"> </span><span class="o">]</span><span class="p">;</span><span class="w"> </span><span class="k">then</span></span>&#10;<span class="code-line"><span class="c1"># Write pid to pidfile if it is defined.</span></span>&#10;<span class="code-line"><span class="k">if</span><span class="w"> </span><span class="o">[</span><span class="w"> </span><span class="nv">$LIBRESONIC_PIDFILE</span><span class="w"> </span><span class="o">]</span><span class="p">;</span><span class="w"> </span><span class="k">then</span></span>&#10;<span class="code-line"><span class="w">    </span><span class="nb">echo</span><span class="w"> </span><span class="nv">$!</span><span class="w"> </span>&gt;<span class="w"> </span><span class="si">$&#123;</span><span class="nv">LIBRESONIC_PIDFILE</span><span class="si">}</span></span>&#10;<span class="code-line"><span class="k">fi</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="nb">echo</span><span class="w"> </span>Started<span class="w"> </span>Libresonic<span class="w"> </span><span class="o">[</span>PID<span class="w"> </span><span class="nv">$!</span>,<span class="w"> </span><span class="si">$&#123;</span><span class="nv">LOG</span><span class="si">}</span><span class="o">]</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="k">else</span></span>&#10;<span class="code-line"></span>&#10;<span class="code-line"><span class="nb">echo</span><span class="w"> </span>Something<span class="w"> </span>went<span class="w"> </span>wrong<span class="w"> </span>-<span class="w"> </span>ret.<span class="w"> </span>code<span class="w"> </span><span class="nv">$rc</span></span>&#10;<span class="code-line"><span class="k">fi</span><span class="w"> </span></span>&#10;</code></pre>
</li>
<li>Configure nginx as reverse proxy, assure https support in nginx (from Internet libresonic should be access only via encrypted connection).   For SSL certificate use [Let's Encrypt certification authority](https://letsencrypt.org/), which issues certificates for free - <code>certbot-auto run --nginx</code> work fine for me.
This is part of nginx configuration relevant for libresonic:
<pre class="code-highlight" data-language="sh"><code><span class="code-line">server<span class="w"> </span><span class="o">&#123;</span></span>&#10;<span class="code-line"><span class="w">    </span>location<span class="w"> </span>/libresonic<span class="w"> </span><span class="o">&#123;</span></span>&#10;<span class="code-line"><span class="w">	</span>proxy_set_header<span class="w"> </span>X-Real-IP<span class="w">         </span><span class="nv">$remote_addr</span><span class="p">;</span></span>&#10;<span class="code-line"><span class="w">      	</span>proxy_set_header<span class="w"> </span>X-Forwarded-For<span class="w">   </span><span class="nv">$proxy_add_x_forwarded_for</span><span class="p">;</span></span>&#10;<span class="code-line"><span class="w">      	</span>proxy_set_header<span class="w"> </span>X-Forwarded-Proto<span class="w"> </span>https<span class="p">;</span></span>&#10;<span class="code-line"><span class="w">      	</span>proxy_set_header<span class="w"> </span>X-Forwarded-Host<span class="w">  </span><span class="nv">$http_host</span><span class="p">;</span></span>&#10;<span class="code-line"><span class="w">      	</span>proxy_set_header<span class="w"> </span>Host<span class="w">              </span><span class="nv">$http_host</span><span class="p">;</span></span>&#10;<span class="code-line"><span class="w">      	</span>proxy_max_temp_file_size<span class="w">           </span><span class="m">0</span><span class="p">;</span></span>&#10;<span class="code-line"><span class="w">      	</span>proxy_pass<span class="w">                         </span>http://127.0.0.1:4040<span class="p">;</span></span>&#10;<span class="code-line"><span class="w">      	</span>proxy_redirect<span class="w">                     </span>http://<span class="w"> </span>https://<span class="p">;</span></span>&#10;<span class="code-line"><span class="w">	</span><span class="o">}</span></span>&#10;<span class="code-line"><span class="w">   </span>listen<span class="w"> </span><span class="m">443</span><span class="w"> </span>ssl<span class="p">;</span><span class="w"> </span><span class="c1"># managed by Certbot</span></span>&#10;<span class="code-line"><span class="w">   </span><span class="c1"># ... more ssl settings managed by Certbot</span></span>&#10;<span class="code-line"><span class="o">}</span></span></code></pre>
</li>
<li>Open port 443 in you route to access libresonic from Internet</li>
</ol>




## Setting Up Subsonic (outdated)




<ol>
<li>Install from [official site](http://www.subsonic.org/pages/download.jsp). I prefer stand alone installation, assuming others will be similar.</li>
<li>Replace .war file with one from [this fork](https://github.com/EugeneKay/subsonic). This one is patched to remove time limitation of some features.  (It's not crack - [subsonic is Open Source under GPLv3](http://sourceforge.net/projects/subsonic/),  so it's legitimate to create modified version as long as their source is available under compatible license).</li>
<li> Edit subsonic.sh (or /etc/default/subsonic  appropriately, if you installed package)
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="nv">SUBSONIC_HOME</span><span class="o">=</span>/data/local/subsonic</span>&#10;<span class="code-line"><span class="nv">SUBSONIC_PORT</span><span class="o">=</span><span class="m">0</span></span>&#10;<span class="code-line"><span class="nv">SUBSONIC_HTTPS_PORT</span><span class="o">=</span><span class="m">4043</span></span>&#10;</code></pre>
Enable https, disable http (but only if you will not use DLNA, it will not work without http port).  Set home directory (if different from default).</li>
<li>Also you need to assure that UTF-8 support is in place.  For this ensure that these  variables are set in subsonic environment:
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="nb">export</span><span class="w"> </span><span class="nv">LC_ALL</span><span class="o">=</span><span class="s2">&quot;en_US.UTF-8&quot;</span></span>&#10;<span class="code-line"><span class="nb">export</span><span class="w"> </span><span class="nv">LANG</span><span class="o">=</span><span class="s2">&quot;en_US.UTF-8&quot;</span></span>&#10;</code></pre>
Easiest way is to add them to subsonic.sh script ( or /etc/init.d startup script in packaged installation).
Without these variables subsonic will not recognize files with national characters in file name!</li>
<li>Subsonic comes with pre-packed SSL key and certificate for HTTPS - this is <span style="text-decoration: underline;">significant</span> security risk, if internet access is enabled. (Anybody can fetch private key from subsonic distribution and then decode your ssl trafic).  Generate new key+certificate and update <code>subsonic-booter-jar-with-dependencies.jar</code> as described [here](http://www.richgrundy.com/blog/setting-up-ssl-cert-for-subsonic/).
Self-signed certificate would be enough ( just add -x509 -days 3650 to openssl req command).</li>
<li>Enable port forwarding on your home router (either manually or in subsonic network setup enable UPnP NAT PMP</li>
<li>Run subsonic as non-root account</li>
</ol>

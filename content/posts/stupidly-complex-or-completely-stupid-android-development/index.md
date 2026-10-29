+++
title = "Stupidly Complex or Completely Stupid - Android Development"
path = "/stupidly-complex-or-completely-stupid-android-development/"
date = "2018-04-26T11:02:36"
include_in_feeds = true
[extra]
wordpress_id = 1852
kind = "post"
node_key = "1852"
author = "admin"
source_url = "http://zderadicka.eu/stupidly-complex-or-completely-stupid-android-development/"
source_guid = "http://zderadicka.eu/?p=1852"
source_date_gmt = "2018-04-26 10:02:36"
categories = ["Uncategorized"]
+++
As part of <a href="https://github.com/izderadicka/audioserve">audioserve</a> project I decided to create an Android client. To make this exercise more interesting I decided to write it in <a href="https://kotlinlang.org">Kotlin</a> language (see p<a href="/from-russia-with-love-kotlin-language/">revious article about Kotlin language</a>).  This client should provide roughly similar interface as web client (see <a href="/audioserve-audiobooks-server-stupidly-simple-or-simply-stupid/">this article</a> for web client interface demo), but I hoped to achieve much better caching features, which will enable to play smoothly even when connectivity is temporarily lost ( for half an  hour, an hour) and possibility to download and play audiobooks completely offline.  Further in this article I'd like to share my experiences with Android development, as beginner in this area.  And spoiler is I do not like it.<span id="more-1852"></span>

I do not enjoy working on user interfaces generally (although I'm not novice in this area, I have worked in many UI frameworks - both native like GTK, Qt, Java based like Swing and web based like Aurelia), but as being a single resource on my fun projects there is no avail, I have to do it.  So I jumped into Android development finally (for my previous projects I tried to avoid mobile platform and provide responsive web interfaces - for <a href="/projects/python/mybookshelf2-ebooks-management-and-sharing/">Mybookshelf2</a> it worked fine, the web client is reasonably usable in mobile browser), as reasonable playback experience on mobile does require native app.

Concerning learning there are tons of resources as Android is extremely  popular platform. I chose lectures from <a href="https://eu.udacity.com">Udacity</a> ( <a href="https://classroom.udacity.com/courses/ud851">this</a> and <a href="https://classroom.udacity.com/courses/ud855">this</a> course provided by Google engineers/instructors).  Courses combined videos and exercises in Java, which were not difficult to follow and acquired skills were easy to apply in other language - Kotlin. Courses were generally fine,  but  gave me an impression that they were created in hurry - sample exercises have issues in the code and some concepts were  explained hastily. But fine - I went through I started to work on my own application.

First thing I found that I forgot majority of things that I learned - and that was my first issue with Android development - it's huge topic - there are many concepts to grasp, many APIs, many details that can get wrong.  I have to refresh many things around the way. Crucial question that haunted me during the project is - does really Android application have to be so complex? When looking around it seems that Android development takes at least 30% more time (and money) then iOS - is this only due to diversity of Android platform?  I do not believe so,   I thinks it's also due to the monstrosity of the platform.

As one example of things which I consider quite complex is the lifetime of the application - especially when you have fragments in you application. It took me while to get everything in order - so that list fragments appears in the correct position after phone rotation, after hiding activity or after going back in the navigation (using back stack of fragments).

Another thing, which is complete madness, are support libraries (libraries to support newer features in previous versions of Android). There are many of them, often classes have same name as in the core platform and if you are unlucky fool like me you can easily mix then around and got very strange errors.

Another thing which unpleasantly surprised me is how much of incorrect, outdated or incomplete information about Android is around.  Official developer's guide  is fine, but cannot contain every detail ( and it also contains some errors - like <a href="https://developer.android.com/training/volley/requestqueue#singleton">this</a> incorrect implementation of singleton in Kotlin - if not still corrected).  However for particular issues I search the web and usually was directed to famous (or should I say infamous in this context?) <a href="https://stackoverflow.com/">StackOverflow</a>.  A lot of answers there did not work for me, often answers were totally off - topic (obviously put there by desperate reputation seeking individuals with Indian sounding names).  As one example I can mention <a href="https://stackoverflow.com/questions/41547122/android-hamburger-menu-and-back-arrow/49463738#49463738">this one</a> about back navigation from activity bar. None of answers worked, so I wasted quite some time implementing this rather simple navigation feature.  And even worth experience was to make hyperlink working from TextView in navigation drawer.

Third annoying aspect of development where tools. I used Android Studio on Linux desktop (Ubuntu) and it's not working well. When I learned that Android Studio is based on IntelliJ's IDEA, "the most advanced Java IDE", I was looking forward to enjoy care of this popular IDE. However I experienced quite few issues (structure view often gets out of sync, text editor freezes for a while,  autocomplete stops working, project gets of of synch and requires manual resynch).  Issues were not critical, but made feeling of working in Android Studio less pleasant (I heard that IDEA works better on Windows, but I do not want to change my desktop just for this project).

But to be fair I'm just beginner in Android world and surely many things have very good reasoning behind and Android platform is definitely not limited. You can customize each and every aspect of your application and many things are just necessity of the platform (like restart due to screen rotation, complex lifetime to enable system to manage application efficiently and save battery, support for different versions of the system and different HW, etc.). Maybe it's just me who's completely  stupid and struggling with this platform.

Anyhow I crawled through (with many desperate moments, when I was crying aloud "It's so bad, bad, bad")  and application (audioserve Android client) is generally working  - you can check the code <a href="https://github.com/izderadicka/audioserve-android">here</a>.

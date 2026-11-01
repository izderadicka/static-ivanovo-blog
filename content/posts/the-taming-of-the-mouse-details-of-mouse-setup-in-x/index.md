+++
title = "The Taming of The Mouse - Details of Mouse Setup in X"
path = "/the-taming-of-the-mouse-details-of-mouse-setup-in-x/"
date = "2012-10-13T08:37:06"
include_in_feeds = true
[extra]
wordpress_id = 265
kind = "post"
node_key = "265"
author = "admin"
source_url = "http://zderadicka.eu/the-taming-of-the-mouse-details-of-mouse-setup-in-x/"
source_guid = "http://zderadicka.eu/?p=265"
source_date_gmt = "2012-10-13 07:37:06"
[taxonomies]
category = ["Admin"]
tag = ["desktop", "linux", "X"]
+++
<a href="/wp-content/uploads/point.jpeg" rel="attachment wp-att-275"><img alt="" class="wp-image-275 alignleft" decoding="async" height="150" loading="eager" src="/wp-content/uploads/point-150x150.jpeg" title="point" width="150"/></a>After upgrade to  the new version of Linux (Mint 13, which is based on Ubuntu Precise) I'd found that my trackpoint is not working right (on Dell E6410), it was bit unresponsive and movement was not smooth.   Touchpad was generally  OK, but trackpoint really sucked. So I had to look into details of mouse setup in X and I was really surprised how many various parameters are there and how many aspects of mouse behaviour could be modified.   So I'd like to share few tips how to set pointing device - apart of those obvious settings, which are available in desktop settings (Acceleration and Sensitivity).

<span id="more-265"></span>

First of all the desktop setup (Mouse and TouchPad in Gnome/Cinnamon/Unity) was not working for trackpoint, because trackpoint basically another pointer device and setup works reasonably only for  touchpad and external mouse (at least in my case).   So we  have to configure trackpoint manually.

First step is to find right input device - here the `xinput` tool can help us,   if runs without any parameters it lists all available input devices:


```sh
$ xinput
⎡ Virtual core pointer                    	id=2	[master pointer  (3)]
⎜   ↳ Virtual core XTEST pointer              	id=4	[slave  pointer  (2)]
⎜   ↳ DualPoint Stick                         	id=11	[slave  pointer  (2)]
⎜   ↳ AlpsPS/2 ALPS DualPoint TouchPad        	id=12	[slave  pointer  (2)]
⎣ Virtual core keyboard                   	id=3	[master keyboard (2)]
    ↳ Virtual core XTEST keyboard             	id=5	[slave  keyboard (3)]
    ↳ Power Button                            	id=6	[slave  keyboard (3)]
    ↳ Video Bus                               	id=7	[slave  keyboard (3)]
    ↳ Power Button                            	id=8	[slave  keyboard (3)]
    ↳ Sleep Button                            	id=9	[slave  keyboard (3)]
    ↳ AT Translated Set 2 keyboard            	id=10	[slave  keyboard (3)]
    ↳ Dell WMI hotkeys                        	id=13	[slave  keyboard (3)]
```


We can see that the trackpoint device is called "DualPoint Stick" and has id 11. Now we can start to play with its settings, here again `xinput` will help. We need to find what parameters we can set for this device:


```sh
$ xinput watch-props "DualPoint Stick"
Device 'DualPoint Stick':
	Device Enabled (126):	1
	Coordinate Transformation Matrix (128):	1.000000, 0.000000, 0.000000, 0.000000, 1.000000, 0.000000, 0.000000, 0.000000, 1.000000
	Device Accel Profile (247):	2
	Device Accel Constant Deceleration (248):	2.000000
	Device Accel Adaptive Deceleration (249):	2.000000
	Device Accel Velocity Scaling (250):	10.000000
	Device Product ID (243):	2, 8
	Device Node (244):	"/dev/input/event6"
	Evdev Axis Inversion (251):	0, 0
...and more
```


To influence cursor movement these 4 properties are of interest:
**Device Accel Profile** \- this is most important parameter, because it set  an algorithm for cursor behaviour - how it accelerates  and decelerates based on mouse movement.  I have found that profile 2 - **polynomial** is most appropriate for me.   Also default profile 0 can behave well for trackpoint, but I have found one flaw -  this profile is dependent on *threshold* value (the desktop setting window calls it Sensitivity) that is set by `xset mouse` \- and this value is common for several pointer devices, so if you optimize your trackpoint for profile 0,  and then you go to touchpad settings and change Sensitivity value there, your trackpoint settings get suboptimal again.  So profile 2 can assure completely independent control of  this device.
**Device Accel Constant Deceleration** and **Device Accel Adaptive Deceleration** parameters controls how cursor will slow down and are quite important for precise movement.  Especially Adaptive Deceleration is worth to play with.
**Device Accel Velocity Scaling** basically influences how sensitive cursor is to mouse movements and determines sampling rate of mouse movement.
Very detailed and profound explanation of  how these parameters works and how they should be set up can be found [here](http://xorg.freedesktop.org/wiki/Development/Documentation/PointerAcceleration#Scenarios).

To find optimal parameters we have to play with them for a while - using`  xinput set-prop ` \- the mouse reacts immediately after property is changed. Property can be referenced either by name or id - I've found using ids easier. So we can try something like this:


```sh
xinput set-prop "DualPoint Stick" 247 2
xinput set-prop "DualPoint Stick" 248 2
xinput set-prop "DualPoint Stick" 249 2
xinput set-prop "DualPoint Stick" 250 10
```


When we're done with tests we have to make these changes permanent, best way is to create device specific config file  /etc/X11/xorg.conf.d/90-evdev-trackpoint.conf that looks like this:


```sh
Section "InputClass"
	Identifier	"trackpoint E6410"
	MatchIsPointer	"true"
	MatchProduct	"DualPoint Stick"
	MatchDevicePath	"/dev/input/event*"
	Option "AccelerationProfile"  "2"
	Option "ConstantDeceleration"  "2.0"
	Option "AdaptiveDeceleration"  "2.0"
	Option "VelocityScale" "10.0"

EndSection
```

+++
title = "NetworkManager Script to Set HTTP Proxy"
path = "/networkmanager-script-to-set-http-proxy/"
date = "2016-10-27T13:35:08"
include_in_feeds = true
[extra]
wordpress_id = 1475
kind = "post"
node_key = "1475"
author = "admin"
source_url = "http://zderadicka.eu/networkmanager-script-to-set-http-proxy/"
source_guid = "http://zderadicka.eu/?p=1475"
source_date_gmt = "2016-10-27 12:35:08"
categories = ["Admin"]
+++
While Gnome and it's derivatives support automatic proxy detection,  it do not work well for all programs, particularly for command line programs.   I've found  that using simple script in /etc/NetworkManager/dispatcher.d works better for me, which sets and unsets fixed proxy works better.   NM dispatcher scripts are run each time network connections change (network up, down, VPN connect etc.) and received two parameters ( interface name and status) and bunch of environment variables.<span id="more-1475"></span>

This script is useful for exploring how NM dispatcher scripts are called:


```sh
#!/bin/bash
LOG_FILE=/tmp/nmlog.txt
if [[ ! -f $LOG_FILE ]]; then exit 0; fi

echo ------`date`------ >> $LOG_FILE
echo Running as `whoami` >> $LOG_FILE
echo PARAMS $1 $2 >> $LOG_FILE 
env >> $LOG_FILE

```


For proxy activation and deactivation we first need to set it up in Network preferences as manual proxy (or you can use `dconf_editor` \- which enables to setup also URLs to bypass proxy - look under key `system/proxy`).  To activate or deactivate proxy we can later just switch between manual and none proxy modes (which we can  do easily with `gsettings command`).

Here is final script:


```sh
#!/bin/bash

VPN_DEV=vpn0
OFFICE_IP_PREFIX='^10\.163\.1'
USER=`users|awk '{print $1}'` #on normal desktop usually only one user is logged
USER_ID=`id -u $USER`
ETHER_DEV=`nmcli d| grep ethernet| awk '{print $1; exit}'`
export $(strings /proc/$(pgrep -U $USER_ID gnome-session | head -n 1)/environ | grep DBUS)

set_proxy () {
[[ -z "$1" ]] && MODE="none" MSG="Proxy Unset" || MODE="manual" MSG="Proxy Set"

sudo -u $USER -E gsettings set org.gnome.system.proxy mode $MODE
sudo -u $USER -E  notify-send -t 2000 -i network-wired-disconnected $MSG

}

up_down () {
	if [[ $1 == "up" ]]; then
		set_proxy 1
	elif [[ $1 == "down" ]]; then
		set_proxy
	 fi
}

if [[ $1 == $VPN_DEV ]]; then
	up_down $2
elif [[ $1 == $ETHER_DEV  ]]; then 
	if [[  $2 == "up" || $2 == "dhcp4-change" ]]  && [[ $IP4_ADDRESS_0 =~ $OFFICE_IP_PREFIX ]]; then
		set_proxy 1
	elif [[ $2 == "down" ]]; then
		set_proxy
	 fi
fi

```


Some gotchas:


<ul>
<li>Scripts must have proper permissions,   NetworkManager runs only executable scripts and ignores scripts with too permissive access ( write for others)</li>
<li>Script runs under root, but <code>gsettings</code> and <code>send-notify</code> should be run under your user account and they also need current desktop dbus address (DBUS env.variable in your desktop session)</li>
<li>in case of DHCP 'up' status is often not enough - interface can be up, but yet not received IP address from DHCP server, we should look also for<code> dhcp4-change</code> status</li>
<li>Skype does not handle change of proxy (from manual to none and vice versa), this function could be used to restart skype (not yet fully reliable):
<pre class="code-highlight" data-language="sh"><code><span class="code-line">restart_skype<span class="o">()</span><span class="w"> </span><span class="o">&#123;</span></span>&#10;<span class="code-line">sudo<span class="w"> </span>-u<span class="w"> </span><span class="nv">$USER</span><span class="w"> </span>bash<span class="w"> </span>-c<span class="w"> </span><span class="s2">&quot;export </span><span class="k">$(</span>strings<span class="w"> </span>/proc/<span class="k">$(</span>pgrep<span class="w"> </span>-U<span class="w"> </span><span class="nv">$USER_ID</span><span class="w"> </span>gnome-session<span class="w"> </span><span class="p">|</span><span class="w"> </span>head<span class="w"> </span>-n<span class="w"> </span><span class="m">1</span><span class="k">)</span>/environ<span class="p">|</span>xargs<span class="k">)</span><span class="s2">; pkill skype; sleep 5; skype &amp;&quot;</span></span>&#10;<span class="code-line"><span class="o">}</span></span></code></pre>
 </li>
</ul>

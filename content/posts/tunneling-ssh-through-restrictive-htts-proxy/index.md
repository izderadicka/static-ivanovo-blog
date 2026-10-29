+++
title = "Tunneling SSH through Restrictive HTTS Proxy"
path = "/tunneling-ssh-through-restrictive-htts-proxy/"
date = "2015-02-27T12:09:06"
include_in_feeds = true
[extra]
wordpress_id = 996
kind = "post"
node_key = "996"
author = "admin"
source_url = "http://zderadicka.eu/tunneling-ssh-through-restrictive-htts-proxy/"
source_guid = "http://zderadicka.eu/?p=996"
source_date_gmt = "2015-02-27 11:09:06"
categories = ["Admin"]
tags = ["proxy", "SSH"]
+++
In <a href="/accessing-imapsmtp-via-https-proxy/">one of past articles</a> I've described how to use HTTP CONNECT method to tunnel other protocols through a proxy.  It worked for me for various protocols ( mainly email access IMAP, SMTP),  but recently it stopped working for SSH protocol. After some investigation I've found  that proxy is checking  what protocol it is tunnelling through and expects it to be SSL/TLS.  If it is anything else, proxy closes connection with an error.  It still worked for mail protocols,  because they were already wrapped in SSL. But to be still able to use SSH through proxy some more sophisticated setup was needed -  tunnelling SSH through SSL protocol, which is then tunnelled via HTTPS proxy ( HTTP CONNECT method).  Below I describe a setup,  which works for me.<span id="more-996"></span>


##  Tools used


All tools could be installed from Ubuntu/Debian repositories via apt-get.

<strong>stunnel4</strong> \-   is a program that can wrap/unwrap any connection into/from SSL protocol
<strong>openssl</strong> \- SSL utilities and SSL client
<strong>proxytunnel</strong> \-  utility to tunnel connection through HTTPS proxy


##  Sever Setup


On SSH server we have to install stunnel4 and openssl and configure it to accept SSL on some port and forward then unencrypted connection to local SSH server:


```sh
sudo apt-get install stunnel4
#generate key - we are not interested very much in security so can use rather minimal settings
openssl req -newkey rsa:1024 -sha1 -days 3650 -keyout stunnel.key -nodes -x509 -out stunnel.crt
cat stunnel.crt stunnel.key > stunnel.pem
sudo cp stunnel.pem /etc/stunnel/
#enable stunnel - set ENABLED=1
sudo nano /etc/default/stunnel4
#edit configuration - see below
sudo nano /etc/stunnel/stunnel.conf
#and start stunnel server
sudo service stunnel4 start

```


Here is configuration file stunnel.conf:


```sh
pid = /var/run/stunnel.pid
cert = /etc/stunnel/stunnel.pem
[ssh] 
accept = 192.168.1.110:2222
connect = 127.0.0.1:22

```




## On Client Behind Proxy


We need to install `proxytunnel` here. Then following command will connect us to remote SSH server via HTTPS proxy:


```sh
ssh -o "ProxyCommand /usr/bin/proxytunnel -v -p proxy_host:port -d ssh_server_host:2222 -e" user@ssh_server_host

```


And we can add proxy configuration to ~/.ssh/config:


```sh
Host ssh_server_host
       ProxyCommand /usr/bin/proxytunnel -v -p proxy_host:port -d ssh_server_host:2222 -e


```


And then connect easily just with short ssh command:


```sh
ssh user@ssh_server_host
```




## Possible Improvements


This <a href="http://blog.chmd.fr/ssh-over-ssl-episode-4-a-haproxy-based-configuration.html">article describes</a> how to use <a href="http://www.haproxy.org/">haproxy</a> to serve both HTTPS and SSH (tunneled in SSL) on same port, e.g. 443 - so service will look like normal secure web site.

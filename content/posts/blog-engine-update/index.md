+++
title = "Blog Engine Update"
path = "/blog-engine-update/"
date = "2026-11-01T08:34:11+00:00"
[taxonomies]
category = ["Announcement"]
tag = []
[extra]
kind = "post"
author = "admin"
+++

I've update blog engine to statically generated site using [Zola](https://getzola.org).  I have been thinking of moving from [Wordpress](https://wordpress.org/) for some time, but recent [php2shell vulnerability](https://en.wikipedia.org/wiki/PHP2Shell) convinced me to proceed. 

<!-- more -->

Actually most of work was done with help of [Codex](https://openai.com/codex/), partly as exercise with this coding agent. The goal was to use Zola to make static site similar to the old one. Work went well - actually should be done with one pass using `Astra` model -  but final solution seemed too complicate -  so I required some simplification - and that was bit iterative process - common understanding of simpler was bit more tricky to achieve with the agent.

As I do not publish more and most of my content is outdated (but still want to keep it around - mainly from sentimental reasons) I decided for static site.  Wordpress requires continuous updates and is bit overkill for simple blog.  Will see how it'll work.

I also use [Pagefind](https://pagefind.app/) - static full text search, fully in browser. Works quite well - with index size something like 30k and almost instant build.

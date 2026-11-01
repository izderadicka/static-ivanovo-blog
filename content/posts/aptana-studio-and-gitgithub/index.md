+++
title = "Aptana Studio And Git/Github"
path = "/aptana-studio-and-gitgithub/"
date = "2012-09-23T18:08:12"
include_in_feeds = true
[extra]
wordpress_id = 121
kind = "post"
node_key = "121"
author = "admin"
source_url = "http://zderadicka.eu/aptana-studio-and-gitgithub/"
source_guid = "http://zderadicka.eu/?p=121"
source_date_gmt = "2012-09-23 17:08:12"
[taxonomies]
category = ["Programming"]
tag = ["aptana", "eclipse", "git"]
+++
Aptana studia is a plugin to Eclipse, which contains many useful modules (like PyDev) and amongst many also GIT module. However this module is different than EGit ( and EGit cannot be installed because it conflicts with Aptana Git)so manual on Github is not applicable. So how does it work? On my recent project I've tried to use it  and here is quick guide how to  create project and push it to Github.<span id="more-121"></span>


<ol>
<li>Create project on GITHub. Register your SSH key with project (If you do not know how, surely there is a tutorial on Github).</li>
<li>In Eclipse in Navigator or Project Explorer right click on project folder and select **Team/Share Project ...**</li>
<li>Select **Aptana Git** and click **Next**</li>
<li>Select proposed location for GIT repository, click **Create** and **Finish**</li>
<li>Select files you do not want to include in version control (temp files, test data, etc.) in Navigator or Project Explorer, right click and select **Team/ Add to .gitignore**</li>
<li>Select project folder, right click and select **Team/Commit ...**</li>
<li>In dialog choose .gitignore file - move it to right  (Staged Changes)  and click **Commit**. This has to be done because Aptana plugin will remove unwanted files from unstaged files only after .gitignore is committed.</li>
<li>Now click on project folder again, right click and select **Team/Commit ...** and commit all remaining files.</li>
<li>Click on the project folder, then right click and select **Team/Remotes/Add...**</li>
<li>In dialog fill Remote Name, Remote URI (something like git@github.com:your_name/your_project.git) and click **OK**.</li>
<li>Now you need to push project to remote -  first time you should do it from terminal - for two reasons - first to associate local branch with remote branch (I did not found any way how to do it in Eclipse), second reason is that for first time git will require to confirm authenticity of remote key - if process is run from Eclipse, it gets stuck.  This is command to push:
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="nb">cd</span><span class="w"> </span>your_project_directory</span>&#10;<span class="code-line">git<span class="w"> </span>push<span class="w"> </span>--set-upstream<span class="w"> </span>your_remote_name</span></code></pre>
You may need to pull remove branch first if you already have some files there:
<pre class="code-highlight" data-language="sh"><code><span class="code-line">git<span class="w"> </span>pull<span class="w"> </span>your_remote_name</span></code></pre>
</li>
<li>From now on you can work normally work with Aptana Git - commit all changes you do, and push changes to Github - via context menu **Team/Push**</li>
</ol>

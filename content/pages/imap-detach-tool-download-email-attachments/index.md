+++
title = "imap_detach Tool - Download Email Attachments"
path = "/projects/python/imap_detach-tool-download-email-attachments/"
date = "2015-11-21T08:47:09"
include_in_feeds = false
[extra]
wordpress_id = 1137
kind = "page"
node_key = "1137"
author = "admin"
source_url = "http://zderadicka.eu/projects/python/imap_detach-tool-download-email-attachments/"
source_guid = "http://zderadicka.eu/?page_id=1137"
source_date_gmt = "2015-11-21 07:47:09"
menu_order = 0
parent = "/projects/python/"
+++
<strong>imap_detach </strong>is a command line tool, which enables you to automatically download email attachments (or particular email parts) from your mailbox  via IMAP protocol.  The tool is fairly universal and can be used with various IMAP servers for various tasks. The tool is written in <a href="https://www.python.org/">Python</a>.


## How it works


To work efficiently with this tool you need at least basic understanding of two email technologies <a href="https://en.wikipedia.org/wiki/MIME">MIME</a>  and <a href="https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol">IMAP</a>.

MIME defines structure of an email message and it enables the message to have multiple parts. The message and each of its parts have a header, which defines it's type (`Content-type` field in the header) and how it's attached to the message (`Content-disposition` field in the header, which also defines file name of the attachment).  Content type defines media type within particular message part - for message text it can be `text/plain` or `text/html`, for PDF document it's `application/pdf`,  for PNG image it's `image/png` etc.  Content type consists from two parts: type and subtype, separated by slash. Content types are registered by <a href="http://www.iana.org/">IANA</a> for every possible media type. List of all content types is <a href="http://www.iana.org/assignments/media-types/media-types.xhtml">here</a>.

Email message following MIME standard can have multiple parts, which can be nested, so message parts form a tree structure. For the purpose of parts nesting MIME defines special content types - `multipart`.  Below is a sample MIME message structure:

<a href="/wp-content/uploads/mime.png"><img alt="mime" class="alignnone wp-image-1145 size-medium" decoding="async" height="296" loading="eager" sizes="(max-width: 300px) 100vw, 300px" src="/wp-content/uploads/mime-300x296.png" srcset="/wp-content/uploads/mime-300x296.png 300w, /wp-content/uploads/mime.png 768w" width="300"/></a>

IMAP is a protocol for communication with mailbox server - e.g. server where your emails are stored.  IMAP server organizes emails into folders (Inbox, Sent, Drafts ...,  you can also easily create your own folders) and enables you to access to particular folders.  IMAP protocol is pretty complex and provides many advanced operations with messages -  for our purpose these three are of special importance:  search, MIME message structure parsing and MIME message parts download.

Similar tools or scripts for downloading attachments often take simplified approach - they download all messages from a folder and then parse message locally and extract required parts and save them.  This approach is indeed inefficient,  because much more data are downloaded, then is finally needed.

Our tool exploits advanced features of IMAP to get only those data, that are necessary to download required parts of email messages. We use a simple filter expression, described in detail in the next section. With this expression you can easily specify, which attachments you'd like to download.  For example we can specify:
`! seen & from ~="john.doe" & mime= "application/pdf"`.
This expression basically says - get me all attached PDF files, which were sent by john.doe (from whatever domain) and which I have not seen yet.

And this is our formula how to get relevant attachments / message parts using the filter expression:


<ol>
<li>Convert filter expression into IMAP search keywords. However IMAP search is less powerful then our expressions, especially many servers cannot search on part attributes like content type, file name etc.   So IMAP search can only provide a superset of messages we are interested in.  For our sample filter expression above IMAP search will look like (NOT SEEN FROM "john.doe") - so it provides message IDs for all unseen messages from john.doe.</li>
<li>For all messages identified by IMAP search we download message structure (BODYSTRUCTURE), which provides necessary details about message parts</li>
<li>Use filter expression again for all parts - now we have all details to identify relevant parts - for our sample expression we select just PDF attachments.</li>
<li>Download all matching parts.</li>
<li>Optionally for processed messages we can do some IMAP actions on the message - like delete it, move to other folder or mark is as seen.</li>
</ol>


It has to be understood that compliance level of various IMAP server implementations differs -  our tool has been tested mostly against <a href="http://www.dovecot.org/">dovecot</a> \- which provides <a href="http://imapwiki.org/ImapTest/ServerStatus">best IMAPv4 compliance level</a>.  From tests with other servers we saw some differentness  ( for instance Gmail subject search works only for full words). It's left to users to explore peculiarities of particular IMAP server.  And you are always welcomed to <a href="https://github.com/izderadicka/imap_detach/issues">log issue on github</a>.


## Usage


<strong>Warning: If used with some arguments (--delete, --move) it can significantly modify your mailbox - so be careful!</strong>

Commad to run is called detach.py,   `detach.py -h` will show help message - for convenience help is shown in next section.

Connection to server must be specified with `--host`, `--user` and `--password` arguments, `--host` is just a server name or host:port, if non standard port is used.  By default connection is using SSL encryption,  plain, non-encrypted connection can be enforced by`  --no-ssl ` argument. There is also `--insecure-ssl`  argument, which switch off check of SSL certificate (useful mainly for testing).

Folder argument `--folder` defines which folder(s) to be searched. If not specified default is INBOX, you can specify one or more folders ( with multiple `--folder` arguments). Also patterns are supported:  \* (matches all characters except /), \*\* (match all characters) and ? (matches one character).

If you specify `--threads x`,  download of emails parts  runs in x separate threads (each having separate connections).  This can significantly speed up download if there are many messages ( but could be overkill for few messages).

`filter` argument specifies a logical expression, which identifies message parts that are to be downloaded. Expression consist of literals, comparisons, variables and logical operators.

<strong>Literals</strong>:


<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table style="height: 35px;" width="877">
<tbody>
<tr>
<td>string</td>
<td>Enclosed in double quotes</td>
<td>"some text"</td>
</tr>
<tr>
<td>integers</td>
<td>numbers[kMG]</td>
<td>1234 5k 12M</td>
</tr>
<tr>
<td>date</td>
<td>YYYY-MM-DD</td>
<td>2015-11-214</td>
</tr>
<tr>
<td>datetime</td>
<td>YYYY-MM-DD HH:SS</td>
<td>2015-11-21 17:04</td>
</tr>
</tbody>
</table></div>


<strong> Comparisons (variable operator literal):</strong>


<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table>
<tbody>
<tr>
<td>=</td>
<td>equals</td>
<td>universal, for strings it ignores case</td>
<td>mime = "image/png"</td>
</tr>
<tr>
<td>~=</td>
<td>contains</td>
<td>strings only, case insensitive</td>
<td>subject ~= "test"</td>
</tr>
<tr>
<td>^=</td>
<td>starts with</td>
<td>strings only, case insensitive</td>
<td>subject ^= "Re:"</td>
</tr>
<tr>
<td>$=</td>
<td>ends with</td>
<td>strings only, case insensitive</td>
<td>name $= ".pdf"</td>
</tr>
<tr>
<td>&lt;</td>
<td>less then</td>
<td>integers or dates</td>
<td>date &lt; 2015-11-21</td>
</tr>
<tr>
<td>&gt;</td>
<td>greater then</td>
<td>integers or dates</td>
<td>size &gt; 2M</td>
</tr>
<tr>
<td>&lt;=</td>
<td>less then or equal</td>
<td>integers or dates</td>
<td>date &lt;= 2015-11-21</td>
</tr>
<tr>
<td>&gt;=</td>
<td>greater then or equal</td>
<td>integers or dates</td>
<td>size &gt;= 2M</td>
</tr>
</tbody>
</table></div>


<strong>Variables:
</strong>Various variables with information related to email header or email part are available.  These variables can be also used as substitution variables for output file name or for command run on part content.


<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table>
<tbody>
<tr>
<td>subject</td>
<td>string</td>
<td>Email header</td>
<td>subject of the email</td>
</tr>
<tr>
<td>from</td>
<td>string</td>
<td>Email header</td>
<td>email address of the sender</td>
</tr>
<tr>
<td>sender</td>
<td>string</td>
<td>Email header</td>
<td>email address of the sender - can be different from the from</td>
</tr>
<tr>
<td>to</td>
<td>string</td>
<td>Email header</td>
<td>email addresses of recipients, separated by comma</td>
</tr>
<tr>
<td>cc</td>
<td>string</td>
<td>Email header</td>
<td>email addresses of CC recipients, separated by comma</td>
</tr>
<tr>
<td>bcc</td>
<td>string</td>
<td>Email header</td>
<td>email addresses of BCC recipients, separated by comma</td>
</tr>
<tr>
<td>date</td>
<td>datetime</td>
<td>Email header</td>
<td>date, when email arrived to mailbox - e.g. receipt date,  ignores time zone</td>
</tr>
<tr>
<td>year</td>
<td>integer</td>
<td>Email header</td>
<td>year, when email arrived to mailbox</td>
</tr>
<tr>
<td>month</td>
<td>integer</td>
<td>Email header</td>
<td>month (1 -12), when email arrived to mailbox</td>
</tr>
<tr>
<td>day</td>
<td>integer</td>
<td>Email header</td>
<td>day (1-31), when email arrived to mailbox</td>
</tr>
<tr>
<td>answered</td>
<td>boolean</td>
<td>IMAP Flag</td>
<td>Email has Answered flag - it's set by client, when answering the email</td>
</tr>
<tr>
<td>seen</td>
<td>boolean</td>
<td>IMAP Flag</td>
<td>Email has Seen flag- it has been opened by some email client</td>
</tr>
<tr>
<td>flagged</td>
<td>boolean</td>
<td>IMAP Flag</td>
<td>Email has Flagged flag - often it's called "stared" email by clients</td>
</tr>
<tr>
<td>deleted</td>
<td>boolean</td>
<td>IMAP Flag</td>
<td>Email has Deleted flag - it has been deleted by client, but not yet expunged from the folder</td>
</tr>
<tr>
<td>recent</td>
<td>boolean</td>
<td>IMAP Flag</td>
<td>Email has Recent flag - this is the first session, when this email is available</td>
</tr>
<tr>
<td>draft</td>
<td>boolean</td>
<td>IMAP Flag</td>
<td>Email has Draft flag</td>
</tr>
<tr>
<td>flags</td>
<td>string list</td>
<td>IMAP Flag</td>
<td>All flags available, even non-standard. You can test them as string, test succeeds, if string matches any flag.</td>
</tr>
<tr>
<td>mime</td>
<td>string</td>
<td>Email part</td>
<td>Content type of this part - type/subtype</td>
</tr>
<tr>
<td>attached</td>
<td>boolean</td>
<td>Email part</td>
<td>Is it attachment (Content-disposition is attachment)?</td>
</tr>
<tr>
<td>size</td>
<td>integer</td>
<td>Email part</td>
<td>Approximate size of this part in bytes (inexactness is because we know only encoded size -  for base64 difference can be max 3 bytes due to padding, but for quoted-printable it can be bigger)</td>
</tr>
<tr>
<td>name</td>
<td>string</td>
<td>Email part</td>
<td>File name of attachment (or empty if this part is not attachment)</td>
</tr>
<tr>
<td>section</td>
<td>string</td>
<td>Email part</td>
<td>Number of part in email structure - like 1, 2.1, 1.2.1 etc.</td>
</tr>
</tbody>
</table></div>


<strong>Logical operators:</strong>

Simple expressions (comparisons or standalone boolean variables)  can be combined by logical operators:
! - not
& - and
| - or
Priority of operators is ! & |,  bracket ( and ) can be used to explicitly define evaluation order.

Example of filter expression:


```sh
subject ~= "test" & date > 2015-10-21 & ( ! deleted | ! seen)
```


Next after filter we have to define what happens to downloaded email parts, there are three options:


<ul>
<li>save part in the file named after <code>--file</code> argument (with possible variables replacements explained below)</li>
<li>run the command specified by --command argument - part content is passed to the command as standard input</li>
<li>both save the file first and then run command on it (use both <code>--file</code> and <code>--command</code> arguments),  command then must contain file name variable.</li>
</ul>


Both command and output file arguments can contain variables in  curly brackets - {variable}.  Same variables as for filter can be used for command - so for instance {subject} is replaced by email subject, {name} by attachment file name (the original name specified in the email), {date} by received date etc. There is also possibility for very simple combinations of variables {name|subject}, expands to name, if available, else to subject, {name+subject} expands to name joined with subject by '\_' character. Both can be combined so we can write {name|subject+section}.

Additionally `--command` can contain following variables related to already expanded output file name:


<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table>
<tbody>
<tr>
<td>file_name</td>
<td>full output file name with path</td>
</tr>
<tr>
<td>file_base_name</td>
<td>output file name without path and without extension</td>
</tr>
<tr>
<td>file_dir</td>
<td>directory component of output file name</td>
</tr>
</tbody>
</table></div>


`--delete-file` argument deletes file after it's processed by command ( so it makes sense to use it only if combination of `--file` `--command` is used).

After message parts are processed we can apply an action to the whole email message containing these parts - we can either delete email message (`--delete`), move to other folder (`--move`) or mark as seen (`--seen`). These 3 arguments are only 'unsafe' arguments that modify the mailbox.

To follow the progress of the tool and debug potential issues several other arguments are available:
`--test` \-  dry run - just prints which message parts it should download based on the filter, but does not download them
`--verbose` \- prints some basic message about message parts being downloaded
`--debug` \- prints debug information
`--log-file` \- messages are printed to this file instead of standard error output
`--no-imap-search` \- implementations of IMAP SEARCH commands varies by server. This option causes to skip IMAP SEARCH and to get all messages in folder and to filter them locally.


## Help


<strong>detach.py -h</strong>


```sh
usage: detach.py [-h] -H HOST -u USER [-p PASSWORD] [--no-ssl]
                 [--insecure-ssl] [--folder FOLDER] [-f FILE_NAME]
                 [-c COMMAND] [-t THREADS] [-v] [--debug]
                 [--log-file LOG_FILE] [--test] [--seen] [--delete]
                 [--delete-file] [--move MOVE] [--timeit] [--no-imap-search]
                 [--unsafe-imap-search] [--version]
                 filter

positional arguments:
  filter                Filter for mail parts to get, simple expression with variables comparisons ~=, = , > etc. and  logical operators & | ! and brackets 

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  IMAP server - host name or host:port
  -u USER, --user USER  User name
  -p PASSWORD, --password PASSWORD
                        User password
  --no-ssl              Do not use SSL, use plain unencrypted connection
  --insecure-ssl        Use insecure SSL - certificates are not checked
  --folder FOLDER       mail folder(s), can specify more, or pattern with ?, * or **,  default is INBOX
  -f FILE_NAME, --file-name FILE_NAME
                        Pattern for outgoing files - supports {var} replacement - same variables as for filter
  -c COMMAND, --command COMMAND
                        Command to be executed on downloaded file, supports {var} replacement - same variables as for filter, if output file is not specified, data are sent via standard input 
  -t THREADS, --threads THREADS
                        Download message parts in x separate threads
  -v, --verbose         Verbose messaging
  --debug               Debug logging
  --log-file LOG_FILE   Log is written to this file (otherwise it's stdout)
  --test                 Do not download and process - just show found email parts
  --seen                Marks processed messages (matching filter) as seen
  --delete              Deletes processed messages (matching filter)
  --delete-file         Deletes downloaded file after command
  --move MOVE           Moves processed messages (matching filter) to specified folder
  --timeit              Will measure time tool is running and print it at the end
  --no-imap-search      Will not use IMAP search - slow, but will assure exact filter match on any server
  --unsafe-imap-search  Advanced IMAP search features, requiring full IMAPv4 compliance, which are supported only by some servers (dovecot)
  --version             show program's version number and exit

Variables for filter: answered attached bcc cc date day deleted draft flagged flags from mime month name recent section seen sender size subject to year
Operators for filter: = ~= (contains) ^= (starts with) $= (ends with) > < >= <= 
Date(time) format: YYYY-MM-DD or YYYY-MM-DD HH:SS - enter without quotes
Additional variables for command: file_name file_base_name file_dir

```




## License


<a href="http://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License v3 (GPLv3)</a>


## Download


Download <a href="https://github.com/izderadicka/imap_detach">source from github</a>.

Install with pip:


```sh
pip install imap_detach
```




## Support


Have a problem with tool? The best solution is go tothe  code and fix it yourself. Then send pull request to <a href="https://github.com/izderadicka/imap_detach/">github</a>.  By this you'll assure that it's fixed and you can also help others.

If you cannot fix it you are welcomed to <a href="https://github.com/izderadicka/imap_detach/issues">post issue on github project pages</a>.

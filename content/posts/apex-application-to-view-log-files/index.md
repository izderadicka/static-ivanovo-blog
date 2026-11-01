+++
title = "APEX Application to View Log Files"
path = "/apex-application-to-view-log-files/"
date = "2014-07-07T07:45:22"
include_in_feeds = true
[extra]
wordpress_id = 824
kind = "post"
node_key = "824"
author = "admin"
source_url = "http://zderadicka.eu/apex-application-to-view-log-files/"
source_guid = "http://zderadicka.eu/?p=824"
source_date_gmt = "2014-07-07 06:45:22"
[taxonomies]
category = ["Programming"]
tag = ["Apex", "Java", "PL/SQL"]
+++
Oracle APEX is keeping all data in database and makes it easy to create different reports for tables or views.  But what if we want to present something outside of database?   Like text log files - how this could be done in APEX?   For regular web server it is a trivial task - usually simple configuration of web server enables to list directory and download any files from it (and it probably would be easiest way to do it). But what if we need to integrate logs browsing into APEX application?  Actually there is a way to list and serve files even in APEX, if it is required.<span id="more-824"></span>


## DB Schema Setup


First we need to add some privileges to  our APEX schema (let it call APEX\_SCHEMA);  Execute this commands as sysdba:


```sql
CREATE DIRECTORY UPLOADS AS '/data/uploads';
GRANT READ ON DIRECTORY UPLOADS TO APEX_SCHEMA;
exec dbms_java.grant_permission( 'APEX_SCHEMA', 'SYS:java.io.FilePermission', '/data/uploads', 'read' );
exec dbms_java.grant_permission( 'APEX_SCHEMA', 'SYS:java.io.FilePermission', '/data/uploads/*', 'read' );

```


This createa a DB directory object - so we can access the files within this directory from PL/SQL.  For some reasons ( probably security) it is not possible to list files in directory object.  So we  need some Java code to do this.  Java is running in a sandbox so we need to add explicit permissions to access files in our directory.


## Supporting Code


We need some code to help us with directory listing:


```sql
create global temporary table DIR_LIST
  ( filename varchar2(255),
    modified timestamp with local time zone,
    len number)
  on commit preserve rows;
 /

create or replace
      and compile java source named "DirList"
    as
    import java.io.*;
    import java.sql.*;
    
    public class DirList
    {
    public static void getList(String directory)
                      throws SQLException
   {
       File path = new File( directory );
       File[] list = path.listFiles();
       String element;
       Timestamp updated;
       long len;
       
       for(int i = 0; i < list.length; i++)
       {
           element = list[i].getName();
           updated = new Timestamp(list[i].lastModified());
           len = list[i].length();
           
          #sql { INSERT INTO DIR_LIST (FILENAME, MODIFIED, LEN)
                 VALUES (:element, :updated, :len) };
      }
   }
 
  }
 /
 
create or replace
procedure get_dir_list( p_directory in varchar2 )
  as language java
  name 'DirList.getList( java.lang.String )';
/

function load_file_to_blob(p_filename varchar2) return blob
as
l_file UTL_FILE.FILE_TYPE;
l_data blob;
l_chunk number := 32767;
l_buf raw(32767);
l_pos number;
l_read number;
begin
l_file := UTL_FILE.fopen('UPLOADS', p_filename, 'r',  32767);
DBMS_LOB.createtemporary(l_data, true);
loop
l_pos:= UTL_FILE.fgetpos(l_file);
UTL_FILE.get_raw(l_file, l_buf, l_chunk);
l_read := UTL_FILE.fgetpos(l_file) - l_pos;
DBMS_LOB.writeappend(l_data, l_read, l_buf); 
if  l_read < l_chunk then 
exit;
end if;
end loop;
UTL_FILE.fclose(l_file);
return l_data;
end load_file_to_blob;
/
```


This  creates a temporary table, that  contains the listing of the directory,  procedure `get_dir_list` that  fills this table and function`  load_file_to_blob `.


##  APEX Application


Now we can create two new pages in our APEX application - first page will show report with all files in given directory. We create regular report page, where there is following PL/SQL process started 'Before Header':


```sql
begin 
delete from dir_list;
get_dir_list('/data/uploads');
end;
```


Source of the the report is following query:


```sql
select filename, modified, len as "length", 'Show' as "Link" from dir_list order by modified desc
```


Last column should be a link,   which redirects to our next page.  There should be also page item PX\_FNAME, that stores selected file name. To open link in  a new browser window set 'Link Attributes' to 'target="\_blank"'. Also use link to set item PX\_FNAME to #FILENAME#.

Second page serves the file content. We create blank page and put this code into PL/SQL code assigned to 'Before Header' stage:


```sql
declare
l_data blob;
begin
htp.init;  
OWA_UTIL.mime_header ('text/plain');  
l_data:= load_file_to_blob(v('PX_FNAME'));
WPG_DOCLOAD.download_file (l_data);  
apex_application.stop_apex_engine;   
end;
```


The code for serving file content is bit different in APEX 4.2  -  I found some examples on Internet, which has been writing additional headers  (Content-Disposition, Content-Length) using htp.p procedure and then closing header with ` OWA.UTIL.http_header_close.  ` However this is not working with latest APEX version - everything written to response after`  OWA_UTIL.mime_header ` call is written to response body. On the other hand the length of content is calculated automatically.

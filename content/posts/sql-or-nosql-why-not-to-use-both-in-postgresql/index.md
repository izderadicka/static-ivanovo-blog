+++
title = "SQL or NoSQL - Why not to use both (in PostgreSQL)"
path = "/sql-or-nosql-why-not-to-use-both-in-postgresql/"
date = "2016-05-01T10:40:44"
include_in_feeds = true
[extra]
wordpress_id = 1329
kind = "post"
node_key = "1329"
author = "admin"
source_url = "http://zderadicka.eu/sql-or-nosql-why-not-to-use-both-in-postgresql/"
source_guid = "http://zderadicka.eu/?p=1329"
source_date_gmt = "2016-05-01 09:40:44"
categories = ["Programming", "Tools"]
tags = ["comparison", "MongoDb", "PostgreSQL", "python"]
+++
NoSQL databases have become very popular in last years and there is a plenty of various options available. It looks like traditional relational databases (RDBMs) are almost not needed any more. NoSQL solutions are advertised as faster, more scalable and easier to use. So who would care about relations, joins, foreign keys and similar stuff (not talking about ACID properties, transactions, transaction isolation)? Who would,  if NoSQLs can make your life much easier. But there is a key insight about NoSQL databases - their wonderful achievements are possible because they made their life easier too is some aspects. But that comes with some price - would you be happy, if your bank will store your saving in MongoDb?

However there are many environments, where NoSQL databases shine - especially when there are huge amounts of simple data structures, which need to be scaled massively across the globe and where these data are not of much value - solutions like social networks, instant messaging etc. are not so much concerned about data consistency or data loss, because these data are basically valueless. (Their business model is just based on sharing absolutely trivial data, where one piece can be easily replaced with another and it does not matter if some pieces are lost. Consider - what will happen if whole Facebook will go away in one minute? Nothing! Few people will be pissed off because they think their online profile was cool, few sad that they cannot share their meaningless achievements with so called 'friends', but generally considered nothing special will happen and no real value will be lost. People will just switch to another provider and fill it's database with tons of trivialities and will easily forget about data in their previous account).

I don't want to create impression that NoSQL databases are useless, they are very good for certain scenarios (and we need to remember that NoSQL is rather broad category, it includes structured documents stores, key-value stores, object databases etc. - each one has it's particular niche, where it excels), but relational databases are also good, actually very good. Relational model is fairly good abstraction of very many real world situations, data structures, entities, however we call them. And relational databases provide solid tools to works with them. So it make sense to use them in many cases. It might bit more difficult to start with relational database then with schema-less document store, but  in the long run it should pay off. And what is really nice it's not about one or another solution, but we can use both and combine them smartly and inventively.
So enough of general mumbo jumbo - let's get to my particular case - I've been looking for data store for my new project and considered to try MongoDb this time ( while in past I stuck to relational DBs), however finally decided for PostgreSQL (again) - and I'd like to share some tests, findings and thoughts.<span id="more-1329"></span>

For data I'll use this relational model (simplified):

<a href="/wp-content/uploads/erd.png"><img alt="erd" class="alignnone size-large wp-image-1334" decoding="async" height="712" loading="eager" sizes="(max-width: 884px) 100vw, 884px" src="/wp-content/uploads/erd-1024x825.png" srcset="/wp-content/uploads/erd-1024x825.png 1024w, /wp-content/uploads/erd-300x242.png 300w" width="884"/></a>

This is basically commonly referred author - book schema (used in many database examples),  but here to make it more real life like the relationship between authors and books is many-to-many.  Data are taken from my previous project <a href="/projects/python/mybookshelf-ebooks-library/">mybookshelf</a> \- approximately 30k+ books and ~10k authors - so relatively small database - but with the real data.

I've played with these 3 set-ups:


<ul>
<li>classical relationship data store - <a href="http://www.postgresql.org/">PostgreSQL</a> 9.5, accessed from python with psycopg2 and <a href="http://www.sqlalchemy.org/">SQLAlchemy </a><a href="https://en.wikipedia.org/wiki/Object-relational_mapping">ORM</a>.</li>
<li><a href="https://www.mongodb.org/">MongoDB</a> 3.2.5 - in order to leverage capabilities of document based approach, data schema is flattened into one document. Mongo is accessed from pymongo.</li>
<li>Use PostgreSQL 9.5 JSONB  type for structured documents -  same flattened schema as in Mongo.</li>
</ul>


By no means these tests should be considered as benchmarks, for that purpose they are too simplistic.  Rather it should be considered as quick peek into particular data stores capabilities.


### Basic stuff


Let's start with something simple (all examples are from IPython notebook running Python 3.4):

Get all ebooks via SQLAlchemy ORM:


```sh
%timeit x=s.query(model.Ebook).all()
1 loop, best of 3: 1.67 s per loop
```


It seems to be be quite slow, what about Mongo?


```sh
%timeit x=list(db.ebooks.find())
1 loop, best of 3: 379 ms per loop
```


Yes, Mongo is significantly faster, however we should not forget that ORM is doing much much more then just loading data - it maps data to objects, observes objects changes, maintains local 'unit of work' context etc. This extra functionality costs us many cycles.  Especially if we work with many objects like here.  However we can always step back to plain SQL:


```sh
%timeit all=list(engine.execute('select * from ebook'))
1 loop, best of 3: 249 ms per loop
```


Here performance is even slightly better then in Mongo. But it does not retrieve details for each book - if we want all details we have to join ebook table with other tables, this is the query ORM executes in background:


```sh
q="""SELECT ebook.id AS ebook_id, ebook.created AS ebook_created, ebook.modified AS ebook_modified, ebook.title AS ebook_title, ebook.description AS ebook_description, ebook.language_id AS ebook_language_id, ebook.series_id AS ebook_series_id, ebook.series_index AS ebook_series_index, ebook.rating AS ebook_rating, ebook.cover AS ebook_cover, ebook.modified_by_id AS ebook_modified_by_id, ebook.created_by_id AS ebook_created_by_id, language_1.id AS language_1_id, language_1.code AS language_1_code, language_1.name AS language_1_name, series_1.id AS series_1_id, series_1.created AS series_1_created, series_1.modified AS series_1_modified, series_1.title AS series_1_title, series_1.rating AS series_1_rating, series_1.description AS series_1_description, series_1.modified_by_id AS series_1_modified_by_id, series_1.created_by_id AS series_1_created_by_id, author_1.id AS author_1_id, author_1.created AS author_1_created, author_1.modified AS author_1_modified, author_1.last_name AS author_1_last_name, author_1.first_name AS author_1_first_name, author_1.description AS author_1_description, author_1.modified_by_id AS author_1_modified_by_id, author_1.created_by_id AS author_1_created_by_id 
FROM ebook JOIN language AS language_1 ON language_1.id = ebook.language_id LEFT OUTER JOIN series AS series_1 ON series_1.id = ebook.series_id LEFT OUTER JOIN (ebook_authors AS ebook_authors_1 JOIN author AS author_1 ON author_1.id = ebook_authors_1.author_id) ON ebook.id = ebook_authors_1.ebook_id ORDER BY author_1.id"""

%timeit cursor.execute(q); x= cursor.fetchall()
1 loop, best of 3: 476 ms per loop
```


OK joins take  time - we know that - but it's not that bad - still roughly comparable with Mongo.

And now let's look at PostgreSQL document solution - selecting from one table with JSONB column ( same JSON data as in Mongo):


```sh
%%timeit
cur.execute('select doc from ebook')
cur.fetchall()
1 loop, best of 3: 772 ms per loop
```


Interesting - why it takes longer then relational model?

In web applications usually we work with fewer records (paginated, sorted) - so let's see how it looks if we limit number of rows and sort them (no index yet):


```sh
%timeit x=session.query(model.Ebook).order_by(model.Ebook.title).limit(100).all()
100 loops, best of 3: 21.8 ms per loop
```




```sh
%timeit x=list(db.ebooks.find().sort([('title', pymongo.ASCENDING)]).limit(100))
100 loops, best of 3: 2.65 ms per loop
```




```sh
%timeit x=list(engine.execute(model.Ebook.__table__.select().order_by('title').limit(100)))
100 loops, best of 3: 2.79 ms per loop
```




```sh
q="""SELECT ebook.id AS ebook_id, ebook.created AS ebook_created, ebook.modified AS ebook_modified, ebook.title AS ebook_title, ebook.description AS ebook_description, ebook.language_id AS ebook_language_id, ebook.series_id AS ebook_series_id, ebook.series_index AS ebook_series_index, ebook.rating AS ebook_rating, ebook.cover AS ebook_cover, ebook.modified_by_id AS ebook_modified_by_id, ebook.created_by_id AS ebook_created_by_id, language_1.id AS language_1_id, language_1.code AS language_1_code, language_1.name AS language_1_name, series_1.id AS series_1_id, series_1.created AS series_1_created, series_1.modified AS series_1_modified, series_1.title AS series_1_title, series_1.rating AS series_1_rating, series_1.description AS series_1_description, series_1.modified_by_id AS series_1_modified_by_id, series_1.created_by_id AS series_1_created_by_id, author_1.id AS author_1_id, author_1.created AS author_1_created, author_1.modified AS author_1_modified, author_1.last_name AS author_1_last_name, author_1.first_name AS author_1_first_name, author_1.description AS author_1_description, author_1.modified_by_id AS author_1_modified_by_id, author_1.created_by_id AS author_1_created_by_id 
FROM ebook JOIN language AS language_1 ON language_1.id = ebook.language_id LEFT OUTER JOIN series AS series_1 ON series_1.id = ebook.series_id LEFT OUTER JOIN (ebook_authors AS ebook_authors_1 JOIN author AS author_1 ON author_1.id = ebook_authors_1.author_id) ON ebook.id = ebook_authors_1.ebook_id ORDER BY ebook.title, author_1.id limit 100"""

%timeit cursor.execute(q); x= cursor.fetchall()
10 loops, best of 3: 110 ms per loop
```


Last result looks bit weird - why joined select takes longer then ORM fetch?  It's  because this query is  suboptimal -  it is better first to limit ebook rows and then join - this is actually what happens in ORM fetch:


```sh
q="""SELECT anon_1.ebook_id AS anon_1_ebook_id, anon_1.ebook_version_id AS anon_1_ebook_version_id, anon_1.ebook_created AS anon_1_ebook_created, anon_1.ebook_modified AS anon_1_ebook_modified, anon_1.ebook_title AS anon_1_ebook_title, anon_1.ebook_description AS anon_1_ebook_description, anon_1.ebook_language_id AS anon_1_ebook_language_id, anon_1.ebook_series_id AS anon_1_ebook_series_id, anon_1.ebook_series_index AS anon_1_ebook_series_index, anon_1.ebook_rating AS anon_1_ebook_rating, anon_1.ebook_cover AS anon_1_ebook_cover, anon_1.ebook_modified_by_id AS anon_1_ebook_modified_by_id, anon_1.ebook_created_by_id AS anon_1_ebook_created_by_id, language_1.id AS language_1_id, language_1.version_id AS language_1_version_id, language_1.code AS language_1_code, language_1.name AS language_1_name, series_1.id AS series_1_id, series_1.version_id AS series_1_version_id, series_1.created AS series_1_created, series_1.modified AS series_1_modified, series_1.title AS series_1_title, series_1.rating AS series_1_rating, series_1.description AS series_1_description, series_1.modified_by_id AS series_1_modified_by_id, series_1.created_by_id AS series_1_created_by_id, author_1.id AS author_1_id, author_1.version_id AS author_1_version_id, author_1.created AS author_1_created, author_1.modified AS author_1_modified, author_1.last_name AS author_1_last_name, author_1.first_name AS author_1_first_name, author_1.description AS author_1_description, author_1.modified_by_id AS author_1_modified_by_id, author_1.created_by_id AS author_1_created_by_id 
FROM (SELECT ebook.id AS ebook_id, ebook.version_id AS ebook_version_id, ebook.created AS ebook_created, ebook.modified AS ebook_modified, ebook.title AS ebook_title, ebook.description AS ebook_description, ebook.language_id AS ebook_language_id, ebook.series_id AS ebook_series_id, ebook.series_index AS ebook_series_index, ebook.rating AS ebook_rating, ebook.cover AS ebook_cover, ebook.modified_by_id AS ebook_modified_by_id, ebook.created_by_id AS ebook_created_by_id 
FROM ebook ORDER BY ebook.title 
 LIMIT 100) AS anon_1 JOIN language AS language_1 ON language_1.id = anon_1.ebook_language_id LEFT OUTER JOIN series AS series_1 ON series_1.id = anon_1.ebook_series_id LEFT OUTER JOIN (ebook_authors AS ebook_authors_1 JOIN author AS author_1 ON author_1.id = ebook_authors_1.author_id) ON anon_1.ebook_id = ebook_authors_1.ebook_id ORDER BY anon_1.ebook_title, author_1.id"""

%timeit list(engine.execute(q))
100 loops, best of 3: 5.64 ms per loop
```


That's better - Mongo is still faster, but not so much.


### Complex query


Now let's try a complex search across several attributes -  returns records where all words are found either in book title,  series or authors name:


```python
def build_search_expr(q):
    def create_and(field):
        return and_(*map(lambda v: func.unaccent(field).ilike(v),q))
    q=map(lambda x: x.strip(), q.split())
    q=list(map(lambda x: func.unaccent('%%%s%%'%x),q))
    return or_(create_and(model.Ebook.title), create_and(model.Series.title), 
               create_and(func.concat(model.Author.first_name, ' ',  model.Author.last_name)))

def build_search(session,q):
    return session.query(model.Ebook).outerjoin(model.Author, model.Ebook.authors)\
    .outerjoin(model.Series).filter(build_search_expr(q))
```




```sh
%timeit build_search(session,'karel capek')\
.limit(5).all()
10 loops, best of 3: 39.5 ms per loop
```


and Mongo equivalent:


```python
def mongo_build_search(q):
    def create_and(field):
        return {'$and': list(map(lambda x: {field:{'$regex':x,'$options': 'i'}},q))}
    def create_and2(field, field2):
        return {'$and': list(map(lambda x: {'$or':[{field:{'$regex':x,'$options': 'i'}}, {field2:{'$regex':x,'$options': 'i'}}]},q))}
    q=list(map(lambda x: x.strip(), q.split()))
    return {'$or':[create_and('title'), create_and('series'), create_and2('authors.lastname', 'authors.firstname')]}
```




```sh
%timeit list(c.ebooks.ebooks.find(mongo_build_search('karel čapek'))[:5])
The slowest run took 179.87 times longer than the fastest. This could mean that an intermediate result is being cached.
1 loop, best of 3: 2.71 ms per loop

```


Mongo is again faster, but PostgreSQL solution is better, because it searches without diacritics (something very important for us living in the middle Europe).  I did not find any easy way how to do it in Mongo (only in full text search - which is discussed below).

Again ORM has some extra costs, but even direct SQL query is slower then Mongo:


```sh
q=select([ebook]).select_from(ebook.outerjoin(series).outerjoin(ebook_authors).join(author)).where(build_search_expr('karel capek'))
%timeit list(engine.execute(q.limit(5)))
100 loops, best of 3: 12.9 ms per loop
```


We can do same query also for PostgreSQL JSONB documents:


```python
def build_search_expr(q):
    def create_and(field):
        return " and ".join(map(lambda v: "unaccent(%s) ilike %s"%(field,v),q))
    q=map(lambda x: x.strip(), q.split())
    q=list(map(lambda x: "unaccent('%%%s%%')"%x,q))
    terms=[create_and("b.doc->>'title'"), create_and("b.doc->>'series'"), 
           create_and("concat(a.value->>'firstname', ' ', a.value->>'lastname')")]
    return ' or '.join(terms)
           
print (build_search_expr('karel capek'))
```




```sh
%%timeit
search="karel čapek"
cur.execute("select b.id, b.doc from ebook b, jsonb_array_elements(b.doc->'authors') a where %s limit 5" % \
           build_search_expr(search))
cur.fetchall()
The slowest run took 184.14 times longer than the fastest. This could mean that an intermediate result is being cached.
1 loop, best of 3: 2.13 ms per loop
```


So even faster then Mongo and with diacritics insensitive match. But  note about caching in result would be probably true, because if  I try similar query without limit (there are approximately 50 matches in total), query takes much longer:


```sh
search="karel čapek"
cur.execute("select b.id, b.doc from ebook b, jsonb_array_elements(b.doc->'authors') a where %s" % \
           build_search_expr(search))
cur.fetchall()
1 loop, best of 3: 364 ms per loop
```


while Mongo is faster for all results:


```sh
%timeit list(c.ebooks.ebooks.find(mongo_build_search('karel čapek')))
10 loops, best of 3: 96.9 ms per loop
```




###  Full Text Search


Both Mongo and PostgreSQL offer full text search. In PostgreSQL a column (full\_text) was added to ebook table containing full text search data (TSVECTOR), concatenation of  title, series title and all authors names. Both PostgreSQL and Mongo use full text index and support case insensitive, diacritics insensitive search.


```sh
%%timeit
search="capek & karel"
session.query(model.Ebook).filter(model.Ebook.full_text.match(search))\
.order_by(desc(func.ts_rank_cd(model.Ebook.full_text, func.to_tsquery(text("'custom'"), search))))\
.all()
100 loops, best of 3: 15.8 ms per loop
```


Again we can assume there is significant ORM overhead, let's look at pure sql query:


```sh
search='capek & karel'
q=select([ebook]).where(text("full_text @@ to_tsquery('custom', '%s')"%search)).order_by(text("ts_rank_cd(full_text, to_tsquery('custom', '%s')) desc"%search))

%timeit list(engine.execute(q))
100 loops, best of 3: 2.86 ms per loop
```


And Mongo:


```sh
%%timeit
list(client.ebooks.ebooks.find({"$text":{"$search":"karel capek"}},
                          projection={"score":{"$meta":"textScore"}},
                             sort=[("score", {"$meta": "textScore"})] ))
100 loops, best of 3: 10.5 ms per loop

```


In fulltext search PosgreSQL is faster.


### Updates


I was focused mostly on queries - because my use case will be mostly read orientated, but could not resist to test updating author name, where I expected relational database to  really excel due to it's data representation.


```sh
%%timeit -n1 -r1
a=session.query(model.Author).filter_by(first_name='Karel', last_name='Čapek').one()
a.first_name='Karlicek'
session.commit()
1 loop, best of 1: 55.1 ms per loop
```


Nor so fast, what about Mongo?


```sh
%%timeit -n1 -r1
res=client.ebooks.ebooks.update_many({'authors.lastname':'Čapek', 'authors.firstname':'Karel'}, 
{'$set':{'authors.$.firstname': 'Karlicek'}})
1 loop, best of 1: 6.58 ms per loop
```


Ooops - why PostgreSQL is so slow - maybe it's again ORM part. Let's look at pure SQL update:


```sh
conn=engine.connect()
%timeit -n1 -r1 conn.execute("update author set first_name='Karel' where last_name='Čapek' and first_name='Karlicek'")
conn.close()
1 loop, best of 1: 53.2 ms per loop
```


OK it looks like update time is spent in the database. Well done Mongo,  I did not really expect so fast updates.


### PostgreSQL JSONB Fun


PostgreSQL offers many useful  operators and functions, with which we can create different queries - functionality is roughly comparable with Mongo.  Few examples below:

@\> operator find document containing given json:


```sh
%%timeit    
cur.execute("""select doc->'title' from ebook where doc @> '{"authors":[{"lastname":"Adams"}]}'::jsonb limit 5""")
cur.fetchall()
The slowest run took 2734.04 times longer than the fastest. This could mean that an intermediate result is being cached.
1 loop, best of 3: 167 µs per loop
```


That's superfast, compare with Mongo:


```sh
%timeit list(client.ebooks.ebooks.find({"authors.lastname":"Adams"}).limit(5))
The slowest run took 29.50 times longer than the fastest. This could mean that an intermediate result is being cached.
1000 loops, best of 3: 318 µs per loop
```


\-\>\> extracts text and can be used for instance  in where clause:


```sh
%%timeit
cur.execute("""select doc->'title' from ebook where doc->>'title' ilike 'ca%' """)
cur.fetchall()
10 loops, best of 3: 41.6 ms per loop
```


we can use join on JSONB array to get distinct authors:


```sh
%%timeit
cur.execute("""select  distinct a.value->>'lastname', a.value->>'firstname' from ebook b, jsonb_array_elements(b.doc->'authors') a 
""")
list(cur)
10 loops, best of 3: 96.3 ms per loop
```


or use it to get count of books per author:


```sh
%%timeit
cur.execute("""select  a.value->>'lastname' as lastname, a.value->>'firstname', count(b.id) as num_books from ebook b, jsonb_array_elements(b.doc->'authors') a 
group by a.value order by lastname
""")
list(cur)[:10]
10 loops, best of 3: 133 ms per loop
```


And we can do much more ...


### Conclusion


There are many different databases and they differ much in functionality and targeted usage. Despite of current  popularity of NoSQL databases, traditional relational databases (RDBMs) are viable solutions for many applications storage needs including dynamic web applications. RDBMs are rock solid and proven in many battles. They are know to be reliable and scalable.
Just performance should not be the main selection criteria,  unless such performance is really and truly needed. RDBMs can offer much in area of reliability and data consistency. Neither ease of use should be overestimated - there is a good reason why relational databases are more complex.
I personally would prefer RDMS like PostgreSQL as a default choice, unless there is very good reason to use other (NoSQL) database.  And even in these cases, not all data must go to other database - we can use it for instance as a 'data cache'   for fast reads from replicated servers.
And when looking for document based stores or key-value stores, we do not have to leave PostgreSQL environment, because it provides very solid solutions also in this area (JSONB and HSTORE).

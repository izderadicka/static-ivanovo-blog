+++
title = "Sqlite3 - How Slow Is Write?"
path = "/sqlite3-how-slow-is-write/"
date = "2018-10-23T13:58:13"
include_in_feeds = true
[extra]
wordpress_id = 1954
kind = "post"
node_key = "1954"
author = "admin"
source_url = "http://zderadicka.eu/sqlite3-how-slow-is-write/"
source_guid = "http://zderadicka.eu/?p=1954"
source_date_gmt = "2018-10-23 12:58:13"
categories = ["Programming"]
tags = ["Rust", "sqlite3"]
+++
<a href="https://www.sqlite.org">Sqlite3</a> is lightweight relational database, mainly focused on smaller local systems. Being used in Android it's now probably most spread relational database in world with billions of instances running. Lite in the name means that it is not client-server architecture and it's intended for lower data volumes - ideal usage profile is <a href="https://www.sqlite.org/whentouse.html">read mostly, with occasional writes</a>. Sqlite3 is often used as an embedded data store in various applications (Firefox and Chrome are most prominent ones). Recently I've been playing a bit with sqlite3 interface in Rust and had run couple of simple tests especially focused on writes. So how does sqlite3 performs and how it compares with other more typical client-server RDBMS like PostgreSQL?  It's not any serious benchmark, just couple of toy tests to highlight few things.<span id="more-1954"></span>

So I started with testing highly concurrent load of independent writes into one table - 10 thousand inserts from independent tasks (running in thread pool and using connection pool) - see code below:


```rust
extern crate chrono;
extern crate r2d2;
extern crate r2d2_sqlite;
extern crate threadpool;

use chrono::prelude::*;
use threadpool::ThreadPool;
use std::time::Duration;

#[derive(Debug)]
struct Person {
    id: i32,
    name: String,
    time_created: DateTime<Local>,
    data: Option<Vec<u8>>,
}

fn main() {
    let _ = std::fs::remove_file("my_test_db");
    let manager = r2d2_sqlite::SqliteConnectionManager::file("my_test_db");
    let pool = r2d2::Pool::builder().max_size(5).build(manager).unwrap();

    {
        let conn = pool.get().unwrap();
        assert!(conn.is_autocommit());
        let mut check_stm = conn
            .prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?1;")
            .unwrap();

        if !check_stm.exists(&[&"person"]).unwrap() {
            //conn.execute_batch("pragma journal_mode=WAL").unwrap();
            conn.execute(
                "CREATE TABLE person (
                  id              INTEGER PRIMARY KEY,
                  name            TEXT NOT NULL,
                  time_created    TEXT NOT NULL,
                  data            BLOB
                  )",
                &[],
            )
            .unwrap();
        }
    }

    let thread_pool = ThreadPool::new(4);

    for i in 0..10_000 {
        let pool = pool.clone();

        thread_pool.execute(move || {
            let me = Person {
                id: 0,
                name: format!("Usak{}", i),
                time_created: Local::now(),
                data: None,
            };
            let conn = pool.get().unwrap();
            conn.busy_timeout(Duration::from_secs(600)).unwrap();
            conn.execute(
                "INSERT INTO person (name, time_created, data)
                  VALUES (?1, ?2, ?3)",
                &[&me.name, &me.time_created, &me.data],
            )
            .unwrap();
        });
    }

    thread_pool.join();
    let conn = pool.get().unwrap();

    let mut stmt = conn
        .prepare("SELECT count(*) FROM person")
        .unwrap();
    let mut query = stmt.query(&[]).unwrap();
    let count: i32 = query.next().unwrap().unwrap().get(0);
    assert_eq!(count, 10_000);
}

```


As expected performance was very bad. Actually initially many tasks/threads panicked with "busy/database locked" error.  As all writes to sqlite3 database has to be serialized (using lock on db), concurrent threads have been competing for the lock and some were less lucky and timeouted before  acquiring the lock.  Extending `conn.busy_timeout` helped, but performance was still very poor.  But there was one possibility to improve performance - to use different journal mechanism for slqlite3 database. It's not so well known than sqlite3 has two mechanism for database journal (journals are used for data consistency and atomic commits) - default is <a href="https://www.sqlite.org/atomiccommit.html">rollback journal</a>, but it also enables <a href="https://www.sqlite.org/wal.html">write ahead log</a> (WAL) journal. WAL journal can be enabled explicitly by pragma  ` "pragma journal_mode=WAL"  `(commented in previous code - see line 31). If we change journal mode to WAL (uncomment line 31), we can see significant improvement in performance, but it's still pretty slow.

Problem here is sqlite3 is not designed for intensive concurrent write operations, more real live scenario would be that just one thread is filling the data and it inserts/updates many records in single transaction:


```rust
extern crate chrono;
extern crate rusqlite;
extern crate threadpool;

use chrono::prelude::*;
use std::time::Duration;
use rusqlite::Connection;
use std::thread;

#[derive(Debug)]
struct Person {
    id: i32,
    name: String,
    time_created: DateTime<Local>,
    data: Option<Vec<u8>>,
}

fn main() {
    let _ = std::fs::remove_file("my_test_db");
    let conn = Connection::open("my_test_db").unwrap();

    {
        assert!(conn.is_autocommit());
        let mut check_stm = conn
            .prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?1;")
            .unwrap();

        if !check_stm.exists(&[&"person"]).unwrap() {
            conn.execute_batch("pragma journal_mode=WAL").unwrap();
            conn.execute(
                "CREATE TABLE person (
                  id              INTEGER PRIMARY KEY,
                  name            TEXT NOT NULL,
                  time_created    TEXT NOT NULL,
                  data            BLOB
                  )",
                &[],
            )
            .unwrap();
        }
    }

    let thread = thread::spawn(move || {
        let mut conn = Connection::open("my_test_db").unwrap();
        conn.busy_timeout(Duration::from_secs(60)).unwrap();
        let t = conn.transaction().unwrap();

    for i in 0..10_000 { 
            let me = Person {
                id: 0,
                name: format!("Usak{}", i),
                time_created: Local::now(),
                data: None,
            };
            
            t.execute(
                "INSERT INTO person (name, time_created, data)
                  VALUES (?1, ?2, ?3)",
                &[&me.name, &me.time_created, &me.data],
            )
            .unwrap();
        }
        t.commit().unwrap();
    });

    thread.join().unwrap();
    let mut stmt = conn
        .prepare("SELECT count(*) FROM person")
        .unwrap();
    let mut query = stmt.query(&[]).unwrap();
    let count: i32 = query.next().unwrap().unwrap().get(0);
    assert_eq!(count, 10_000);

}
```


As you can verify above code is at least by order of magnitude faster then previous attempt (see also table below -first vs last column). But what if we forgot to use transaction in this case? By default connection is in auto commit mode, so each insert is committed individually.  Quick check shows that then we are back at lousy performance (see table below - middle column) - basically comparable with writing in concurrent tasks. So it is not so much about concurrency, but commits in sqlite3 are expensive.

And how does sqlite3 compares with fully bodied database like <a href="https://www.postgresql.org/">PostgresSQL</a> ( I used basically same code as above, just changed for rust-postgres crate):


```sh
/----------------------------------------------------\
|           |10k tasks  |10k inserts |insert 10k recs|
|===========|===========|============|===============|
|pg         | ~ 5.6 secs| ~ 13 secs  | ~ 1.7 secs    |
|sqlite wal | ~ 1.5 mins| ~ 1.5 mins | ~ 0.3 secs    |
|sqlite rb  | ~ 14 mins | ~ 13.5 mins| ~ 0.3 secs    |
\____________________________________________________/
```


(Only bear in mind that measurements are approximate, informative, done by time command only)

As you can see postgres (first line - pg) is significantly faster for many inserts. You can see that it even can leverage concurrency (more the two times faster when inserts are run in concurrent threads).  But for one transcation (10k inserts in one transaction), sqlite3 is faster, benefiting probably from simple architecture (no client server).

Some conclusions:


<ul>
<li>If you writing a lot of records in sqlite3, try to write them in one transaction - it really helps.</li>
<li>Many independent writes performs badly in sqlite3. For write intensive database consider something else.</li>
<li>But for many types of applications sqlite3 is very good solution - it's proven, robust and performs well, when used appropriately.</li>
</ul>

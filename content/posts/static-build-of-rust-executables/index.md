+++
title = "Static Build of Rust Executables"
path = "/static-build-of-rust-executables/"
date = "2019-03-20T18:57:35"
include_in_feeds = true
[extra]
wordpress_id = 2011
kind = "post"
node_key = "2011"
author = "admin"
source_url = "http://zderadicka.eu/static-build-of-rust-executables/"
source_guid = "http://zderadicka.eu/?p=2011"
source_date_gmt = "2019-03-20 17:57:35"
categories = ["Programming"]
tags = ["linux", "Rust", "static executable"]
+++
Recently I wanted to create completely static build of <a href="https://github.com/izderadicka/audioserve">audioserve</a> \- so it can be easily moved and  run on any modern 64bit linux without any other actions. Rust provides some guidelines for static building, but it still took me some time to make it work, mainly due to dependencies on other C/C++ libraries (libssl, libavformat ...). So here I my experiences:<span id="more-2011"></span>


#### How rust compiler links by default




<ul>
<li>Pure Rust dependencies are linked statically into final executable</li>
<li>Rust executable is dependent of few very core linux libraries (libc, libdl, ....), which are linked dynamically</li>
<li>If a Rust crate is dependent on other C/C++ libraries (called native in Rust lingo),  they are linked dynamically (unless crate already has  linked it statically to it's code object as part of it's build process)</li>
</ul>


This means that normally you'll end up with dynamically linked executable, which depends on few dynamic libraries, if you want completely static binary you need to put an extra effort into building.


#### How to link statically


In order to create completely static executable you must use special target platform as explained <a href="https://doc.rust-lang.org/1.7.0/book/advanced-linking.html">here</a> and also <a href="https://doc.rust-lang.org/edition-guide/rust-2018/platform-and-target-support/musl-support-for-fully-static-binaries.html">here</a> \- in short we must build against standard library build with<a href="https://www.musl-libc.org/"> musl c</a> library and not gnu c library. The target `platfom x86_64-unknown-linux-musl` provides this.

RECENT CHANGE:  <a href="https://github.com/rust-lang/compiler-team/issues/422">musl targets are now also by default linking libmuslc  dynamically</a>. So these compiler options must be added for static linking


```
-C target-feature=+crt-static -C link-self-contained=yes
```


So far it looks fairly easy, but complications come, if you try to link other native (C/C++) libraries - they have to be also build against  musl libc - otherwise you'll see some strange undefined symbols during the linking (and I guess this is the better case, really not sure what will happen if two different libc libraries are arbitrary mixed).

If you will use above mention target on your usual linux (debian, ubuntu, centos etc.), where everything is based on gnu libc, it means that you'll have to install additions to gcc (to compile against musl libc) and then  recompile needed libraries from source ( which can be pretty demanding for complex libraries) - see this approach in this <a href="https://github.com/emk/rust-musl-builder/blob/master/Dockerfile">Dockerfile</a>.

Luckily there is an easier approach - <a href="https://alpinelinux.org/">alpine linux</a> \-   where everything is already build against musl libc.  Rust on this platform has default target  `x86_64-alpine-linux-musl` , which is also dynamically linked by default.  There has been some <strong>recent change</strong> so I was not able to to convince this target to build binary statically even with above mentioned flags. So after bit of struggle I used target ` x86_64-unknown-linux-musl, for  `which I have to use external rust toolchain installed via rustup (so not using packed rust via apk). <code></code>

And we need to do one more thing for static linking of  native dependency like `openssl-dev`. If you remember, what was noted above,  dependent native libraries are linked dynamically unless specified otherwise. Easiest way to change this  is to create build.rs in root of your project, which will hint compiler about static linking:


```rust
fn main() {
    #[cfg(feature="static")]
    {
    println!("cargo:rustc-link-lib=static=ssl");
    println!("cargo:rustc-link-lib=static=crypto");
    }
}
```


As you can see here static linking is hidden behind feature static, so I can easily also build dynamically linked version of binary if required.  Above mentioned cargo directives map then to -l flags for compiler.

Above described approach assumes that statically linkable libraries (.a) are in the dev package. This is true for many dev packages, but not for all (alpine linux now have special packages for static libraries - ending with -static suffix) - for  ffmpeg libraries (libavformat ...) I had to build them from source to have statically linkable objects. If libraries are in non standard place, then compiler has to be also advised, where to find them ( -L compiler flags), which can be easily done by adding


```rust
println!("cargo:rustc-link-search=native=some/directory");
```


to the build.rs file.

Another complication can appear in case when your project depends on crate that itself depends on native libraries. The compilation of that crate is driven by it's Cargo.toml and build script, so optimally they need to have feature to enable static build.  If not you can try to add additional -L and -l options to exported RUSTFLAGS env. variable and thus force static linking for given native libraries.  For instance this worked for me for static linking of rust\_icu\_col (which is using several native C libraries):


<div>
<div>
<pre class="code-highlight" data-language="bash"><code><span class="code-line"><span class="nb">export</span><span class="w"> </span><span class="nv">RUSTFLAGS</span><span class="o">=</span><span class="nv">$RUSTFLAGS</span><span class="s2">&quot; -L native=/usr/lib -l static=clang -l static=icui18n -l static=icuuc -l static=icudata -l static=stdc++&quot;</span></span></code></pre>
</div>
</div>


So to put this together:


<ul>
<li>create <strong>build.rs</strong> file in root of you project and output there appropriate directives for static linking - sample build file (from audioserve project) is for instance <a href="https://github.com/izderadicka/audioserve/blob/master/build.rs">here</a></li>
<li>create a <strong>docker image from alpine linux</strong> where you install rust stack with rustup, sample Dockerfile is <a href="https://github.com/izderadicka/audioserve/blob/master/Dockerfile.static">here</a></li>
<li>image runs some simple build script like <a href="https://github.com/izderadicka/audioserve/blob/master/_build_static.sh">this one</a>. Important is to compile against <strong>*-musl target</strong> and have <strong>compiler</strong> <strong>arguments</strong> <code>"-C target-feature=+crt-static -C link-self-contained=yes"</code> set up (in our case already setup via ENV RUSTFLAGS in the image)</li>
<li>for dependencies on <strong>native libraries</strong>, first you need to assure that static version of libraries (*.a) are available and then either add appropriate rust directives to build.rs script (if you control the build of your crate, ideally this should be behind a feature).  Or you can export RUSTFLAGS with appropriate additional -l and -L flags.</li>
</ul>

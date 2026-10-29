+++
title = "Plugins in OCAML with Dynlink library"
path = "/plugins-in-ocaml-with-dynlink-library/"
date = "2014-10-25T09:28:47"
include_in_feeds = true
[extra]
wordpress_id = 919
kind = "post"
node_key = "919"
author = "admin"
source_url = "http://zderadicka.eu/plugins-in-ocaml-with-dynlink-library/"
source_guid = "http://zderadicka.eu/?p=919"
source_date_gmt = "2014-10-25 08:28:47"
categories = ["Programming"]
tags = ["OCaml"]
+++
I slowly continue with learning of OCAML -  as a training project I work on  <a href="https://github.com/izderadicka/mapred">simplified Map-Reduce framework</a> (utilizing Core and Async libraries).   Here I had a need to plug  a selectable code (map reduce algorithm) to main program.   Ocaml provides <a href="http://caml.inria.fr/pub/docs/manual-ocaml/libref/Dynlink.html">Dynlink</a> library, which can dynamically link either byte-code or native object/library to running program.  This can be utilize to create simple plugin framework as explained below.<span id="more-919"></span>

Key function is `Dynlink.loadfile`, which can load .cmo/cma (bytecode) or .cmxs file (native code) from given file.  Loaded modules cannot be referenced from main program, so they must register themselves in defined extension points in main program during their load, where all code in plugin modules is executed. Key insight here (which is not well documented) is that loaded modules can reference only fully evaluated modules in main program - e.g. <span style="text-decoration: underline;">they cannot reference module, which is loading them</span>.

In combination with first-class modules, we can build a plugin system with well defined interfaces. Below is simplified example how it may look like:

<strong>dtest_ep.ml</strong>:


```sh
module type PLUG =
	sig
		val hello: unit -> string
	end
	
let p = ref None
let get_plugin () : (module  PLUG)  =
	match !p with 
	| Some s -> s
	| None -> failwith "No plugin loaded"
	
	

```


Here we define interface `PLUG`  of the plugin, variable `p` which will hold refrerence to plugin implementation (as first class module option) and function `get_plugin`.

dtest.ml:


```sh
open Dtest_ep

let load_plug fname = 
  let fname = Dynlink.adapt_filename fname in
  if Sys.file_exists fname then
		try
			Dynlink.loadfile fname
		with 
		| (Dynlink.Error err) as e -> 	 print_endline ("ERROR loading plugin: " ^ (Dynlink.error_message err) ); raise e
		| _ -> failwith "Unknow error while loading plugin"
	else 
	  failwith "Plugin file does not exist"
		

let () =
	load_plug "/home/ivan/workspace/mapred/tests/_build/dtest_plug.cmo";
	let module M = (val get_plugin () : PLUG) in
	print_endline (M.hello ())
```


This is main program - it contain function to load plugin and in main code uses plugin as module `M`.

<strong>dtest_plug.m</strong>l:


```sh
open Dtest_ep

module M:PLUG =
	struct
		let hello () = "Hello, World!"
	end
	
	
let () = 
 p := Some (module M:PLUG)


```


And this file is implementation of the plugin.

We can compile with:


```sh
ocamlbuild -lib dynlink dtest_plug.cmo dtest.byte
ocamlbuild -lib dynlink dtest_plug.cmxs dtest.native

```


Plugin should be compiled against same version of interfaces as main program.


#### External modules in plugins


Plugin can use other external modules,  but then it gets bit more tricky,  if these modules not linked in main program -  you'll get 'Unknown Global X'  error  during dynamic linking of the plugin.

Solution is either to force module(s) to be linked in main program (`  let _ = X.y  `) or load required libraries with `Dynlink.loadfile` (dynamically loaded modules will be visible from the plugin, but not to main program).   Other option is to pack plugin with dependent object into one library file - I have not tested it, but I assume this should work.
I experienced Interesting behaviour when plugin ligrary contains same module as main program. In this case module from plugin library is loaded and linked to the plugin and hides module from main program.
For our sample above it means, if plugin will be packed in .cma file with Dtest\_ep module object,  plugin will not be able to register itself,   because Dtest\_ep from main program will be hidden from it.


####

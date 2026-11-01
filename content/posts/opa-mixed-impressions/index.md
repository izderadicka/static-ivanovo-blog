+++
title = "Opa - Mixed Impressions"
path = "/opa-mixed-impressions/"
date = "2015-02-23T12:03:12"
include_in_feeds = true
[extra]
wordpress_id = 983
kind = "post"
node_key = "983"
author = "admin"
source_url = "http://zderadicka.eu/opa-mixed-impressions/"
source_guid = "http://zderadicka.eu/?p=983"
source_date_gmt = "2015-02-23 11:03:12"
[taxonomies]
category = ["Programming"]
tag = ["Opa", "web framework"]
+++
Coming little bit late to [Opa](http://opalang.org/) (looks like real hype was  couple years ago), I  was still caught by this interesting new language.  Opa is a new language - cross-over between JavaScript ( providing JS like syntax) and [OCaml](http://ocaml.org/) (using  many functional programming idioms from that language , plus Opa complier is written in OCaml). Opa is used  solely to program web applications -  so Opa is both language and web framework. Opa compiles to JavaScript,  which on client side runs in a browser and on server side in [node.js](http://nodejs.org/). You write just one Opa code and compiler decided, where the code should run.

I have spent some time looking into Opa recently - mainly trying some of Opa tutorial plus and doing some small experiments myself and I'd like to share my experiences and impressions.<span id="more-983"></span>


## Documentation, Tutorials


I think documentation is one of biggest pains of Opa.  Online documentation is scarce and focused mostly on basics,  reference documentation for standard library is missing! (There used to be one,  but it disappeared half year ago -  now the recommendation is to use source code of standard library - see [this](https://github.com/MLstate/opalang/issues/158)).

There are also two books [Opa: Up And Running from O'Reilly ](http://shop.oreilly.com/product/0636920025436.do)(which is kind of 'official guide' to Opa) and [Opa Application Development from Packt](https://www.packtpub.com/application-development/opa-application-development). But both books suffer same issues as online documentation -   they provide only shallow overview of the language and former also contains a lot of  errors in code samples.

I think that Opa will not attract inexperienced web developers, who would rather try some well established language and framework first,   so effort put to explain some basic web development concepts in both books is rather waisted.  What is really missing is solid, easily navigable  reference documentation, which could one use when working with Opa.


## Installation


Installation for Linux platform is done by [compilation from source](https://github.com/MLstate/opalang/wiki/Building-Opa).  It went relatively OK (I have problem with latest OCaml 4.02,  but this was fixed  meanwhile).  As Opa  is written in Ocaml,  Ocaml compiler and related tools are needed.  If dependent ocaml libraries are installed via OPAM, you should use `configure` script with `-ocamlfind <path>` option.


### Tools, Editors


After installation there is `opa` multifunctional tool, which works as compiler, but can also create new project or start  a web server. `opa` tool works  fine,  its command line help can give idea about available options.

There is  Opa support for these 3 editors - Emacs, SublimeText and vim (there was also an attempt to make Eclipse plugin, but it looks like not working, haven't been updated for 4 years, so I did not bother to give it a try, even tough I'm a big Eclipse fan).

I used Emacs, Opa provides some ELisp code for new major mode "Opa-Js" with code highlighting.
For inline compilation I had to add regular expression to recognize compilation error messages:


```lisp
(add-to-list 'compilation-error-regexp-alist 'opa)
(add-to-list 'compilation-error-regexp-alist-alist
       '(opa "File \"\\([^\"]+\\)\", line \\([0-9]+\\), characters \\([0-9]+\\)"
           1 2 3))

```


(above should be added to emacs init)

There was some quite annoying bug in indentation of code, appearing in case normal code and xhmtl is combined. Then is some situations, line is automatically indented by one tab with each new bracket  character written. Probably could be fixed easily by experienced Emacs programmer,  which I'm not.


##  Language, Features


First interesting thing to note about Opa is that language has two possible syntax variations - classic and JS-like. Former is older and there is no documentation for it now,  all available documentation is for newer JS-like syntax.  However vast majority of Opa standard library is written older classic syntax,   so if you are looking into code ( which you must because of missing referential documentation),  you should somehow get to understand older classic syntax too.

The main difference between both is that classic syntax is closer to Ocaml,  while new syntax is closer to JavaScript. Compiler supports both, with JS-like syntax being default, so I assume they both compile to same [AST](http://en.wikipedia.org/wiki/Abstract_syntax_tree).

Generally Opa is functional  programming language with a lot of syntactic sugar to support web programming.  This makes resulting code very concise and nice looking. This is definitely one of key attractions of Opa.  Just one sample to illustrate this:


```javascript
max=10
Random.random_init()


function show_result(secret, _) {
    guess = String.to_int(Dom.get_value(#guess))
    if (guess == secret) { 
	#hint= <span class=correct>You got it!</span>
	    Dom.hide(#btn)
    }
    else if (guess < secret) {#hint= "Bellow" }
    else { #hint="Above" }
    
}

function page() {
    secret = 1 + Random.int(max)
	<h1>Guess number between 1 to {max}</h1>
	<input id="guess"/>
	<a id=#btn onclick={show_result(secret,_)}>Guess</a>
	<div id="hint"/>
}

Server.start(
    Server.http,
    {title: "Guess game",
     page: page
    }
)
```


Above code is a very simple number guessing game.

Another shining feature is type inference - Opa is statically typed, but in majority of cases types do not have to be explicitly declared and still compiler assures type safety of your program.  The record and sum (variant) types are very powerful, as described [here](http://hbbio.tumblr.com/post/31526019499/power-rows-the-datatype), giving more powerful type manipulations then for instance in OCaml.

However on the other hands type inference can give sometime very cryptic error message during compilation- like this one:


```sh
Sum type with row and column variables { path: list(string); 'r.a } / 'c.a
Error: File "src/controller/main.opa", line 6, characters 9-11, (6:9-6:11 | 127-129)
Exportation failure
```


Which finally turned out  compiler's complain that it cannot infer type for variable in a match expression - it was enough to add type to that variable and code compiled OK.  Generally majority of weird compile errors I saw in Opa were somehow related to type inference. (But syntactic errors were also sometimes hard to decipher too).

Although Opa syntax might remind JavaScript, actually language is much closer to OCaml with majority of functional goodies (including immutable values, first class functions, function partial application, higher order functions, operators as functions etc.) available.  So experiences from Ocaml came quite handy.

As I already noted in introduction you are writing just one Opa code, which is automatically sliced by compiler between client and server.  The default rule is to make it available on both sides, if possible. If not then move it to where it will work. Programmer has also possibility to explicitly set where function is defined via specific keywords (server, client, both).  Automatic code slicing can be very convenient, however it can lead to less performer application with extensive client - server communication. I'll touch it latter because it seems to be a serious issue for current version of Opa.

Standard library looks to be rich and complete enough to write complex applications,  however without reference documentation it's hard to navigate it, especially when some functions have specific names ( string split is called `explode_with` in Opa).

External JavaScript libraries can be easily used from Opa ( just need to create and interface file(s) with type annotations).

As a web framework Opa offers standard [MVC](http://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) pattern. Model data can persist in [mongodb](http://www.mongodb.org/) NOSQL database.  Opa extends its syntax to provide easy access to database as a part of the core language.  This is very convenient, however this extension seems to be crafted to match mongodb capabilities. So I'm not sure if it can work well with other database backends (Opa supports also PostgreSQL sever, but I did not test it- it's not documented,  probably it's rather basic - I doubt it can support more advanced SQL features like joins). For controller part Opa offers flexible ways to route web requests to appropriate functions -  you can use either pattern matching or regular expression on relative path.  On view side Opa provides integration with  [Boostrap](http://getbootstrap.com/) framework, I18N support,  forms support, convenient DOM manipulation and more,  but again problem is to understand what is available due to missing reference documentation (for instance it took me some time to understand how to create a select input in a form - for this I have to visit and read two source files in standard library).

Another great feature of Opa for views building is its syntactic extension, which enables to directly include XHTML into code and vice versa include Opa expressions in this XHTML.  This provides equivalent functionality to templating, which is common in many other web frameworks, but with higher safety/correctness assurance.

Opa also provides functions for advanced messaging between client and server - one or two way channels between client and server, including support for broadcasting messages to all clients.  This enables to build interactive web applications very easily. See the [chat application tutorial](https://github.com/MLstate/opalang/wiki/Hello%2C-chatb) for practical example.


## Deployment, Running, Performance


During development and testing it's very easy to compile and run application via one opa command invocation.  Opa compiler creates shell script `project_name.exe`, which can be used later to run the application. As already noted on server side application runs in node.js.

I haven't seen any documentation for larger scale deployment, but I assume that node.js best practices can be leveraged here too.

When browser client connects to server it starts to communicate on background using XMLHttpRequest POST requests to exchange necessary data.  Looks like current version of Opa has some problems here, because even for very simple application (a form with couple of fields, which are saved to database after submission), this communication is massive ( see [this](https://github.com/MLstate/opalang/issues/175) \- 29 requests just to switch focus from one input to another). As per explanation from developers this is a regression issue in current version and should be hopefully fix in future. They said it  can be mitigated by carefully assigning code explicitly to either server or client,  however I did not find an easy way how to do it in that simple form example. As per now it's looks to me as a serious issue, because it completely undermines application performance and scalability.


## Community, History


Opa is not a new project, it appeared  in 2010 (according to [this article](http://en.wikipedia.org/wiki/Opa_%28programming_language%29)) and couple years later received some attention as promising 'next-gen'  web framework.   However it never really captured broader audience after that initial hype.

Now Opa community is small and it is mainly based in [MLState, ](http://www.mlstate.com)a company founded by Opa principal author. MLState is also a key user of Opa,  which is utilized in their commercial projects. But Opa project is still alive, maintained and developed and developers reply to issues posted on Github.


## Conclusion


There is a lot of nice things in Opa, which can improve and speed up web application development. I particularly liked:



- one code for client and server, ideally compiler decides where to put it.
- very concise code - a lot of nice syntactic extensions for web programming (xhtml, css, IDs, DOM manipulation)
- static typing with type inference (catches many problems during compile time)
- very flexible record and sum types
- all the functional goodies ( immutable values, first class functions, functions partial application, higher order functions, operators as functions ...)



On the other hand do these benefits justify an effort to learn completely new language and framework?  As per language itself, with some exposure to Ocaml, I did not find it difficult and it was relatively easy to start to write in Opa. However I really struggled with standard library due to lack of documentation.

The regression issue with very massive communication between client and server in current Opa version is worrying  and would prevent me from from deploying a production quality application, without acquiring much more deeper understanding of Opa internals.

Also editor support for Emacs is not flawless and made writing code bit annoying,  but this could be probably easily fixed.

To conclude - it was definitely useful to play with Opa, many nice concepts, however I do not think I will use it in near future due do issues mentioned above.

But I touched only surface of this interesting framework,  so I'd also like very much to hear your experiences so please do not hesitate to add comments!

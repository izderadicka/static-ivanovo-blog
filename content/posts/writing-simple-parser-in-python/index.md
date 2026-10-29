+++
title = "Writing Simple Parser in Python"
path = "/writing-simple-parser-in-python/"
date = "2015-11-14T10:12:07"
include_in_feeds = true
[extra]
wordpress_id = 1128
kind = "post"
node_key = "1128"
author = "admin"
source_url = "http://zderadicka.eu/writing-simple-parser-in-python/"
source_guid = "http://zderadicka.eu/?p=1128"
source_date_gmt = "2015-11-14 09:12:07"
categories = ["Programming"]
tags = ["parser", "python"]
+++
From time to time one might need to write simple language parser to  implement  some domain specific language for his application.  As always python ecosystem offers  various solutions - overview of python parser generators is available <a href="https://wiki.python.org/moin/LanguageParsing">here</a>.  In this article I'd like to describe my experiences with <a href="https://github.com/erikrose/parsimonious">parsimonious</a> package. For recent project of mine ( <a href="/projects/python/imap_detach-tool-download-email-attachments/">imap_detach</a> \-  a tool to automatically download attachment from IMAP mailbox) I needed simple expressions to specify what emails and what exact parts should be downloaded.<span id="more-1128"></span>


## Requirements


I needed a parser for simple logical expressions, which use a set of predefined variables ( properties of email), like these:


```sh
mime = "image/jpg" & attached & ! seen
```


Meaning: Email part is jpg image and is added as attachment and have not been seen yet


```sh
name ~=".pdf" & ( from ~= "jack" | from ~= "jim" )
```


Meaning all email part where filename contains .pdf and is from jack or jim


## Grammar


Parsimonious implements <a href="https://en.wikipedia.org/wiki/Parsing_expression_grammar">PEG</a> grammar which enables to create very compact grammar definitions. Unlike some other parser generators, where grammar in expressed in Python, parsimonious  has it's own syntax, which enables to create short and easy to overview grammar definitions:


```python
GRAMMAR=r""" # Test grammar
expr = space or space
or = and   more_or
more_or = ( space "|" space and )*
and = term  more_and
more_and = ( space "&" space term )*
term = not / value
not = "!" space value
value =  contains  / equals / bracketed / name
bracketed = "(" space expr space ")"
contains  =  name space "~="  space literal
equals =  name space "="  space literal
name       = ~"[a-z]+"
literal    = "\"" chars "\""
space    = " "*
chars = ~"[^\"]*"
"""
```


There are  couple of things which has to be remembered, when creating grammar:


<ul>
<li>PEG grammar should avoid left recursion, so rules like
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="nv">and</span><span class="w"> </span><span class="o">=</span><span class="w"> </span>expr<span class="w"> </span>space<span class="w"> </span><span class="s2">&quot;&amp;&quot;</span><span class="w"> </span>space<span class="w"> </span>expr</span></code></pre>
Don not work and will result in recursion error ( infinite recursion).  They have to be rewritten as indirect left recursion, which might be sometime challenging.</li>
<li>PEG grammar grammar are more deterministic that <a href="https://en.wikipedia.org/wiki/Context-free_grammar">context free grammars</a> -  so there is always one rule that is matched - there is no ambiguity like in  CFG.   This is assured by deterministic selection  / - always first match is selected and by greedy repetition operators * + ?  (they always match maximum possible length from input).
Practically this means that rules has to be more carefully designed and they need to be design in particular way to assure required priority of operators.</li>
<li>Only named rules can have some special treatment when walking <a href="https://en.wikipedia.org/wiki/Abstract_syntax_tree">AST</a> tree ( see below).  I think this is special feature of parsimonious,  but AST contains  nodes for a part of rule - like expressions that are in brackets.   This means if I have rule like this:
<pre class="code-highlight" data-language="sh"><code><span class="code-line"><span class="nv">and</span><span class="w"> </span><span class="o">=</span><span class="w"> </span>term<span class="w"> </span><span class="o">(</span><span class="w"> </span>space<span class="w"> </span><span class="s2">&quot;&amp;&quot;</span><span class="w"> </span>space<span class="w"> </span>term<span class="w"> </span><span class="o">)</span>*</span></code></pre>
I have no control on evaluating the right part, so I rather split it into two rules.</li>
</ul>




## Evaluation


Once we have the grammar, we can evaluate expressions by walking the parsed AST. Parsimonious provides nice support for this with <a href="https://en.wikipedia.org/wiki/Visitor_pattern">visitor pattern</a> . We can create subclass of `parsimonious.NodeVisitor` with `visit_rulename` methods for all (relevant) rules from the grammar.   visit method receives current node in AST and list of values from its already visited (evaluated ) children.

We will need some supporting code (error class and function to decode binary strings to unicode):


```python
class EvalError(Exception):
    def __init__(self, text, pos=0):
        super(EvalError, self).__init__(text+ ' at position %d'%pos)

def decode(s):
    if isinstance(s, six.binary_type):
        return s.decode('UTF-8')
    return s
```


 

So here is example of `NodeVisitor` class, that evaluates our simple expressions:


```python
class SimpleEvaluator(parsimonious.NodeVisitor):
    def __init__(self, ctx, strict=True):
        self.grammar = parsimonious.Grammar(GRAMMAR)
        self._ctx = ctx
        self._strict = strict
    
    def visit_name(self, node, chidren):
        if node.text in self._ctx :
            val=self._ctx[node.text]
            if isinstance(val, (six.string_types)+ (six.binary_type,)) :
                val = decode(val).lower()
            return val
        elif self._strict:
            raise EvalError('Unknown variable %s'%node.text, node.start)
        else:
            return ''
    
    def visit_literal(self,node, children):
        return decode(children[1]).lower()
        
    def visit_chars(self, node, children):
        return node.text
    
    def binary(fn):  # @NoSelf
        def _inner(self, node, children):
            if isinstance(children[0], bool):
                raise EvalError('Variable is boolean, should not be used here %s'% node.text, node.start)
            return fn(self, node, children)
        return _inner
    
    @binary
    def visit_contains(self, node, children):
        return children[0].find(children[-1]) > -1
    
    @binary
    def visit_equals(self, node, children):
        return children[0] == children[-1]
   
    def visit_expr(self, node, children):
        return children[1]
    
    def visit_or(self, node, children):
        return children[0] or children[1] 
    
    def visit_more_or(self,node, children):
        return any(children)
    
    def visit_and(self, node, children):
        return children[0] and (True if children[1] is None else children[1])
    
    def visit_more_and(self, node, children):
        return all(children)
        
    def visit_not(self, node, children):
        return not children[-1]
    
    def visit_bracketed(self, node, children):
        return children[2]
    
    def generic_visit(self, node, children):
        if children:
            return children[-1]
```


This class evaluates expression within context of defined variable's values (dictionary). So we can parse and evaluate expression with one method:


```python
context = {"name": "test.pdf", 
           "mime": "application/pdf",
           "from": "jim@example.com",
           "to": "myself@example.com",
           "attached": True,
           "seen": False
            }

parser=SimpleEvaluator(context)
result= parser.parse('name ~=".pdf" & ( from ~= "jack" | from ~= "jim" )')
```




##  Conclusion


Parsimonious is a nice compact package for creating small parsers that are easy to use. For myself I bit struggled with PEG grammar,  but that's probably due to my unfamiliarity with this type of grammars.  Once accustomed to it one can create more complex grammars.

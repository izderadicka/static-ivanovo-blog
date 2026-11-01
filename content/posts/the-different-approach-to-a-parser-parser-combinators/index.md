+++
title = "The Different Approach to  A Parser - Parser Combinators"
path = "/the-different-approach-to-a-parser-parser-combinators/"
date = "2017-12-20T14:59:07"
include_in_feeds = true
[extra]
wordpress_id = 1817
kind = "post"
node_key = "1817"
author = "admin"
source_url = "http://zderadicka.eu/the-different-approach-to-a-parser-parser-combinators/"
source_guid = "http://zderadicka.eu/?p=1817"
source_date_gmt = "2017-12-20 13:59:07"
[taxonomies]
category = ["Programming"]
tag = ["parser", "python"]
+++
Some [time ago I've looked into building parser](/writing-simple-parser-in-python/) for simple logical language used by <a href="/projects/python/imap_detach-tool-download-email-attachments/">imap_detach Tool</a>. I used there [parsimonious](https://github.com/erikrose/parsimonious) module which uses [PEG](https://en.wikipedia.org/wiki/Parsing_expression_grammar) grammars. Recently I learned about another parsing technique -[ Parser Combinators](https://en.wikipedia.org/wiki/Parser_combinator). The idea comes from functional programming and is about combining (with help of higher order functions - so called combinators) simple parsing functions, which parse primitive tokens, into more complex parsing functions, which parse parts of text and further combine those into more complex ones, ending finally with one function, which parses all given data. I first met with parser combinators in [Rust](https://www.rust-lang.org) library [nom](https://github.com/Geal/nom). Here parsers and  combinators are express as macros, which is convenient on one side (concise syntax), but can lead to pretty cryptic error messages and one cannot rely much on editor's help with auto-completions, context help etc..  I used nom to build very [simple URI parser](https://github.com/izderadicka/uri_parser).  I was wondering also if parser combinators are available for Python and how they would compare with other approaches - like above mentioned PEG grammars.<span id="more-1817"></span>

Looking around I found [parsec](https://github.com/sighingnow/parsec.py) \- Python parser combinators library inspired by well know [Haskell](https://www.haskell.org/) library.  Parsec is a small library with as much of functional style one can get out of Python.  You can check example for[ JSON parser](https://github.com/sighingnow/parsec.py/blob/master/examples/jsonc.py).

In my test I wanted to create a parser for same logical expressions as in previous [ article](/writing-simple-parser-in-python/) \- so we can parse and evaluate following expressions into either True or False value (assuming names are replaced with actual values):


<div>
<div><code>name &#126;=".pdf" &amp; from &#126;= "jack" | ! attached</code></div>
</div>




<div></div>




<div>
<div>
<div><code>name &#126;=".pdf" &amp; ( from &#126;= "jack" | from &#126;= "jim")</code></div>
</div>
</div>


 

After playing a bit with the parsec library I started to construct parsers and hit obvious problem (similarly as in initial trials with parsimonious) - [ left recursion](https://en.wikipedia.org/wiki/Left_recursion) \- though there are some advanced parser combinators that can handle left recursion with help of memoization,  Python parsec is a simple library, so combinators with left recursion have to avoided.  Below is the final code that works similarly to parsimonious grammar:


```python
from parsec import *

parsing_ctx = {}
strict = False


class ContextError(Exception):
    pass


def ctx_lookup(name):
    try:
        return parsing_ctx[name]
    except KeyError:
        if strict:
            raise ContextError("Name %s not is context" % name)
        return ''


def skip(p): return p << spaces()


left_bracket = skip(string('('))
right_bracket = skip(string(')'))
quote = string('"')
or_op = skip(string('|'))
and_op = skip(string('&'))
not_op = skip(string('!'))
contains_cmp = skip(string('~='))
eq_cmp = skip(string('='))
name = skip(regex('[a-z]+')).parsecmap(ctx_lookup)


@skip
@generate
def literal():
    yield quote
    text = yield many(none_of('"'))
    yield quote
    return ''.join(text)


@generate
def bracketed():
    yield left_bracket
    exp = yield expression
    yield right_bracket
    return exp


@generate
def equals():
    var = yield name
    yield eq_cmp
    val = yield literal
    return var == val


@generate
def contains():
    var = yield name
    yield contains_cmp
    val = yield literal
    return var.find(val) > -1


@generate
def not_exp():
    yield not_op
    val = yield simple ^ bracketed
    return not val


ops = or_op | and_op
simple = equals ^ contains ^ name
composed = simple ^ not_exp ^ bracketed


def reduce_ops(val1):
    @Parser
    def rp(text, index):
        curr_values = [val1]
        curr_index = index
        while True:
            res = ops(text, curr_index)
            if not res.status:
                # there is no further operation - stop parsing
                return Value.success(curr_index, any(curr_values))
            else:
                curr_index = res.index
                op = res.value
                res = composed(text, curr_index)
                if res.status:
                    if op =='&':
                        curr_values[-1] = curr_values[-1] and res.value
                    else:
                        curr_values.append(res.value)
                    curr_index = res.index
                else:
                    return res
    return rp


expression = composed.bind(reduce_ops)

```


Parsers in parsec are functions which take two arguments - index where to start and text to parse - and they return Value type - which contains either parsed value and index where next parser can continue or, in case of error, some description of expected input.  Combinator then takes parser functions as arguments and returns a new parser function, which applies parsers in some useful combination -  look for instance at `skip` function - it uses combinator skip implemented as  \<\< (overloaded operator ) - it returns value only from first parser and second parser just eats characters from input - in our case non-significant spaces.

Parsec has one very cool feature -  it can turn Python generator into parser. Generator must yields parsers, which are subsequently applied and their value is returned  back to generator - thus final value can be calculated very easily - look for instance to `equals` functions.

Final piece is function `reduce_ops`, which creates a parser that parses zero or more following binary operations (ands / ors) and reduces their operands into one single value - first ands as they have higher precedence then ors.

Big advantage of parser combinators is that they are built from bottom up and each parser can be tested independently so you can make unit tests for intermediate parsers to assure that they are working correctly.

I made quick comparison of performance for both parsers - old with parsimonious grammar and new with parsec combinators (1000 iterations of two simple expressions shown above):


<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table>
<tbody>
<tr>
<th>Old with grammar compilation in each iteration</th>
<td> 4.830 secs</td>
</tr>
<tr>
<th>Old with grammar compilation once before iterations</th>
<td>0.563 secs</td>
</tr>
<tr>
<th>New</th>
<td>0.536 secs</td>
</tr>
</tbody>
</table></div>


as you can see in parsimonious grammar compilation takes significant time, but once compiled it is almost as fast as parsec. Concerning code size both examples were similar in size ~ 100 lines of code.

Conclusions? Nothing particular - parser combinators are fun, you can try them yourself, if you like functional programing. If code is reasonably organized they can still provide comprehensible overview of the underlying "grammar".

+++
title = "Comparison of JSON Like Serializations - JSON vs UBJSON vs MessagePack vs CBOR"
path = "/comparison-of-json-like-serializations-json-vs-ubjson-vs-messagepack-vs-cbor/"
date = "2017-02-27T17:36:12"
include_in_feeds = true
[extra]
wordpress_id = 1558
kind = "post"
node_key = "1558"
author = "admin"
source_url = "http://zderadicka.eu/comparison-of-json-like-serializations-json-vs-ubjson-vs-messagepack-vs-cbor/"
source_guid = "http://zderadicka.eu/?p=1558"
source_date_gmt = "2017-02-27 16:36:12"
categories = ["Programming"]
tags = ["JSON", "python", "serialization"]
+++
Recently I've been working on some extensions to <a href="https://github.com/izderadicka/asexor/tree/multibackend/asexor">ASEXOR,</a> adding there direct support for messaging via WebSocket and I use JSON for small messages that travels between client (browser or standalone)  and backend.  Messages looks like these:


```python
messages = [
    {'call_id': 1, 'kwargs': {}, 'args': ['sleep', 0.1]},
    {'call_id': 1, 't': 'r', 'returned': 'd53b2823d35b471282ab5c8b6c2e4685'},
    {'call_id': 2, 'kwargs': {'utc': True}, 'args': ['date', '%d-%m-%Y %H:%M %Z']},
    {'call_id': 2, 't': 'r', 'returned': '77da239342e240a0a3078d50019a20a0'},
    {'call_id': 1, 'data': {'status': 'started', 'task_id': 'd53b2823d35b471282ab5c8b6c2e4685'}, 't': 'm'},
    {'call_id': 2, 'data': {'status': 'started', 'task_id': '77da239342e240a0a3078d50019a20a0'}, 't': 'm'},
    {'call_id': 1, 'data': {'status': 'success', 'task_id': 'd53b2823d35b471282ab5c8b6c2e4685', 'result': None, 'duration': 0.12562298774719238}, 't': 'm'},
    {'call_id': 2, 'data': {'status': 'success', 'task_id': '77da239342e240a0a3078d50019a20a0', 'result': '27-02-2017 11:46 UTC', 'duration': 0.04673957824707031}, 't': 'm'}
    
]

```


I wondered, if choosing different serialization format(s) (similar to JSON, but binary) could bring more efficiency into the application -  considering  both message size and encoding/decoding processing time.  I run small tests  in python 3.5 (CPython and <a href="https://pypy.org/">PyPy</a>)  (see tests <a href="https://gist.github.com/izderadicka/e08e058591528d3775a5712e7174752f">here on gist</a>) with few established serializers, which can be used as quick replacement for JSON and below are results (updated Dec 2nd 2017 thanks to comment below, as situation changed a bit with new libraries versions):<span id="more-1558"></span>


<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table>
<tbody>
<tr>
<th>Format</th>
<th>Total messages size (bytes)</th>
<th>Processing time
10000 x encoding/decoding all messages</th>
<th>PyPy 3</th>
</tr>
<tr>
<td><a href="http://www.json.org/">JSON</a> (standard library)</td>
<td>798</td>
<td>789 ms</td>
<td> 706 ms</td>
</tr>
<tr>
<td>JSON (<a href="https://github.com/esnme/ultrajson">ujson</a>)</td>
<td>798</td>
<td>181 ms</td>
<td> 3.14 s</td>
</tr>
<tr>
<td><a href="http://msgpack.org/index.html">MessagePack</a> (official lib)</td>
<td>591</td>
<td>286 ms</td>
<td> 314 ms</td>
</tr>
<tr>
<td>MessagePack (<a href="https://github.com/vsergeev/u-msgpack-python">umsgpack</a>)</td>
<td>585</td>
<td>435 ms</td>
<td> 519 ms</td>
</tr>
<tr>
<td><a href="http://cbor.io/">CBOR</a></td>
<td>585</td>
<td>164 ms</td>
<td> 313 ms</td>
</tr>
<tr>
<td><a href="http://ubjson.org/">UBJSON</a></td>
<td>668</td>
<td>292 ms</td>
<td> 406 ms</td>
</tr>
</tbody>
</table></div>


As messaging can use clients in web browser we can also look at performace  of some serializers in Javascript on <a href="https://jsperf.com/msgpack-js-vs-json/37">this page</a>.  As JSON serialization in part of browsers Web API, unsurprisingly it's fastest there.

All alternative libraries are faster then standard library JSON, some improved significatly form previous tests ( UBJSON and umsgpack).  Standard library implementation of JSON serializer can be easily replaced by better performing ujson package. In PyPy interpreter standard library JSON is doing a slightly better, however every other library is performing worse,  notably ujson.


## Conclusions


JSON is today really ubiquitous, thanks to it's ease of use and readability.  It's probably good choice for many usage scenarios and luckily JSON serializers show good performance.   If size of messages is of some concern, CBOR looks like great, almost  instant replacement for JSON, with similar performance in Python ( slower performance in browser is not big issues as browser will process typically only few messages)  and 27% smaller messages size.

If size of messages is big concern carefully designed binary protocol ( with <a href="https://developers.google.com/protocol-buffers/">Protocol Buffers</a> for instance) can provide much smaller messages ( but with additional costs in development).

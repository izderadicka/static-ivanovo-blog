+++
title = "Next Adventure in Aurelia - Autocomplete Component"
path = "/next-adventure-in-aurelia-autocomplete-component/"
date = "2016-07-16T10:42:02"
include_in_feeds = true
[extra]
wordpress_id = 1405
kind = "post"
node_key = "1405"
author = "admin"
source_url = "http://zderadicka.eu/next-adventure-in-aurelia-autocomplete-component/"
source_guid = "http://zderadicka.eu/?p=1405"
source_date_gmt = "2016-07-16 09:42:02"
[taxonomies]
category = ["Programming"]
tag = ["Aurelia", "autocomplete", "Javascript", "Web UI"]
+++
As I have written in [this post](/starting-with-aurelia-pagination-with-back-and-sort/) I'm slowly getting into [Aurelia](http://aurelia.io) Web UI framework. Recently I needed an autocomplete component.  My requirements were:


<ul>
<li>get suggestions from server via REST API (JSON payload)</li>
<li>simple, yet flexible (value can be calculated from received suggestions)</li>
<li>flexible ways to display suggestions (ideally provide a template to display suggestions values)</li>
<li>suggest values as one types matching starting letters (case insensitive and <span style="text-decoration: underline;">diacritics</span> insensitive)</li>
<li>cache server responses for efficiency</li>
<li>can use both mouse and keys (arrows + enter) to select suggestion</li>
</ul>


I'm sure that existing autocomplete components like [typeahead](https://twitter.github.io/typeahead.js/) or [JQuery UI Autocomplete](https://jqueryui.com/autocomplete/) would serve my purpose quite well. It's fairly easy to integrate existing components from other frameworks into Aurelia (see [this post](http://ilikekillnerds.com/2016/02/using-jquery-ui-widgets-in-aurelia/) for instance).  But I decided to create my own, using only Aurelia (and a bit of [JQuery](https://jquery.com/) \- but it can be easily rewritten in pure DOM API - JQuery is used just for convenience, because it's anyhow  used in Aurelia skeleton app). I though it would be nice learning exercise (and it really was) and also we programmers (especially leisure programmers like myself) do like to reinvent the wheel, right? (But it's not always bad idea - image world when only one type of wheel exists - by recreating existing solutions, improving them, changing them we can also achieve progress - Web UI frameworks themselves are good example of such progress).  I'd like to share my experiences further in this article.<span id="more-1405"></span>


# Coding And Learning


I'll not show all the code here - sources are available [here at github](https://github.com/izderadicka/mybookshelf2/tree/master/client/src/components/autocomplete), as part of my other project.

So let's start with component's view ( template) [autocomplete.html](https://github.com/izderadicka/mybookshelf2/blob/master/client/src/components/autocomplete/autocomplete.html):


```html
<template>
  <require from="./autocomplete.css"></require>
  <div class="autocomplete-container">
    <input class="autocomplete-input ${additionalClass}" autocomplete="off" value.bind="value & debounce:850" blur.trigger="hideSuggestions()"
    keydown.delegate="keyPressed($event)" placeholder.bind="placeholder" focus.trigger="showSuggestions()">
    <div class="autocomplete-suggestion" style="display:none">
      <div class="list-group">
        <a data-index="${$index}" class="list-group-item ${$index == _selected ? 'active' : ''}"
        repeat.for="item of _suggestions" mousedown.delegate="select($index)">
          <span if.bind="! suggestionTemplate">${item}</span>
          <compose if.bind="suggestionTemplate" view.bind="suggestionTemplate" view-model.bind="item"></compose>
        </a>
      </div>
    </div>
  </div>
</template>
```


Aurelia is all about data bindings, right? So we use it here intensively  to implement autocomplete functionality. There are two important bindings:
<code></code>
`value.bind="value & debounce:850"` \- on line 4 - this will assure that changes in the text input are propagated into our view-model and  we also use 'binding behaviour' -  `debounce:850, which` assures that value is updated only after it stays same for 850ms (e.g. we've paused writing), and it's exactly what we want for autocomplete. In view model we process these changes in `valueChanged` method and fetch appropriate suggestions. This binding is by default two-way.

`repeat.for="item of _suggestions"` \- on line 9 - this is one way binding that is updated as new suggestions are loaded in view-model.

We need also some event bindings to enable us to select a suggestion:

`keydown.delegate="keyPressed($event)"` \- on line 4 - binds a method to handle special keys for selecting suggestions (up, down, enter, escape).  It worth to note that by default such method prevents default handling of the event unless it returns `true`. In this case it's crucial to enable default handling, otherwise we could not write into this input.

`mousedown.delegate="select($index)"` - on line 9 - enables us to select given suggestion with mouse click. To identify individual suggestion (for key initiated selection and scrolling) we use custom data attribute:  `data-index="${$index}"` (`$index` is bound to index of `repeat.for` iterator).

Other bindings on lines 10 and 11 are used to display suggestion - either as plain string (line 10), when no template is provided. Or we can use custom template with help of `compose` tag.  if.bind is used to decide, which one to use. For custom template we had to provide model-view property containing template path: `view.bind="suggestionTemplate"`. View-model here is bound to individual suggestion objects from iterator in parent element (`item`).
Here is an example of simple template for a suggestion:


```html
<template>
  ${title} (${id})
</template>
```


Only remaining bindings are:


<ul>
<li>on line 4 - <code>blur.trigger="hideSuggestions()"</code>. It hides suggestions, when text input loses focus (user click somewhere else on the page). Note that blur event does not bubble up in DOM, so <code>blur.delegate</code> does not work. Actually implementing this binding was bit challenging, because it interferes with mouse action on line 7. The only working combination was <span style="font-family: monospace, serif;"><span style="font-size: 15px;">with</span></span> <code>mousedown</code> event on line 7 (not click event).</li>
<li>and <code>focus.trigger</code> on next line, which will again show suggestions, if we click on input box.</li>
</ul>


We  also need some styling for our autocomplete  component (absolute position for suggestions list), which is contained in file [autocomplete.css ](https://github.com/izderadicka/mybookshelf2/blob/master/client/src/components/autocomplete/autocomplete.css)required on line 2.

Next we have to implement view-model for our template - [autocomplete.js](https://github.com/izderadicka/mybookshelf2/blob/master/client/src/components/autocomplete/autocomplete.js). The basic skeleton of view-model class is:


```javascript
import {bindable, inject} from 'aurelia-framework';
//other imports

@inject(Element)
export class Autocomplete {
  @bindable({defaultBindingMode: bindingMode.twoWay}) value; // value of input
  @bindable loader;
  // more properties ...
  _suggestions;
 
  constructor(elem) {
    this.elem = elem;
  }

  valueChanged() {
    // load suggestions for current value calls getSuggestions
  }

  getSuggestions(forValue) {
  // logic to fetch suggestions for server
  }

  attached() {
    this.suggestionsList = $('div.autocomplete-suggestion', this.elem)
  }

  hideSuggestions() {
    this.suggestionsList.hide();
  }

  showSuggestions() {
    this.suggestionsList.show();
  }
}
```


First we use dependency injection of Aurelia framework to make root element of the component available in our model-view class ( `@inject` decorator on line 4, `constructor` lines 11-12 and assignment in `attached` method on line 24). This is very common patter for Aurelia components - key insight here is that we can work with view elements only after they are attached to page DOM (signalized by `attached` method).

Core logic of our autocomplete component is implementedin getSuggestions method:


```javascript
  getSuggestions(forValue) {
    logger.debug(`Get suggestions for ${forValue}`);
    if (Array.isArray(this.loader)) {
      return Promise.resolve(this.loader.filter(item =>
        startsWith(this.getSuggestionValue(item), forValue)));
    } else if (typeof this.loader === 'function') {
      if (this._cache && startsWith(forValue, this._cache.search) &&
        new Date() - this._cache.ts <= CACHE_DURATION) {
        return Promise.resolve(this._cache.items.filter(
          item => startsWith(this.getSuggestionValue(item), forValue)
        ))
      }
      return this.loader(forValue)
        .then(res => {

          if (res.items.length === res.total) {
            // we have all results, can cache
            this._cache = {
              search: forValue,
              items: res.items,
              ts: new Date()
            }
          }

          // if inputed value already changed do not return these suggestions
          if (this.value !== forValue) return [];

          return res.items;
        });
    }
    return Promise.reject(new Error('Invalid loader'));
  }
```


Here we use class  bindable property `loader` to get appropriate suggestions - for testing purposes it can be  just plain array of all available suggestions (ordered appropriately). Then we need to filter them with current autocomplete value (lines 3-5) and return matching suggestions as resolved Promise (to keep it consisted with asynchronous fetch of suggestions from server). Filtering is done by matching start of the suggestions values ( case and diacritics insensitive):


```javascript
function startsWith(string, start) {
  string = diacritic.clean(string).toLowerCase();
  start = diacritic.clean(start).toLowerCase()
  return string.startsWith(start);
}
```


More interesting behaviour happens when `loader` is a function. This function should return a Promise that resolves to  an object with suggestions (items property contains suggestions, total property contains total number of suggestions available on the server).  If we receive all suggestions from server for given search key (length of items less or equal then total), we can cache them and use later (lines 16-23). Cashing strategy is simple -  if current value of autocomplete starts with search value of cached response, we can use current cache and just filter it locally (lines 7-11). Crucial is that local filtering works exactly same way as on the server. We also limit time validity of cache to certain period (60 seconds).

This simple strategy  works fine in most cases,  because people are writing sequentially, so in some moment we've got in cache all suggestions needed for all following strings with this prefix and can filter suggestions locally in client. Just stick to KISS (Keep It Simple Stupid) approach here.

So basically that's the core of our view model - for complete implementation check full code in [autocomplete.js](https://github.com/izderadicka/mybookshelf2/blob/master/client/src/components/autocomplete/autocomplete.js).

Now we can use our component in the page:


```html
<template>
  <require from="components/autocomplete/autocomplete"></require>
  <h3> Ebooks (loader is fetching values from API)</h3>
  <autocomplete loader.bind="loaderEbooks" value-key="title" suggestion-template="./autocomplete-ebooks.html" value.bind="ebook"></autocomplete>
  <p>Selected ebook is ${ebook}</p>
</template>
```


with this view-model:


```javascript
import {inject} from 'aurelia-framework';
import {ApiClient} from 'lib/api-client';

@inject(ApiClient)
export class TestPage {
  ebook;
  
  constructor(client) {
    this.client=client;
  }

  get loaderEbooks() {
    return start => this.client.getIndex('ebooks', start);
  }
}
```


Small note about `loaderEbooks` property - why not to have method :


```javascript
  loadEbooks() {
    return this.client.getIndex('ebooks', start);
  }
```


and bind it directly in `loader.bind` attribute? Actually it will not work due to the way how Javascript uses `this` reference. If a function is called as an object method, then `this` refers to the object from which method is called. It's an instance of `Autocomplete` view-model class, not our page view-model, because function reference is bound to `Autocomplete` `loader` property and then called in `getSuggestions` method like `this.loader(forValue)` (see above - line 13).

We also use custom template for suggestions -  autocomplete-ebooks.html:


```html
<template>
  <require from="components/authors"></require>
  <div class="ebook-title">${title}</div>
  <div class="ebook-series" if.bind="series">${series.title} #${series_index}</div>
  <authors authors.one-time="authors" compact.bind="true" linked.bind="false"></authors>
</template>
```


So finally our autocomplete component may look like this:

<a href="/wp-content/uploads/autocomplete.png"><img alt="autocomplete" class="alignnone size-full wp-image-1422" decoding="async" height="376" loading="eager" sizes="(max-width: 469px) 100vw, 469px" src="/wp-content/uploads/autocomplete.png" srcset="/wp-content/uploads/autocomplete.png 469w, /wp-content/uploads/autocomplete-300x241.png 300w" width="469"/></a>


##  Conclusions


Thanks to Aurelia bindings, binding behaviours, composing and templates I was able to put together a fully functional and flexible autocomplete component in approximately 200 lines of code (including templates). That's pretty impressive, huh? (compare with source code for typeahead). The component might need some tweaking in future, but basics are there.

I'm continuing to learn Aurelia, I'm fairly happy with it, although is some areas my intuition failed me and have to struggle with the framework a bit. I'm sorely missing more detailed documentation of Aurelia, especially in depth explanation of it's key concepts. Also fighting little with  required tool set - especially package manager JSPM (several packages have issues like aurelia-configuration, aurelia-bundler, autobahn). But overall I'm progressing and hoping to learn more about Aurelia (now available as RC).

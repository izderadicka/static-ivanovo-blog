+++
title = "Starting with Aurelia - Pagination with Back and Sort"
path = "/starting-with-aurelia-pagination-with-back-and-sort/"
date = "2016-04-10T11:27:17"
include_in_feeds = true
[extra]
wordpress_id = 1289
kind = "post"
node_key = "1289"
author = "admin"
source_url = "http://zderadicka.eu/starting-with-aurelia-pagination-with-back-and-sort/"
source_guid = "http://zderadicka.eu/?p=1289"
source_date_gmt = "2016-04-10 10:27:17"
[taxonomies]
category = ["Programming"]
tag = ["Aurelia", "ES6", "Javascript", "MVVM", "SPA", "Web UI"]
+++
I do not like very much programming of User Interfaces (UIs) and frankly spoken I'm not very good at that, but alas sometimes UIs are necessary so I have to try my best. Many recent applications use web browser as UI, and  situation here is  quite messy ( see this nice article about[ JS Frameworks Fatigue)](https://www.allenpike.com/2015/javascript-framework-fatigue/).  Last time I was involved with web UIs I had utilized [Backbone with Django based RESTful server](/projects/python/rest2backbone/).  Recently I've decided to rewrite [MyBookshelf](/projects/python/mybookshelf-ebooks-library/) application with modern technonogies (it's about 8 years old, which is something like prehistory considering changes in web development).  New architecture should be based on RESTful services and Single Page Application (SPA) relying on recent browser capabilities.   I've have been looking around and found that Backbone is already almost forgotten and we have two new stars on the stage - [AngujarJS](https://angularjs.org/) and [React ](https://facebook.github.io/react/)\- I have very quickly looked at both and finally decide for another framework [Aurelia](http://aurelia.io/).<span id="more-1289"></span>


## Why not AngularJS or React?


AngularJS is moving to AngularJS2, which is significantly different form previous version and not compatible.  So it probably worth to start directly with AngularJS2 - however I somehow did not like it's syntax and overall approach - it looked bit complicated and inconsistent, relying on experiences from previous version, which I have not tried.

React is only View layer ( so it'll require other libraries for router, their fancy [flux](https://facebook.github.io/flux/) pattern etc.) and it's Facebook product. Maybe it's just my prejudice, but I try to avoid everything related to this company (however generally people are quite positive about React).


## Why Aurelia


Aurelia got some publicity last year and it has been highly prised as well designed, next generation web UI framework.  Generally from what I've seen it looked attractive so I give it a try. You can check this [cool video](https://channel9.msdn.com/Events/Seth-on-the-Road/DevIntersection-2015/Rob-Eisenberg-on-Aurelia), where creator and chief architect of Aurelia  Rob Eisenberg introduces the framework.


### What I liked





- Based on latest [Javascript (ES6, ES7)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Language_Resources) - so basically by learning Aurelia, you are also learning new and future Javascript, which generally feels much better, with a lot of advanced language features present by default.  (in order to use latest JS project has to be compiled(transpiled) with [Babel](https://babeljs.io/)).
- Consistent and compact grammar -   majority is just plain modern JavaScript. I particularly like decorations, because I'm used to them from Python and they are very easy to use and understand. Extensions to HTML (for view templates) are nicely designed and easy to remember (simply named attributes as value.bind, repeat.for, if.bind, ref etc.).
- Convention over configuration - conventions  are easy to understand, logical, so it's no problem to follow them and they save your time.
- Template binding - [MVVM](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel) architecture is easy to understand and supports decomposition of UI into reusable components.
- Basically all solutions and concepts in Aurelia are 'natural' and understandable -  if you think it should work in this way it usually does.
- Batteries included - Aurelia aims to provide complete framework, with all necessary components included.  (However this is not completely true today,  as some libraries are in early stages of development and I have not seen comprehensive widgets library for Aurelia).
- Although Aurelia tries to be self-contained , it can be integrated with other libraries ( for instance [boostrap](http://getbootstrap.com/) in already included by default, others like [JQuery](https://jquery.com/),  [Polymer](https://www.polymer-project.org/1.0/) can be integrated).  Aurelia is also very modular, so any part can be customized, replaced if needed.
- Although it not directly related to this framework, it was first time I used [BrowserSync](https://www.browsersync.io/) and it looks like very powerful tool for testing and experimenting with code and I liked it very much .  All changes are automatically reloaded into browser, which helps a lot.





### What I did not like





- There is only limited amount of documentation, so you are left very much on your own. Apart of basic "Getting Started" there is very little detailed documentation. API reference is minimal.  Articles on the web are often outdated due to massive development  of the framework in last year.
- Key concepts are not well explained -  you can see some examples, but for real work  you need to understand core concepts of this framework like  detailed flow of binding, differences between various options (for instance using component directly vs composing), when view models properties could be used directly and when they have to decorated with @bindable. How  property getters should be used and what is advantage of decorating them with composedForm, how components can be interconnected (observers, events, signals ...) etc.
- Learning experience for somebody without exposure to most recent frameworks (e.g. AngularJS etc.) could be quite steep.
- It's still not production ready, but it's getting there.
- Requires a lot of tools to support it. For one not so familiar with Node and current JS tools stack it's another layer of complexity.
- Framework is quite large (even small app can have 1M) -   so it can be problem for older devices and for slow connections.
- I got into some issues with browsers -  In Firefox some strange interaction with Firebug, which resulted in mysterious errors.  On Chromium fetch requests freeze in pending state randomly.
- Without deeper understanding of component lifetime and data binding I was sometimes surprised how things finally worked (bindings did not changed when expected, or changed too early from undefined to null and only then to final value,   behaviour of components differs based on way how page was routed etc.)





## Getting started


The official documentation gives you quick way to [start up ](http://aurelia.io/docs.html) with a mock-up application, which has some basic navigation and a page, which consumes RESTful API.  Similar app can be cloned from [github aurelia-skeleton](https://github.com/aurelia/skeleton-navigation), but from then you are left to your own skill and to yet limited documentation.

One of features I required, was flexible pagination, which:



- is general and can be used on various data sources
- is native to Aurelia (use core Aurelia components)
- supports browser back button - so I can go to an item detail and then back to the given page
- supports sorting of paginated list
- can be embedded on various pages
- displays spinner when next page is loaded from server



There are few existing plugins for Aurelia, but none really matched my requirements, so I decided to create my own solution, thinking that it could be good learning exercise.


## Pagination solution


Our pagination solution is split into 3 components:


<ul>
<li><code>page-controller</code> -  controls loading of pages from given resource</li>
<li><code>pager</code> - navigation components, which allows to load previous and next pages etc.</li>
<li><code>sorter</code> - select box, which allows to select required sorting of results</li>
</ul>


Let's start with `sorter`. It's fairly simple components -   a select box with a given list of possible sortings for our data.  Each Aurelia component has two parts - view model, which wraps access to data and some logic related to presentation of data. View model is basically plain JavaScript class (using ES6/7 syntax):


```javascript
import {
  bindable,
  LogManager
} from 'aurelia-framework';
const logger = LogManager.getLogger('sorter');

export class sorter {
  @bindable sort;
  @bindable sortings;

  constructor() {
    if (history.state) {
      const state = history.state;
      logger.debug('restoring sorter back to ' + JSON.stringify(state));
      if (state.sort) {
        this.sort = state.sort;
        logger.debug(`sort is ${this.sort}`);
      }
    }
  }

}

```


There is not very much logic in this component -  it has two properties: `sortings` \- which contains a list of all possible sortings of data and current `sort`.  Both are bindable - so they can be bound to value in view template - see below.  One special thing is that sort if restored from `history.state` if that is available. As per my current knowledge best place to do this seems to be constructor of the class (because it does not yet propagate changes through observers - so component is just preset to this value). You can also see a way how logging is supported in Aurelia via `LogManager`, which is pretty standard way similar to logging solutions in other frameworks and languages.

The view template for `sorter` is also pretty simple:


```html
<template>
  <select value.bind="sort">
    <option repeat.for="sorting of sortings" value="${sorting.key}">${sorting.name}</option>
  </select>
</template>
```


It's just HTML select element with few extra attributes, which are basically self explanatory.

Another component is pager, which displays page navigation - in our case has just two buttons - Next and Previous, but could be easily extended to show page numbers. Again it has two parts, view model:


```sh
import {inject,DOM, bindable} from 'aurelia-framework'
import {LogManager} from 'aurelia-framework';
const logger = LogManager.getLogger('pager');

@inject(DOM.Element)
export class Pager{
  @bindable page;
  @bindable lastPage;
  @bindable loading = false;

  constructor(elem) {
    this.elem=elem;
  }

  activated() {
    logger.debug('Pager activated');
  }

  nextPage() {
    if (this.page < this.lastPage && ! this.loading) this.page++;
  }

  prevPage() {
    if (this.page >1 && ! this.loading) this.page--;
  }

  get nextPageNo() {
    return Math.min(this.lastPage, this.page+1)
  }

  get prevPageNo() {
    return Math.max(this.page-1, 1)
  }

  get isFirstPage() {
    return this.page===1
  }

  get isLastPage() {
    return this.page === this.lastPage || ! this.lastPage
  }
}

```


It contains a bunch of helper functions and properties for the view. One notable thing is that we are using Dependency Injection (DI) support of the framework to inject reference to root element of the rendered view. Actually it not  needed here, but it's left for possible future use.

Corresponding view template is:


```html
<template>
  <nav>
  <ul class="pager">
    <li if.bind="!isFirstPage"><a href="#" click.delegate="prevPage()"
      title="Page ${prevPageNo}"><i class="fa fa-caret-left"></i> Previous</a></li>
    <li if.bind="!isLastPage"><a href="#" click.delegate="nextPage()" 
       title="Page ${nextPageNo}">Next <i class="fa fa-caret-right"></i> </a></li>
  </ul>
  <div style='width:100%'>
    <span class="pager-spinner"  if.bind="loading"><i  class="fa fa-spinner fa-spin fa-2x"></i></span>
  </div>
</nav>
</template>

```


You can see conditional display of several elements with `if.bind`  and handling of DOM events with `click.delegate`.  Both refer to available members of the view model.

Finally we have `page-controller` component, which is responsible for loading appropriate data page for us, based on page number and sorting value. This component does not have any view template, it's just responsible to load correct data:


```javascript
import {bindable, processContent, noView, inject, customElement, computedFrom} from 'aurelia-framework'
import {LogManager} from 'aurelia-framework';
const logger = LogManager.getLogger('page-controller');

@noView()
@processContent(false)
@customElement('page-controller')
export class PageController {
  @bindable page=1;
  @bindable sort;
  lastPage;
  @bindable pageSize = 10;
  loading=false;
  data=[];
  @bindable loader = () => Promise.reject(new Error('No loader specified!'));
  @bindable noSort=false;

  constructor() {
    logger.debug('Constructing PageContoller');

    if (history.state) {
      const state=history.state;
      logger.debug('restoring page-controller back to '+JSON.stringify(state));
      if (state.page && state.page != this.page) {
        this.page=state.page;
      }
      if (state.sort) {
        this.sort=state.sort;
        logger.debug(`sort2 is ${this.sort}`);
      }
    }
    }

  created(owningView, myView) {
    logger.debug('Creating PageController');
  }
  bind(ctx) {
    logger.debug(`Binding PageController`);
    // if status is restored from history change to page will not happen so we need to load page here
    if (history.state && history.state.page || this.noSort) this.loadPage(this.page);

  }
  attached() {
    logger.debug('PageController attached');
  }

  loadPage(page) {
    //if (this.loading) return Promise.resolve(null);
    logger.debug(`Loading page ${page}, ${this.sort} by ${this.loader.name}`);
    this.loading=true;
    return this.loader(page, this.pageSize, this.sort)
      .then(({data,lastPage}) => { this.data=data;
                                this.lastPage=lastPage },
            err => logger.error(`Page load error: ${err}`))
      .then(() => this.loading=false);
  }

  pageChanged(newPage) {
    logger.debug('page changed '+newPage);
    this.loadPage(this.page)
    .then(() => {history.replaceState({...(history.state || {}), page:this.page, sort:this.sort}, '')});
  }

  sortChanged(newValue, old) {
    logger.debug(`sort changed ${this.sort}`);
    this.reset();

  }

  loaderChanged() {
    logger.debug('Loader changed in PageController');
    this.reset();
  }

  reset() {
    const oldPage=this.page;
    this.page=1;
    if (oldPage==1) this.pageChanged(1,1);
  }

  @computedFrom('data')
  get empty() {
    return ! this.data || this.data.length==0;
  }

}

```


As this view model will not be rendered we can support this via `noView` decorator, also we do not care about `page-controller` element content ( processContent(false) decorator).   The last decorator `customElement` can be used to give custom name to element corresponding to this view model.

On lines 9-16 we have few properties to control pagination including data representing current page. In constructor we restore state from history.  This state is actually set on line 61, when page changes (using `history.replaceState` not to pollute browser history, just to refer to last page seen).

Apart of the constructor we have several method, which are called back during component life cycle. These are good examples of Aurelia conventions. Life cycle is basically  constructor -\> created -\> bind -\> attached. `bind` is used here to load initial page, rest is there just for debug purposes.

Another examples of Aurelia conventions are `...Changed(oldValue, newValue)` methods on lines 58-73, which are called every time observable property changes.  We use them to load new page when either page number, sorting, or data loader changes.

Pages are loaded in method loadPage on lines 47-56.  It uses bound function - loader, which should return Promise (loader function is basically some kind of wrapper around Aurelia [HttpClient](https://github.com/aurelia/fetch-client/tree/master/doc)).

Finally we need a page, where all three components  are used together, let's start with view template first:


```html
<template>
  <require from="components/authors"></require>
  <section>
    <div class='container-fluid items-header'>
      <h3 class="page-title">Ebooks (${paginator.page}/${paginator.lastPage})
    <div class='sorter' if.bind="sortings.length">
      <label class="sorter-label"><i class="fa fa-sort"></i></label>
      <sorter  sortings.one-time="sortings" view-model.ref="sorter"></sorter>
    </div>
    </h2>
  </div>
  <page-controller view-model.ref='paginator' loader.bind="loader" sort.bind="sorter.sort" page-size="12" no-sort.bind="!sortings.length"></page-controller>

    <div class="container-fluid">
      <div class="row">
        <div class="col-sm-6 col-md-4 col-lg-3" repeat.for="ebook of paginator.data">
          <div class='ebook-detail'>
            <authors authors.one-time="ebook.authors" compact.bind="true"></authors>
            <div class="ebook-title">[${ebook.title}](#/ebook/${ebook._id})</div>
            <div class="ebook-series" if.bind="ebook.series">${ebook.series} #${ebook.series_index}</div>
          </div>
        </div>
      </div>
    </div>

  <pager page.two-way="paginator.page" last-page.bind="paginator.lastPage" loading.bind="paginator.loading"></pager>
    </section>

</template>
```


Since our pagination components are available as a feature in the application we do not have to import them via \<require\>.

Here we just  need to connect these three components together- we can use ref attribute to reference component within this template. Plain ref`  attribute `  references rendered element, `view-model.ref` its view model, which is what we need here. We bind `sorter.sort` to page-controller (which is referenced as `paginator`) and `paginator.page` to pager - in this case we need two way binding -  `page.two-way`, because page can change either internally in pager ( by navigation to other page) or externally as change in sorting of data or binding new data loader.

loader and sorting are provided by view model for this page:


```javascript
import {inject, bindable, LogManager} from 'aurelia-framework';
const logger=LogManager.getLogger('ebooks-panel');

@inject(ApiClient)
export class Ebooks {
  @bindable sortings=[{name:'Title A-Z', key:'title'}, {name:'Title Z-A',key:'-title'}];
 
  constructor(client) {
    this.client=client
  }
  activate(params) {
    logger.debug(`History State ${JSON.stringify(history.state)}`);
  }

  get loader() {
    return this.client.getMany.bind(this.client, 'ebooks');
  }
}

```


loader is just providing method from our custom wrapper around HttpClient to interface our RESTful API:


```javascript
getMany(resource, page=1, pageSize=25, sort, extra='') {
    const url='/'+resource+`?page=${page}&max_results=${pageSize}` +
      (sort?`&sort=${sort}`:'')+extra;
    return this.http.fetch(url)
      .then(response => response.json())
      .then(data => {let lastPage=Math.ceil(data._meta.total / pageSize);
                    return {data:data._items, lastPage:lastPage}})
  }
```




##  Conclusions


Aurelia appears to be a promising framework, which very much make a sense.  It's still in early stages (beta), but everything works quite well.  For me as non expert in recent Web UI development more detailed documentation, explaining in detail core concepts and providing best practices is sorely missing.

As per pagination component, I'm sure it can be done better, when one gets more insight into the framework. Now for instance there is a problem when switching between pages with sub path - like #/search/aaa to search/bbb -   pagination works, but it's not restored to last page  when back button is used (because components are already displayed so constructor is not called).

For curious readers source code is on [github](https://github.com/izderadicka/mybookshelf2/tree/master/client/src/components/pagination).

I'd like very much hear comments, experiences and advices from other Aurelia users.

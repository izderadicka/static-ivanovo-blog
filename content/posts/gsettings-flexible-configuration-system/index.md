+++
title = "GSettings - Flexible Configuration System"
path = "/gsettings-flexible-configuration-system/"
date = "2012-11-26T12:32:17"
include_in_feeds = true
[extra]
wordpress_id = 374
kind = "post"
node_key = "374"
author = "admin"
source_url = "http://zderadicka.eu/gsettings-flexible-configuration-system/"
source_guid = "http://zderadicka.eu/?p=374"
source_date_gmt = "2012-11-26 11:32:17"
categories = ["Programming"]
tags = ["desktop", "gnome 3", "linux", "python"]
+++
GSetttings is the standard way how Gnome 3 applications store their configuration. GSettings is the front-end interface for application, actual values are stored by back-end - standard one is called dconf. We can then use the tool <a href="http://developer.gnome.org/dconf/unstable/dconf-editor.html">dconf-editor</a> to easily browse all stored configurations for all applications. Thanks to GObject introspection we can also work easily with GSettings from python.<span id="more-374"></span>


### Introduction to GSettings in Python


Before we can start with programming, we have to define so call schema of our configuration - schema is a XML file, which describes keys in our configuration.  Schema can look like this:


```html
<schemalist>

    <enum id="eu.zderadicka.sample.enum">
    <value nick="option1" value="1"/>
    <value nick="option2" value="2"/>
    <value nick="option3" value="3"/>
  </enum>
  <schema id="eu.zderadicka.sample"  gettext-domain="thetool">

    <key type="b" name="enable-something">
      <default>false</default>
      <summary>Enable something</summary>
      <description>Enables something important in the application</description>
    </key>
    <key type="i" name="timeout">
        <range min="1" max="15"/>
        <default>1</default>
        <summary>Some timeout</summary>
        <description>Something will happed after that period</description>
    </key>

    <key name="list-of-numbers" type="ai">
      <default>[15,30,45,60,90,120,150,180,240]</default>
      <summary>Some numbers</summary>
      <description>
        List of numbers
      </description>
    </key>

    <key name="list-of-strings" type="as">
        <default>[]</default>
        <summary>Some words</summary>
        <description>List of strings</description>
    </key>

    <key name="option" enum="eu.zderadicka.sample.enum">
        <default>'option1'</default>
        <summary>Some setting requiring options</summary>
        <description>Some options to choose from</description>
    </key>

    <child name="some-details" schema="eu.zderadicka.sample.child"/>
  </schema>

  <schema id="eu.zderadicka.sample.child">
      <key name="name" type="s">
          <default>''</default>
          <summary>User given name</summary>
      </key>
  </schema>
</schemalist>
```


Each schema has an unique  id (using dot notation to make it unique) and also it needs to have a  path under whitch values are stored. But path is derived from id (dots converted to slashes), so it is not necessary to specify it, unless you plan to use some special path, then you can do it with path attribute on schema element.

Within schema you can define various elements with simple or complex types (values are stored as GLib.Variant - so see for its<a href="http://developer.gnome.org/glib/stable/glib-GVariantType.html"> types definition notation</a>). For integer types you can define ranges (see line 16), or define enumerated  type (see lines 3-7 and 36).  Also the schema can have a child schema - when this child schema will have path path/of/parent/child-name/ (and is accessible via `get_child('child-name')` method of Settings object).

Before we can work with schema we have to compile it, schemas normally reside in directory /usr/share/glib-2.0/schemas  - so we should copy our schema there (with mandatory extension gschema.xml)  and compile:

`sudo cp my-schema.gschema.xml /usr/share/glib-2.0/schemas`
`glib-schema-compile  /usr/share/glib-2.0/schemas`

Sometime it is not convenient (especially during development) to have schema in central location -  schema can also reside in the local directory and can be compiled there `glib-compile-schemas --strict .` (strict option provides rigid check of our schema).   However this will require bit more complicated way how to instantiate schema in program - I''l describe it latter.

In python we can use GObject Introspection to work with GSettings, GSettings are part of GIO library.  To import and instantiate schema we can use this code:


```python
from gi.repository import Gio

settings = Gio.Settings('eu.zderadicka.sample')
```


Now we can get and set values like this (for all available methods of Settings class see<a href="http://developer.gnome.org/gio/stable/GSettings.html"> its C documentation</a>\- in python they are available without g\_settings\_ prefix) :


```python
from gi.repository import GLib

settings.set_int('timeout', 5)
timeout=settings.get_int('timeout')
settings.set_string ('option', 'option1')
my_option=settings.get_string('option')
settings.set_value('list-of-string', GLib.Variant('as', ['string1', 'string2']))
strings_list=settings.get_value('list-of-strings').unpack()
```


For complex type 'as' we  use Variant constructor and Variant unpack method to convert from/to python native types as show above.


###  How to work with schema in local directory


In order to instantiate schema that is in a local directory we have to do these several steps:


```python
schema_source=Gio.SettingsSchemaSource.new_from_directory(DIRECTORY, 
                Gio.SettingsSchemaSource.get_default(), False)
schema=Gio.SettingsSchemaSource.lookup(schema_source, schema_id,False)
if not schema:
    raise Exception("Cannot get GSettings  schema")
instance= Gio.Settings.new_full(schema, None, path)
```


This opens Settings with schema from DIRECTORY.    In an application it would be nice if it opens local schema, while in development, but when installed regularly  it' uses schema from central location.   In my project <a href="/wp-content/uploads/thetool.png" title="TheTool">thetool</a> I created class that  does this - you can check it <a href="https://github.com/izderadicka/thetool/blob/master/thetool/gsettings.py">here</a>.
On line 6 the second parameter, which is None, can be an instance of  configuration back-end, this way I think you can even have separated store for development - but did not play with it yet.


### Binding of settings to object properties


One of very cools features of GSettings is that you can bind some setting directly to a property of GObject and setting will set this property initially and then setting changes whenever the property changes.   This is nice feature for a configuration dialogue, where we can bind settings to widgets like this (in \_\_init\_\_ method of configuration window):


```python
settings.bind('enable-something', self.my_switch_widget, 'active', Gio.SettingsBindFlags.DEFAULT)
```




###  1-n relationship


The child element of schema enables 1-1 relationship (because name is already in schema).  However consider this scenario - I need do define some device configuration and my application works with many devices.  Each configuration is similar, but have different values.

For this we  define key  of type array of strings in main schema like this:


```html
 <key name="devices" type="as">
        <default>[]</default>
        <summary>My Devices</summary>
        <description>...</description>
    </key>
```


This will keep unique keys to all know devices.

And we  create schema (in same file as main schema) for device configuration with id eu.zderadicka.sample.device, where all necessary keys for device configuration are defined.
In program can then easily get instance of schema for particular device with this function


```python
 def get_device_settings(main_settings,  device_id):
        p=main_settings.get_property('path')
        if not p.endswith('/'):
            p+='/'
        p+=device_id+'/'
        return Gio.Settings('eu.zderadicka.sample.device', p)
```


And of course we need to update devices list in main settings whenever we add or remove device from application configuration.


### Issues


The only unpleasant issue I've found is that when you try to reach key, that is not defined in the schema - then application crashes (at least that was my case). Luckily GSettings write some warning on stderr first so it's clear what is the problem.

Also I'm not sure how to delete unused configurations - does not seem you to be available  via GSetting interface.   dconf tool has option reset, which will remove path without attached schema - so in our example of devices we can do `dconf reset -f /eu/zderadicka/sample/device-xyz` to remove configuration for device-xyz.

+++
title = "Protecting Django Application Against Brute Force Password Guessing"
path = "/protecting-django-application-against-brute-force-password-guessing/"
date = "2014-01-18T11:13:02"
include_in_feeds = true
[extra]
wordpress_id = 724
kind = "post"
node_key = "724"
author = "admin"
source_url = "http://zderadicka.eu/protecting-django-application-against-brute-force-password-guessing/"
source_guid = "http://zderadicka.eu/?p=724"
source_date_gmt = "2014-01-18 10:13:02"
[taxonomies]
category = ["Programming", "Security"]
tag = ["django", "python", "security"]
+++
<a href="/wp-content/uploads/lock.png"><img alt="lock" class="wp-image-733 alignleft" decoding="async" height="180" loading="eager" sizes="(max-width: 124px) 100vw, 124px" src="/wp-content/uploads/lock-207x300.png" srcset="/wp-content/uploads/lock-207x300.png 207w, /wp-content/uploads/lock.png 354w" width="124"/></a>When you bring  your web application live, you can expected various types of attacks -   one could be a brute force scanning of possible logins.   As a standard mean of prevention against such types of attacks login should be temporarily disabled after some number of unsuccessful attempts.  For [Django](http://djangoproject.com) nice package called [django-lockout](https://github.com/brianjaystanley/django-lockout) exists.

Main advantage of this package is that it keeps history of unsuccessful login attempts in memory (using Django cache system),  so checks are very quick.   django-lockout is fairly easy to implement, however I've found one issue, when it is used together with django admin site.

<span id="more-724"></span>django-lockout is  monkey-patching `django.contrib.auth.authenticate` function (this function is wrapped in custom decorator, that handles checking and blocking of unsuccessful login attempts).  This patching is done in  middle-ware class of django-lockout , as part of  its instantiation.   However as many things in Django,  instantiation of middle-ware classes    is done in latest possible moment -  in this case when first request comes.   And this was source of my issues with django-lockout -   if  we get reference to  `django.contrib.auth.authenticate` function before middle-ware instantiation,  we get unpatched version of the function.

And exactly this happens if we include admin site  into  `urls.py`:


```python
from django.contrib import admin
admin.autodiscover()
```


Import of `admin` causes also import of  ` django.contrib.auth.forms.AuthenticationForm  `, which imports:


```python
from django.contrib.auth import authenticate, get_user_model
```


so we end up with `AuthenticationForm`, which uses unpatched  `authenticate` function.   To fix this we  create subclass of  `AuthenticationForm` :


```python
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from lockout.exceptions import LockedOut

class AuthenticationLockForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            try:
                self.user_cache = auth.authenticate(username=username,
                                           password=password)
            except LockedOut:
                raise ValidationError(_('Login is temporarily disabled due to high amount of unsuccessful attempts from your address - try again later'))
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login']% {'username': self.username_field.verbose_name})
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        self.check_for_test_cookie()
        return self.cleaned_data
```


Method `clean` is overridden with two important changes -   first -  we refer `auth.authenticate`  (via package reference) so we get now patched version of the function,  second - we handle `LockedOut` exception to provide appropriate message.

This modified form has to be used for our application login page (in`  urls.py `):


```python
url(r'^login/$',
    auth_views.login,
    {'template_name': 'registration/login.html',
    'authentication_form': AuthenticationLockForm},
    name='auth_login'),
```


and we also have to patch admin site to use this form (also in `urls.py`):


```python
from django.contrib import admin
#patch site login form
admin.site.login_form=AuthenticationLockForm
admin.autodiscover()
```

<p align="center">
  <img src="docs/images/django-github-sso.png" alt="Django GitHub SSO"/>
</p>
<p align="center">
<em>Easily integrate GitHub Authentication into your Django projects</em>
</p>

<p align="center">
<a href="https://pypi.org/project/django-github-sso/" target="_blank">
<img alt="PyPI" src="https://img.shields.io/pypi/v/django-github-sso"/></a>
<a href="https://github.com/megalus/django-github-sso/actions" target="_blank">
<img alt="Build" src="https://github.com/megalus/django-github-sso/workflows/tests/badge.svg"/>
</a>
<a href="https://www.python.org" target="_blank">
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/django-github-sso"/>
</a>
<a href="https://www.djangoproject.com/" target="_blank">
<img alt="PyPI - Django Version" src="https://img.shields.io/pypi/djversions/django-github-sso"/>
</a>
</p>

## Welcome to Django GitHub SSO

This library aims to simplify the process of authenticating users with GitHub in Django Admin pages,
inspired by libraries like [django-admin-sso](https://github.com/matthiask/django-admin-sso/)

---

### Documentation

* Docs: https://megalus.github.io/django-github-sso/

---

### Install

```shell
$ pip install django-github-sso
```

### Configure

1. Add the following to your `settings.py` `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = [
    # other django apps
    "django.contrib.messages",  # Need for Auth messages
    "django_github_sso",  # Add django_github_sso
]
```

2. Navigate to `https://github.com/organizations/<YOUR ORGANIZATION>/settings/applications`, then select or create a new `Org OAuth App`.  From that, retrieve your `Client ID` and `Client Secret`.

3. On the same page, add the address `http://localhost:8000/github_sso/callback/` on the "Authorization callback URL" field.

4.  Add both credentials in your `settings.py`:

```python
# settings.py

GITHUB_SSO_CLIENT_ID = "your Client ID here"
GITHUB_SSO_CLIENT_SECRET = "your Client Secret  here"
```

5. Let Django GitHub SSO auto create users which have access to your repositories:

```python
# settings.py

GITHUB_SSO_NEEDED_REPOS = ["example/example-repo"]  # user needs to be a member of all repos listed
```

6. In `urls.py` please add the **Django-Github-SSO** views:

```python
# urls.py

from django.urls import include, path

urlpatterns = [
    # other urlpatterns...
    path(
        "github_sso/", include("django_github_sso.urls", namespace="django_github_sso")
    ),
]
```

7. And run migrations:

```shell
$ python manage.py migrate
```

That's it. Start django on port 8000 and open your browser in `http://localhost:8000/admin/login` and you should see the
GitHub SSO button.

<p align="center">
   <img src="docs/images/django_login_with_github_light.png"/>
</p>

---

## License

This project is licensed under the terms of the MIT license.

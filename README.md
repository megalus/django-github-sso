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
<a href="https://github.com/megalus/django-github-sso/blob/main/LICENSE" target="_blank">
<img alt="License" src="https://img.shields.io/github/license/megalus/django-github-sso"/>
</a>
</p>

## Welcome to Django GitHub SSO

This library simplifies the process of authenticating users with GitHub in Django projects. It adds a "Login with GitHub" button to your Django admin login page, allowing users to authenticate using their GitHub accounts.

Unlike more complex solutions like django-allauth, Django GitHub SSO focuses on simplicity and ease of use, with minimal configuration required.

### Features

- Simple integration with Django admin
- Automatic user creation based on GitHub credentials
- Customizable authentication filters (by domain, organization, or repository)
- Compatible with various Django admin skins
- Support for multiple SSO providers
- Light and dark mode support

---

### Documentation

Full documentation is available at: [https://megalus.github.io/django-github-sso/](https://megalus.github.io/django-github-sso/)

---

### Requirements

- Python 3.11+
- Django 4.2+
- A GitHub account or organization

### Installation

```shell
$ pip install django-github-sso
```

> **Compatibility**
> - Python 3.11, 3.12, 3.13
> - Django 4.2, 5.0, 5.1, 5.2
>
> Older python/django versions are not supported.

### Quick Configuration

1. Add the following to your `settings.py` `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = [
    # other django apps
    "django.contrib.messages",  # Required for Auth messages
    "django_github_sso",  # Add django_github_sso
]
```

2. Navigate to `https://github.com/organizations/<YOUR ORGANIZATION>/settings/applications`, then select or create a new `OAuth App`.

3. On the GitHub OAuth App settings page, add the address `http://localhost:8000/github_sso/callback/` (or your domain) in the "Authorization callback URL" field.

4. Add your GitHub OAuth credentials to your `settings.py`:

```python
# settings.py

GITHUB_SSO_CLIENT_ID = "your Client ID here"
GITHUB_SSO_CLIENT_SECRET = "your Client Secret here"
```

5. Configure user authorization filters (at least one is required):

```python
# settings.py

# Choose one or more of these options:
GITHUB_SSO_ALLOWABLE_DOMAINS = ["example.com"]  # Check against user's primary email
GITHUB_SSO_ALLOWABLE_ORGS = ["example"]  # User must be a member of all orgs listed
GITHUB_SSO_NEEDED_REPOS = ["example/example-repo"]  # User must have access to all repos listed
```

6. Add the Django GitHub SSO URLs to your `urls.py`:

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

7. Run migrations:

```shell
$ python manage.py migrate
```

That's it! Start Django and navigate to `http://localhost:8000/admin/login` to see the GitHub SSO button:

<p align="center">
   <img src="docs/images/django_login_with_github_light.png"/>
</p>

### Environment Variables

For security, it's recommended to use environment variables for your GitHub credentials:

```python
# settings.py
import os

GITHUB_SSO_CLIENT_ID = os.environ.get("GITHUB_SSO_CLIENT_ID")
GITHUB_SSO_CLIENT_SECRET = os.environ.get("GITHUB_SSO_CLIENT_SECRET")
```

## Example project

A minimal Django project using this library is included in this repository under `example_github_app/`.
- Read the step-by-step instructions in example_github_app/README.md
- Use it as a reference to configure your own project settings and URLs

---

## License

This project is licensed under the terms of the MIT license.

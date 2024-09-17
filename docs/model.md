# Getting GitHub info

## The User model

**Django GitHub SSO** saves in the database the following information from GitHub, using current `User` model:

* `email`: The primary verified email address of the user.
* `first_name`: The first name of the user.
* `last_name`: The last name of the user.
* `username`: The primary verified email address of the user
* `password`: An unusable password, generated using `get_unusable_password()` from Django.

Getting data on code is straightforward:

```python
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest

@login_required
def retrieve_user_data(request: HttpRequest) -> JsonResponse:
    user = request.user
    return JsonResponse({
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
    })
```

## The GitHubSSOUser model

Also, on the `GitHubSSOUser` model, it saves the following information:

* `github_id`: The internal GitHub user ID.
* `picture_url`: The GitHub user picture URL.
* `user_name`: The public GitHub user ID.

This is a one-to-one relationship with the `User` model, so you can access this data using the `githubssouser` reverse
relation attribute:

```python
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest

@login_required
def retrieve_user_data(request: HttpRequest) -> JsonResponse:
    user = request.user
    return JsonResponse({
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "github_id": user.githubssouser.github_id,
        "picture_url": user.githubssouser.picture_url,
        "user_name": user.githubssouser.user_name,
    })
```

You can also import the model directly, like this:

```python
from django_github_sso.models import GitHubSSOUser

github_info = GitHubSSOUser.objects.get(user=user)
```

!!! tip "You can disable this model"
    If you don't want to save this basic data in the database, you can disable the `GitHubSSOUser` model by setting the
    `GITHUB_SSO_SAVE_BASIC_GITHUB_INFO` configuration to `False` in your `settings.py` file.


## About GitHub Scopes

To retrieve this data, **Django GitHub SSO** uses the following scope from [Scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps):

```python
GITHUB_SSO_SCOPES = [  # GitHub default scope
   "read:user", "user:email", "read:org"
]
```

You can change this scopes overriding the `GITHUB_SSO_SCOPES` setting in your `settings.py` file. But if you ask the user
to authorize more scopes, this plugin will not save this additional data in the database. You will need to implement
your own logic to save this data, calling GitHub again. You can see an example [here](./advanced.md).

!!! info "The main goal here is simplicity"
    The main goal of this plugin is to be simple to use as possible. But it is important to ask the user **_once_** for the scopes.
    That's why this plugin permits you to change the scopes, but will not save the additional data from it.

## The Access Token
To make login possible, **Django GitHub SSO** needs to get an access token from GitHub. This token is used to retrieve
User info to get or create the user in the database. If you need this access token, you can get it inside the User Request
Session, like this:

```python
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest

@login_required
def retrieve_user_data(request: HttpRequest) -> JsonResponse:
    user = request.user
    return JsonResponse({
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "github_id": user.githubssouser.github_id,
        "picture_url": user.githubssouser.picture_url,
        "user_name": user.githubssouser.user_name,
        "access_token": request.session["github_sso_access_token"],
    })
```

Saving the Access Token in User Session is disabled, by default, to avoid security issues. If you need to enable it,
you can set the configuration `GITHUB_SSO_SAVE_ACCESS_TOKEN` to `True` in your `settings.py` file. Please make sure you
understand how to [secure your cookies](https://docs.djangoproject.com/en/4.2/ref/settings/#session-cookie-secure)
before enabling this option.

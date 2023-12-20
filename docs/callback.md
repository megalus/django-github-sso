# Get your Callback URI

The callback URL is the URL where your GitHub will redirect the user after the
authentication process. This URL must be registered in your GitHub OAuth App.

---

## The Callback URI
The callback URI is composed of `{scheme}://{netloc}/{path}/`, where the _netloc_ is the domain name of your Django
project, and the _path_ is `/github_sso/callback/`. For example, if your Django project is hosted on
`https://myproject.com`, then the callback URL will be `https://myproject.com/github_sso/callback/`.

So, let's break each part of this URI:

### The scheme
The scheme is the protocol used to access the URL. It can be `http` or `https`. **Django-GitHub-SSO** will select the
same scheme used by the URL which shows to you the login page.

For example, if you're running locally, like `http://localhost:8000/accounts/login`, then the callback URL scheme
will be `http://`.

??? question "How about a Reverse-Proxy?"
    If you're running Django behind a reverse-proxy, please make sure you're passing the correct
    `X-Forwarded-Proto` header to the login request URL.

### The NetLoc
The NetLoc is the domain of your Django project. It can be a dns name, or an IP address, including the Port, if
needed. Some examples are: `example.com`, `localhost:8000`, `api.my-domain.com`, and so on. To find the correct netloc,
**Django-GitHub-SSO** will check, in that order:

- If settings contain the variable `GITHUB_SSO_CALLBACK_DOMAIN`, it will use this value.
- If Sites Framework is active, it will use the domain field for the current site.
- The netloc found in the URL which shows you the login page.

### The Path
The path is the path to the callback view. It will be always `/<path in urls.py>/callback/`.

Remember when you add this to the `urls.py`?

```python
from django.urls import include, path

urlpatterns = [
    # other urlpatterns...
    path(
        "github_sso/", include(
            "django_github_sso.urls",
            namespace="django_github_sso"
        )
    ),
]
```

The path starts with the `github_sso/` part. If you change this to `sso/` for example, your callback URL will change to
`https://myproject.com/sso/callback/`.

---

## Registering the URI

If you need to change your callback URL, navigate back to `https://github.com/organizations/<YOUR ORGANIZATION>/settings/applications`, change the field `Authorization callback URL` and click `Update Application`.

![change_github_callback.png](images/change_github_callback.png)

!!! tip "Do not forget the trailing slash"
    Many errors on this step are caused by forgetting the trailing slash:

    * Good: `http://localhost:8000/github_sso/callback/`
    * Bad: `http://localhost:8000/github_sso/callback`

---

In the next step, we will configure **Django-GitHub-SSO** to auto create the Users.

# Setup Django URLs

The base configuration for Django URLs is the same we have described as before:
```python
# urls.py

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
You can change the initial Path - `github_sso/` - to whatever you want - just remember to change it in your
GitHub OAuth configuration.

## Overriding the Login view or Path

If you need to override the login view, or just the path, please add on the new view/class the
**Django SSO Admin** login template:

```python
from django.contrib.auth.views import LoginView
from django.urls import path

urlpatterns = [
    # other urlpatterns...
    path(
        "accounts/login/",
        LoginView.as_view(
            # The modified form with GitHub button
            template_name="github_sso/login.html"
        ),
    ),
]
```

or you can use a complete custom class:

```python
from django.contrib.auth.views import LoginView


class MyLoginView(LoginView):
    template_name = "github_sso/login.html"
```

# Using Django Admin

**Django GitHub SSO** integrates with Django Admin, adding an Inline Model Admin to the User model. This way, you can
access the GitHub SSO data for each user.

## Using Custom User model

If you are using a custom user model, you may need to add the `GitHubSSOInlineAdmin` inline model admin to your custom
user model admin, like this:

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_github_sso.admin import (
    GitHubSSOInlineAdmin, get_current_user_and_admin
)

CurrentUserModel, last_admin, LastUserAdmin = get_current_user_and_admin()

if admin.site.is_registered(CurrentUserModel):
    admin.site.unregister(CurrentUserModel)


@admin.register(CurrentUserModel)
class CustomUserAdmin(LastUserAdmin):
    inlines = (
        tuple(set(list(last_admin.inlines) + [GitHubSSOInlineAdmin]))
        if last_admin
        else (GitHubSSOInlineAdmin,)
    )
```

The `get_current_user_and_admin` helper function will return:

* the current registered **UserModel** in Django Admin (default: `django.contrib.auth.models.User`)
* the current registered **UserAdmin** in Django (default: `django.contrib.auth.admin.UserAdmin`)
* the **instance** of the current registered UserAdmin in Django (default: `None`)


Use these objects to maintain previous inlines and register your custom user model in Django Admin.

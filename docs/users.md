# Auto Creating Users

**Django GitHub SSO** can automatically create users from GitHub SSO authentication. To enable this feature, you need to
setup at least one of the available user filters in your `settings.py`. Let's review each one of them.

## Available Filters

### Allowable Repositories

If you want to allow any GitHub users that are members of a specific repository, you can set the `GITHUB_SSO_ALLOWABLE_REPOS`

```python
# settings.py

GITHUB_SSO_ALLOWABLE_REPOS = ["my-company/my-repo"]
```

This is the simpler filter, if the user is a member of the repository, it will be allowed to login.

!!! tip "Always use repository's full name"
    Please remember to use the full name of the repository, including the organization name. Example: `my-company/my-repo`

### Allowable Organizations

If you want to allow any GitHub users that are members of a specific organization, you can set the `GITHUB_SSO_ALLOWABLE_ORGS`

```python
# settings.py

GITHUB_SSO_ALLOWABLE_ORGS = ["my-company"]
```

User must be member, not outside collaborator, for each org listed. To allow outside collaborators, you can set the
`GITHUB_SSO_ALLOW_OUTSIDE_COLLABORATORS` setting to `True`:

```python
# settings.py

GITHUB_SSO_ALLOWABLE_ORGS = ["my-company"]
GITHUB_SSO_ALLOW_OUTSIDE_COLLABORATORS = True
```

### Allowable Domains for Emails

If you want to allow any GitHub users with a specific email domain, you can set the `GITHUB_SSO_ALLOWABLE_DOMAINS` setting:

```python
# settings.py
GITHUB_SSO_ALLOWABLE_DOMAINS = ["my-company.com"]
```

In this example, any users with a `my-company.com` primary email will be allowed to login. On GitHub, a user can have multiple
emails, but only one of them is the primary email. This is the email that will be used for the filter. If you want to check
all user emails with the allowable domains, you can set the `GITHUB_SSO_CHECK_ONLY_PRIMARY_EMAIL` setting to `False`:

```python
# settings.py

GITHUB_SSO_ALLOWABLE_DOMAINS = ["my-company.com"]
GITHUB_SSO_CHECK_ONLY_PRIMARY_EMAIL = False
```

!!! important "*Django GitHub SSO* will always check only against *verified* emails from the user."

??? question "What happens if user has more than one valid email?"
    If the user has more than one valid verified email - for example `user@my-company.com` and `full.name@my-company.com`, the first one will be used.


## Combining Filters

You can combine the filters to allow only users that match all filters. Some examples:

```python
# settings.py

# Allow only users that have a verified email with the my-company.com domain
GITHUB_SSO_ALLOWABLE_DOMAINS = ["my-company.com"]
GITHUB_SSO_CHECK_ONLY_PRIMARY_EMAIL = False
```

```python
# Allow only users that are members of the my-company organization
# and have a primary email with the my-company.com domain
# and are members of the my-repo repository
GITHUB_SSO_ALLOWABLE_ORGS = ["my-company"]
GITHUB_SSO_ALLOWABLE_DOMAINS = ["my-company.com"]
GITHUB_SSO_ALLOWABLE_REPOS = ["my-company/my-repo"]
```

```python
# Allow only users that are members of the my-company organization
# but accept any email domain and outside collaborators
GITHUB_SSO_ALLOWABLE_ORGS = ["my-company"]
GITHUB_SSO_ALLOW_OUTSIDE_COLLABORATORS = True
```

!!! warning "Allowing any GitHub user in your Django Admin"
    * You need to set the option `GITHUB_SSO_ALLOW_ALL_USERS=True` to allow any GitHub user in your Django Admin.
    * If you set any filters, this option will be ignored.
    * Please make sure you understand the security implications of this option.


## Disabling the auto-create users

You can disable the auto-create users feature by setting the `GITHUB_SSO_AUTO_CREATE_USERS` setting to `False`:

```python
GITHUB_SSO_AUTO_CREATE_USERS = False
```

You can also disable the plugin completely:

```python
GITHUB_SSO_ENABLED = False
```

## Giving Permissions to Auto-Created Users

If you are using the auto-create users feature, you can give permissions to the users that are created automatically. To do
this, you can set the following options in your `settings.py`:

```python
# List of emails or github user_names that will be created as staff
GITHUB_SSO_STAFF_LIST = ["my-email@my-company.com", "my-user-name"]

# List of emails or github user_names that will be created as superuser
GITHUB_SSO_SUPERUSER_LIST = ["another-email@my-company.com" "another-user-name"]

# If True, the first user that checks in will be created as superuser
# if no superuser exists in the database at all
GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER = True
```

!!! tip "Which Email will be used to save this user on Django?"
    The primary email will be used. If the option `GITHUB_SSO_CHECK_ONLY_PRIMARY_EMAIL` is `False`
    and  `GITHUB_SSO_ALLOWABLE_DOMAINS` is `True` the first valid email will be used.

For staff user creation _only_, you can add all users using "*" as the value:

```python
# Use "*" to add all users as staff
GITHUB_SSO_STAFF_LIST = ["*"]
```

## Fine-tuning validation before user validation

If you need to do some custom validation _before_ user is validated, you can set the
`GITHUB_SSO_PRE_VALIDATE_CALLBACK` setting to import a custom function that will be called before the user is created.
This function will receive two arguments: the `github_user` instance from GitHub package and `request` objects.

```python
# myapp/hooks.py
def pre_validate_user(github_user, request):
    # Check some info from GitHub user and/or request
    return True  # The user can be created
```

Please note, even if this function returns `True`, the user can be denied if their email is not valid.


## Fine-tuning user info before user creation

If you need to do some processing _before_ user is created, you can set the
`GITHUB_SSO_PRE_CREATE_CALLBACK` setting to import a custom function that will be called before the user is created.
This function will receive two arguments: the `github_user` instance and `request` objects.

!!! tip "You can add custom fields to the user model here"

    The `pre_create_callback` function can return a dictionary with the fields and values that will be passed to
    `User.objects.create()` as the `defaults` argument. This means you can add custom fields to the user model here or
    change default values for some fields, like `username`.

    If not defined, the field `username` is always the Github Login name.

    You can't change the fields: `first_name`, `last_name`, `email` and `password` using this callback. These fields are
    always passed to `User.objects.create()` with the values from Graph API and the password is always unusable.


```python
import arrow

def pre_create_callback(
    github_user: NamedUser | AuthenticatedUser, request: HttpRequest
) -> dict | None:
    """
    Callback function called before user is created.

    params:
        github_user: GitHub User Instance.
        request: HttpRequest object.

    return: dict content to be passed
            to User.objects.create() as `defaults` argument.
    """

    return {
        "date_joined": arrow.utcnow().shift(days=-1).datetime,
    }
```

## Fine-tuning users before login

If you need to do some processing _after_ user is created or retrieved,
but _before_ the user is logged in, you can set the
`GITHUB_SSO_PRE_LOGIN_CALLBACK` setting to import a custom function that will be called before the user is logged in.
This function will receive two arguments: the `user` and `request` objects.

```python
# myapp/hooks.py
def pre_login_user(user, request):
    # Do something with the user
    pass

# settings.py
GITHUB_SSO_PRE_LOGIN_CALLBACK = "myapp.hooks.pre_login_user"
```

Please remember this function will be invoked only if a user exists, and if it is active.
In other words, if the user is eligible for login.

!!! tip "You can add your hooks to customize all steps:"
    * `GITHUB_SSO_PRE_VALIDATE_CALLBACK`: Run before the user is validated.
    * `GITHUB_SSO_PRE_CREATE_CALLBACK`: Run before the user is created.
    * `GITHUB_SSO_PRE_LOGIN_CALLBACK`: Run before the user is logged in.


!!! warning "Be careful with these options"
    The idea here is to make your life easier, especially when testing. But if you are not careful, you can give
    permissions to users that you don't want, or even worse, you can give permissions to users that you don't know.
    So, please, be careful with these options.

---

For the last step, we will look at the Django URLs.

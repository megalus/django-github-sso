# Advanced Use

## Using Custom Authentication Backend

If the users need to log in using a custom authentication backend, you can use the `GITHUB_SSO_AUTHENTICATION_BACKEND`
setting:

```python
# settings.py

GITHUB_SSO_AUTHENTICATION_BACKEND = "myapp.authentication.MyCustomAuthenticationBackend"
```

## Using GitHub as Single Source of Truth

If you want to use GitHub as the single source of truth for your users, you can simply set the
`GOOGLE_SSO_ALWAYS_UPDATE_USER_DATA`. This will enforce the basic user data (first name, last name, email and picture) to be
updated at every login.

```python
# settings.py

GITHUB_SSO_ALWAYS_UPDATE_USER_DATA = True  # Always update user data on login
```

If you need more advanced logic, you can use the `GITHUB_SSO_PRE_LOGIN_CALLBACK` setting to import custom data from GitHub
(considering you have configured the right scopes and possibly a Custom User model to store these fields).

For example, you can use the following code to retrieve repository projects:

```python
# settings.py

GITHUB_SSO_SAVE_ACCESS_TOKEN = True  # You will need this token
GITHUB_SSO_PRE_LOGIN_CALLBACK = "hooks.pre_login_user"
GITHUB_SSO_SCOPES = [
    "read:user",
    "user:email",
    "read:org",
    "read:project",  # <- additional scope
]
```

```python
# myapp/hooks.py
from github import Auth, Github
from loguru import logger


def pre_login_user(user, request):
    token = request.session.get("github_sso_access_token")
    if token:
        # Request GitHub User Info
        # To retrieve user's additional data, you need to add the respective scope,
        # For example, "read:project" in settings GITHUB_SSO_SCOPES
        auth = Auth.Token(token)
        g = Github(auth=auth)
        github_user = g.get_user()
        project_info = github_user.get_repos()[0].get_projects()
        logger.debug(f"Updating User Data with GitHub Project Info: {project_info}")
```

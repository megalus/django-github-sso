# Troubleshooting Guide

### Common questions:

??? question "Admin Message: _**State Mismatched. Time expired?**_"
    This error occurs when the user is redirected to the Google login page and then returns to the Django login page but
    original state are not found or session was expired. Please check if the browser has the anonymous session created by Django.

??? question "Admin Message: _**User not allowed to login**_"
    Please check your filters, some combinations can filter all users. Use the option `GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES`
    to show additional error messages in django message system when authentication fails.

??? question "There's too much information on logs and messages from this app."
    You can disable the logs using the `GITHUB_SSO_ENABLE_LOGS` setting and the messages using the `GITHUB_SSO_ENABLE_MESSAGES` setting.

??? question "System goes looping to admin after login."
    This is because the user data was received from GitHub, but the user was not created in the database or is not active.
    To see these errors please check the logs or enable the option `GITHUB_SSO_SHOW_FAILED_LOGIN_MESSAGE` to see failed
    login messages on browser. Please, make note these messages can be used on exploit attacks.

??? question "When I config a custom Authentication Backend using GITHUB_SSO_AUTHENTICATION_BACKEND, the lib stops to login, without errors or logs."
    This is because the value of `GITHUB_SSO_AUTHENTICATION_BACKEND` is not a valid authentication backend import path.
    Please check the value of this setting and make sure it is a valid import path to a Django authentication backend.

??? question "When using one package for Admin and another for Pages, the user can enter in Admin, even if I configure the Pages SSO to not give any admin rights"
    Please check if the user is not already a staff or superuser in the database, especially if you're using the
    `MICROSOFT_SSO_UNIQUE_EMAIL` and `GITHUB_SSO_UNIQUE_EMAIL` options. If the user is already a staff or superuser,
    he will be able to enter in Admin, even if the SSO package for Pages does not give him any admin rights.

??? question "Got a "KeyError: 'NAME'" error after set SSO_USE_ALTERNATE_W003"
    If you get a `KeyError: 'NAME'` error, please set a `NAME` in `TEMPLATES` at `settings.py`:

    ```python
    # settings.py

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "NAME" : "default",  # <-- Add name here
            "DIRS": [BASE_DIR / "templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]
    ```

??? question "Got this error when migrating: 'The model User is already registered with 'core.GitHubSSOUserAdmin'"
    This is because you're already define a custom User model and admin in your project. You need to [extended the
    existing user model](https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#extending-the-existing-user-model)
    unregistering your current User Admin class and add manually the `GitHubSSOUserAdmin` in your custom class.
    You can use the `get_current_user_and_admin` helper as explained [here](admin.md) (the recommended action), or
    alternately, you can add the `django-google-sso` at the end of your `INSTALLED_APPS` list.

### Example App

To test this library please check the `Example App` provided [here](https://github.com/megalus/django-github-sso/tree/main/example_github_app).

### Not working?

Don't panic. Get a towel and, please, open an [issue](https://github.com/megalus/django-github-sso/issues).

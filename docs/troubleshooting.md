# Troubleshooting Guide

### Common errors:

??? question "Admin Message: _**State Mismatched. Time expired?**_"
    This error occurs when the user is redirected to the Google login page and then returns to the Django login page but
    original state are not found. Please check if the browser has the anonymous session created by Django.

??? question "Admin Message: _**User not allowed to login**_"
    Please check your filters, some combinations can filter all users. Use the option `GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES`
    to show additional error messages in django message system when authentication fails.

??? question "System goes looping to admin after login."
    This is because the user data was received from GitHub, but the user was not created in the database or is not active.
    To see these errors please check the logs or enable the option `GITHUB_SSO_SHOW_FAILED_LOGIN_MESSAGE` to see failed
    login messages on browser. Please, make note these messages can be used on exploit attacks.

### Example App

To test this library please check the `Example App` provided [here](https://github.com/megalus/django-github-sso/tree/main/example_github_app).

### Not working?

Don't panic. Get a towel and, please, open an [issue](https://github.com/megalus/django-github-sso/issues).

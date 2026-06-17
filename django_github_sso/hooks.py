from django.http import HttpRequest
from github.AuthenticatedUser import AuthenticatedUser
from github.NamedUser import NamedUser

from django_github_sso.models import User


def pre_login_user(user: User, request: HttpRequest) -> None:
    """
    Callback function called after user is created/retrieved but before logged in.
    """


def pre_create_user(
    github_user: NamedUser | AuthenticatedUser, request: HttpRequest
) -> dict | None:
    """
    Callback function called before user is created.

    params:
        github_user: GitHub User Instance.
        request: HttpRequest object.

    return:
        By default, dict content to be passed to User.objects.get_or_create()
        as `defaults` argument.

        When GITHUB_SSO_PRE_CREATE_USER_RETURN_FULL_ARGS is True, the dict
        is passed as all kwargs to User.objects.get_or_create().
    """
    return {}


def pre_validate_user(
    github_user: NamedUser | AuthenticatedUser, request: HttpRequest
) -> bool:
    """
    Callback function called before user is validated.

    Must return a boolean to indicate if user is valid to login.

    params:
        github_user: GitHub User Instance.
        request: HttpRequest object.
    """
    return True

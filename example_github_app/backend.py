import arrow
from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest
from github import Auth, Github
from github.AuthenticatedUser import AuthenticatedUser
from github.NamedUser import NamedUser
from loguru import logger


class MyBackend(ModelBackend):
    """Simple test for custom authentication backend"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        return super().authenticate(request, username, password, **kwargs)


def pre_login_callback(user, request):
    """Callback function called before user is logged in."""

    # Example 1: Add SuperUser status to user
    messages.info(request, f"Running Pre-Login callback for user: {user}.")
    logger.debug(f"Running Pre-Login callback for user: {user}.")
    if not user.is_superuser or not user.is_staff:
        logger.info(f"Adding SuperUser status to email: {user.email}")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    # Example 2: Use GitHub Info as a unique source of truth
    token = request.session.get("github_sso_access_token")
    if token:
        # Request GitHub User Info
        # To retrieve user's additional data, you need to add the respective scope
        # For example, "read:project" in settings GITHUB_SSO_SCOPES
        auth = Auth.Token(token)
        g = Github(auth=auth)
        github_user = g.get_user()
        project_info = github_user.get_repos()[0].get_projects()
        logger.debug(f"Updating User Data with GitHub Project Info: {project_info}")


def pre_create_callback(
    github_user: NamedUser | AuthenticatedUser, request: HttpRequest
) -> dict | None:
    """
    Callback function called before user is created.

    params:
        github_user: GitHub User Instance.
        request: HttpRequest object.

    return: dict content to be passed to User.objects.create() as `defaults` argument.
    """

    return {
        "date_joined": arrow.utcnow().shift(days=-1).datetime,
    }


def pre_validate_callback(github_user: NamedUser | AuthenticatedUser, request) -> bool:
    """Callback function called before user is validated.

    Must return a boolean to indicate if user is valid to login.

    params:
        github_user: GitHub User Instance.
        request: HttpRequest object.
    """
    messages.info(request, f"Running Pre-Validate callback for: {github_user.id}.")
    return True

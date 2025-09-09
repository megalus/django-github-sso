import importlib
from copy import deepcopy
from typing import Generator
from unittest.mock import MagicMock
from urllib.parse import quote, urlencode

import pytest
from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sites.models import Site
from django.db import connection, models
from django.test import AsyncClient
from django.urls import reverse
from github import Github
from github.AuthenticatedUser import AuthenticatedUser, EmailData
from github.NamedUser import NamedUser
from github.Organization import Organization
from github.Repository import Repository

from django_github_sso import conf
from django_github_sso import conf as conf_module
from django_github_sso import views
from django_github_sso.main import GithubAuth

SECRET_PATH = "/secret/"


@pytest.fixture
def query_string():
    return urlencode(
        {
            "code": "12345",
            "state": "foo",
            "scope": " ".join(conf.GITHUB_SSO_SCOPES),
            "hd": "example.com",
            "prompt": "consent",
        },
        quote_via=quote,
    )


@pytest.fixture
def callback_request(rf, query_string):
    request = rf.get(f"/github_sso/callback/?{query_string}")
    middleware = SessionMiddleware(get_response=lambda req: None)
    middleware.process_request(request)
    request.session.save()
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)
    return request


@pytest.fixture
def callback_request_from_reverse_proxy(rf, query_string):
    request = rf.get(
        f"/github_sso/callback/?{query_string}", HTTP_X_FORWARDED_PROTO="https"
    )
    middleware = SessionMiddleware(get_response=lambda req: None)
    middleware.process_request(request)
    request.session.save()
    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)
    return request


@pytest.fixture
def callback_request_with_state(callback_request):
    request = deepcopy(callback_request)
    request.session["sso_state"] = "foo"
    request.session["sso_next_url"] = "/secret/"
    return request


@pytest.fixture
def email_data_mock():
    email_data_mock = MagicMock(EmailData)
    email_data_mock.primary = True
    email_data_mock.email = "peter@dailybugle.info"
    return email_data_mock


@pytest.fixture
def member_data_mock():
    member_data_mock = MagicMock(NamedUser)
    member_data_mock.name = "Peter Parker"
    member_data_mock.id = 12345
    member_data_mock.login = "spiderman"
    member_data_mock.avatar_url = "https://avatars.githubusercontent.com/u/12345?v=4"
    return member_data_mock


@pytest.fixture
def org_data_mock(member_data_mock):
    org_data_mock = MagicMock(Organization)
    org_data_mock.name = "example"
    org_data_mock.get_members.return_value = [member_data_mock]
    return org_data_mock


@pytest.fixture
def repo_data_mock():
    repo_data_mock = MagicMock(Repository)
    repo_data_mock.name = "repo-a"
    repo_data_mock.full_name = "example/repo-a"
    return repo_data_mock


@pytest.fixture
def auth_user_mock(org_data_mock, email_data_mock, repo_data_mock, member_data_mock):
    auth_user_mock = MagicMock(AuthenticatedUser)
    auth_user_mock.name = member_data_mock.name
    auth_user_mock.id = member_data_mock.id
    auth_user_mock.login = member_data_mock.login
    auth_user_mock.avatar_url = member_data_mock.avatar_url
    auth_user_mock.get_orgs.return_value = [org_data_mock]
    auth_user_mock.get_emails.return_value = [email_data_mock]
    auth_user_mock.get_repos.return_value = [repo_data_mock]
    return auth_user_mock


@pytest.fixture
def github_mock(auth_user_mock):
    github_mock = MagicMock(Github)
    github_mock.get_user.return_value = auth_user_mock
    return github_mock


@pytest.fixture
def member_data_mock_no_name():
    member_data_mock = MagicMock(NamedUser)
    member_data_mock.name = None
    member_data_mock.id = 12345
    member_data_mock.login = "spiderman"
    member_data_mock.avatar_url = "https://avatars.githubusercontent.com/u/12345?v=4"
    return member_data_mock


@pytest.fixture
def org_data_mock_no_name(member_data_mock_no_name):
    org_data_mock = MagicMock(Organization)
    org_data_mock.name = "example"
    org_data_mock.get_members.return_value = [member_data_mock_no_name]
    return org_data_mock


@pytest.fixture
def auth_user_mock_no_name(
    org_data_mock_no_name, email_data_mock, repo_data_mock, member_data_mock_no_name
):
    auth_user_mock = MagicMock(AuthenticatedUser)
    auth_user_mock.name = member_data_mock_no_name.name
    auth_user_mock.id = member_data_mock_no_name.id
    auth_user_mock.login = member_data_mock_no_name.login
    auth_user_mock.avatar_url = member_data_mock_no_name.avatar_url
    auth_user_mock.get_orgs.return_value = [org_data_mock_no_name]
    auth_user_mock.get_emails.return_value = [email_data_mock]
    auth_user_mock.get_repos.return_value = [repo_data_mock]
    return auth_user_mock


@pytest.fixture
def github_mock_no_name(auth_user_mock_no_name):
    github_mock = MagicMock(Github)
    github_mock.get_user.return_value = auth_user_mock_no_name
    return github_mock


@pytest.fixture
def updated_github_mocks(github_mock, auth_user_mock):
    g = deepcopy(github_mock)
    u = deepcopy(auth_user_mock)
    new_email = MagicMock(EmailData)
    new_email.primary = True
    new_email.email = "miles@verse.com"
    new_email.verified = True
    u.name = "Miles Morales"
    u.get_emails.return_value = [new_email]
    g.get_user.return_value = u
    return g, u


@pytest.fixture
def client_with_session(
    client,
    settings,
    mocker,
    github_mock,
    email_data_mock,
    org_data_mock,
    repo_data_mock,
    auth_user_mock,
):
    settings.GITHUB_SSO_PRE_LOGIN_CALLBACK = "django_github_sso.hooks.pre_login_user"
    settings.GITHUB_SSO_PRE_CREATE_CALLBACK = "django_github_sso.hooks.pre_create_user"
    settings.GITHUB_SSO_PRE_VALIDATE_CALLBACK = "django_github_sso.hooks.pre_validate_user"
    settings.GITHUB_SSO_ALLOWABLE_ORGS = ["example"]
    settings.GITHUB_SSO_NEEDED_REPOS = ["example/repo-a"]
    settings.ALLOWED_HOSTS = ["testserver", "site.com", "other-site.com"]
    mocker.patch.object(
        GithubAuth, "get_user_token", return_value={"access_token": "12345"}
    )
    importlib.reload(conf)
    session = client.session
    session.update({"sso_state": "foo", "sso_next_url": SECRET_PATH})
    session.save()
    mocker.patch("django_github_sso.views.Github", return_value=github_mock)
    mocker.patch.object(views.Github, "get_user", return_value=auth_user_mock)
    yield client


@pytest.fixture
def aclient_with_session(client_with_session, settings):
    """An alias for client_with_session to indicate async client usage."""
    settings.SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
    ac = AsyncClient()
    ac.cookies.update(client_with_session.cookies)
    return ac


@pytest.fixture
def callback_url(query_string):
    return f"{reverse('django_github_sso:oauth_callback')}?{query_string}"


@pytest.fixture
def default_site(settings):
    site, _ = Site.objects.update_or_create(
        id=1, defaults={"domain": "site.com", "name": "Default Site"}
    )
    settings.SITE_ID = site.id
    return site


@pytest.fixture
def other_site(settings):
    site, _ = Site.objects.get_or_create(
        domain="other-site.com", defaults={"name": "Other Site"}
    )
    settings.SITE_ID = None
    return site


@pytest.fixture
def custom_user_model(settings) -> Generator[type, None, None]:
    """
    Create a temporary custom user model, point AUTH_USER_MODEL to it,
    recreate GitHubSSOUser table to reference the new model, yield the
    custom user class and then fully restore the previous state.
    """
    # Capture previous state
    old_auth = settings.AUTH_USER_MODEL
    import django_github_sso.models as gt_models

    old_githubssouser = gt_models.GitHubSSOUser

    class CustomNamesUser(AbstractBaseUser):
        user_name = models.CharField(max_length=150, unique=True)
        mail = models.EmailField(unique=True)
        is_staff = models.BooleanField(default=False)
        is_active = models.BooleanField(default=True)

        USERNAME_FIELD = "user_name"
        EMAIL_FIELD = "mail"
        REQUIRED_FIELDS = ["mail"]

        class Meta:
            app_label = "django_github_sso"

        def __str__(self) -> str:
            return self.user_name

    # Register dynamic model and create its table
    apps.register_model("django_github_sso", CustomNamesUser)
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(CustomNamesUser)

    # Point to the new user model and reload conf + models so relations are rebuilt
    settings.AUTH_USER_MODEL = "django_github_sso.CustomNamesUser"
    importlib.reload(conf_module)
    gt_models = importlib.reload(gt_models)

    # Replace GitHubSSOUser DB table so its FK points to the new user model
    new_githubssouser = gt_models.GitHubSSOUser
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(old_githubssouser)
        schema_editor.create_model(new_githubssouser)

    importlib.reload(importlib.import_module("django_github_sso.main"))

    try:
        yield CustomNamesUser
    finally:
        # Teardown: remove new tables and restore original model/table
        gt_models = importlib.reload(gt_models)
        new_githubssouser = gt_models.GitHubSSOUser

        with connection.schema_editor() as schema_editor:
            # delete the GitHubSSOUser table that references the dynamic user
            schema_editor.delete_model(new_githubssouser)
            # delete the dynamic user table
            schema_editor.delete_model(CustomNamesUser)

        # restore AUTH_USER_MODEL and reload modules
        settings.AUTH_USER_MODEL = old_auth
        importlib.reload(conf_module)
        importlib.reload(gt_models)

        # recreate the original GitHubSSOUser table created by migrations
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(old_githubssouser)

        # unregister the dynamic model from the apps registry and clear caches
        app_models = apps.all_models.get("django_github_sso", {})
        app_models.pop("customnamesuser", None)
        apps.clear_cache()

        importlib.reload(importlib.import_module("django_github_sso.main"))

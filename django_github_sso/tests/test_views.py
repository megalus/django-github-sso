import importlib

import pytest
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse

from django_github_sso import conf
from django_github_sso.tests.conftest import SECRET_PATH

ROUTE_NAME = "django_github_sso:oauth_callback"


pytestmark = pytest.mark.django_db()


class MyBackend(ModelBackend):
    """Simple test for custom authentication backend"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        return super().authenticate(request, username, password, **kwargs)


def test_start_login(client, github_mock):
    # Arrange

    # Act
    url = reverse("django_github_sso:oauth_start_login") + "?next=/secret/"
    response = client.get(url)

    # Assert
    assert response.status_code == 302
    assert client.session["sso_next_url"] == SECRET_PATH


def test_start_login_none_next_param(client, github_mock):
    # Arrange

    # Act
    url = reverse("django_github_sso:oauth_start_login")
    response = client.get(url)

    # Assert
    assert response.status_code == 302
    assert client.session["sso_next_url"] == reverse(conf.GITHUB_SSO_NEXT_URL)


@pytest.mark.parametrize(
    "test_parameter",
    [
        "bad-domain.com/secret/",
        "www.bad-domain.com/secret/",
        "//bad-domain.com/secret/",
        "http://bad-domain.com/secret/",
        "https://malicious.example.com/secret/",
    ],
)
def test_exploit_redirect(client, github_mock, test_parameter):
    # Arrange

    # Act
    url = reverse("django_github_sso:oauth_start_login") + f"?next={test_parameter}"
    response = client.get(url)

    # Assert
    assert response.status_code == 302
    assert client.session["sso_next_url"] == SECRET_PATH


def test_github_sso_disabled(settings, client):
    # Arrange
    from django_github_sso import conf

    settings.GITHUB_SSO_ENABLED = False
    importlib.reload(conf)

    # Act
    response = client.get(reverse(ROUTE_NAME))

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert "GitHub SSO not enabled." in [
        m.message for m in get_messages(response.wsgi_request)
    ]


def test_missing_code(client):
    # Arrange
    importlib.reload(conf)

    # Act
    response = client.get(reverse(ROUTE_NAME))

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert "Authorization Code not received from SSO." in [
        m.message for m in get_messages(response.wsgi_request)
    ]


@pytest.mark.parametrize("querystring", ["?code=1234", "?code=1234&state=bad_dog"])
def test_bad_state(client, querystring):
    # Arrange
    importlib.reload(conf)
    session = client.session
    session.update({"sso_state": "good_dog"})
    session.save()

    # Act
    url = reverse(ROUTE_NAME) + querystring
    response = client.get(url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert "State Mismatch. Time expired?" in [
        m.message for m in get_messages(response.wsgi_request)
    ]


def test_invalid_email(
    client_with_session, settings, callback_url, github_mock, email_data_mock
):
    # Arrange
    from django_github_sso import conf

    settings.GITHUB_SSO_ALLOWABLE_DOMAINS = ["foobar.com"]
    importlib.reload(conf)

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert (
        f"Email address not allowed: {email_data_mock.email}. "
        f"Please contact your administrator."
        in [m.message for m in get_messages(response.wsgi_request)]
    )


def test_inactive_user(
    client_with_session, callback_url, github_mock, auth_user_mock, email_data_mock
):
    # Arrange
    User.objects.create(
        username=auth_user_mock.login,
        email=email_data_mock.email,
        is_active=False,
    )

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 1
    assert User.objects.get(email=email_data_mock.email).is_active is False


def test_new_user_login(client_with_session, callback_url, github_mock):
    # Arrange
    User.objects.all().delete()
    assert User.objects.count() == 0
    importlib.reload(conf)

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 1
    assert response.url == SECRET_PATH
    assert response.wsgi_request.user.is_authenticated is True


def test_existing_user_login(
    client_with_session,
    settings,
    github_mock,
    auth_user_mock,
    email_data_mock,
    callback_url,
):
    # Arrange
    from django_github_sso import conf

    existing_user = User.objects.create(
        username=auth_user_mock.login,
        email=email_data_mock.email,
        is_active=True,
    )

    settings.GITHUB_SSO_AUTO_CREATE_USERS = False
    importlib.reload(conf)

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 1
    assert response.url == SECRET_PATH
    assert response.wsgi_request.user.is_authenticated is True
    assert response.wsgi_request.user.email == existing_user.email


def test_missing_user_login(client_with_session, settings, callback_url, github_mock):
    # Arrange
    from django_github_sso import conf

    settings.GITHUB_SSO_AUTO_CREATE_USERS = False
    importlib.reload(conf)

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert response.url == "/admin/"
    assert response.wsgi_request.user.is_authenticated is False

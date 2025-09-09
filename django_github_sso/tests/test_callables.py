import pytest

from django_github_sso import conf
from django_github_sso.models import User

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.parametrize(
    "value, expected",
    [
        (lambda req: "dynamic_value", "dynamic_value"),
        ("static_value", "static_value"),
    ],
)
def test_value_from_conf(client_with_session, settings, value, expected):
    # Arrange
    settings.GITHUB_SSO_TEXT = value

    # Act
    response = client_with_session.get("/")
    response_text = (
        response.text if hasattr(response, "text") else response.content.decode()
    )

    # Assert
    assert expected in response_text


@pytest.mark.parametrize(
    "value, will_raise",
    [
        (True, False),
        (lambda req: True, True),
    ],
)
def test_accept_callable(settings, value, will_raise):
    # Arrange
    settings.GITHUB_SSO_ENABLED = value

    # Act / Assert
    if will_raise:
        with pytest.raises(TypeError):
            assert conf.GITHUB_SSO_ENABLED is True
    else:
        assert conf.GITHUB_SSO_ENABLED is True


def test_is_admin_path(client_with_session, settings):
    # Arrange
    from django_github_sso.helpers import is_admin_path

    settings.GITHUB_SSO_ADMIN_ENABLED = is_admin_path
    settings.GITHUB_SSO_PAGES_ENABLED = False

    # Act
    response_admin = client_with_session.get("/admin/login", follow=True)
    response_admin_text = (
        response_admin.text
        if hasattr(response_admin, "text")
        else response_admin.content.decode()
    )
    response_page = client_with_session.get("/", follow=True)
    response_page_text = (
        response_page.text
        if hasattr(response_page, "text")
        else response_page.content.decode()
    )

    # Assert
    assert "Sign in with GitHub" in response_admin_text
    assert "Sign in with GitHub" not in response_page_text


def test_is_page_path(client_with_session, settings):
    # Arrange
    from django_github_sso.helpers import is_page_path

    settings.GITHUB_SSO_ADMIN_ENABLED = False
    settings.GITHUB_SSO_PAGES_ENABLED = is_page_path

    # Act
    response_admin = client_with_session.get("/admin/login", follow=True)
    response_admin_text = (
        response_admin.text
        if hasattr(response_admin, "text")
        else response_admin.content.decode()
    )
    response_page = client_with_session.get("/", follow=True)
    response_page_text = (
        response_page.text
        if hasattr(response_page, "text")
        else response_page.content.decode()
    )

    # Assert
    assert "Sign in with GitHub" not in response_admin_text
    assert "Sign in with GitHub" in response_page_text


def test_pages_login_not_allowed(client_with_session, settings, callback_url):
    # Arrange
    settings.GITHUB_SSO_ENABLED = True
    settings.GITHUB_SSO_PAGES_ENABLED = False
    settings.GITHUB_SSO_LOGIN_FAILED_URL = "index"

    # Act
    response = client_with_session.get(callback_url)

    # Assert
    assert response.status_code == 302
    assert User.objects.count() == 0
    assert response.url == "/"
    assert response.wsgi_request.user.is_authenticated is False


def test_conf_with_callable(settings, rf, default_site, other_site):
    # Arrange
    request = rf.get("/")
    request.site = other_site

    def get_cookie_age(req):
        return 86400 if req.site.domain == "other-site.com" else 1800

    # Act
    settings.GITHUB_SSO_SESSION_COOKIE_AGE = 1234

    # Assert
    assert conf.GITHUB_SSO_SESSION_COOKIE_AGE == 1234

    # Act
    settings.GITHUB_SSO_SESSION_COOKIE_AGE = get_cookie_age

    # Assert
    assert conf.GITHUB_SSO_SESSION_COOKIE_AGE(request) == 86400

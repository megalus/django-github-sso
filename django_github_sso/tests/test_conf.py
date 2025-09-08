import importlib
from unittest.mock import MagicMock

import pytest
from django.contrib.sites.models import Site
from django.http import HttpRequest


def test_conf_from_settings(settings):
    # Arrange
    settings.GITHUB_SSO_ENABLED = False

    # Act
    from django_github_sso import conf

    importlib.reload(conf)

    # Assert
    assert conf.GITHUB_SSO_ENABLED is False


def test_conf_callable_values(settings):
    # Arrange
    mock_request = MagicMock(spec=HttpRequest)

    # Define a callable that returns a value based on the request
    def get_client_id(request):
        return "dynamic-client-id"

    settings.GITHUB_SSO_CLIENT_ID = get_client_id

    # Act
    from django_github_sso import conf

    importlib.reload(conf)

    # Assert
    # When accessed directly, it should return the callable
    assert callable(conf.GITHUB_SSO_CLIENT_ID)
    # When called with a request, it should return the dynamic value
    assert conf.GITHUB_SSO_CLIENT_ID(mock_request) == "dynamic-client-id"


@pytest.fixture
def site_objects():
    # Create two sites
    site1 = Site.objects.create(domain="site.com", name="Site 1")
    site2 = Site.objects.create(domain="other-site.com", name="Site 2")
    yield site1, site2
    # Clean up
    Site.objects.filter(domain__in=["site.com", "other-site.com"]).delete()


@pytest.mark.django_db
def test_conf_with_multiple_sites(settings, site_objects):
    # Arrange
    site1, site2 = site_objects

    # Create mock requests for each site
    mock_request1 = MagicMock(spec=HttpRequest)
    mock_request1.get_host.return_value = site1.domain

    mock_request2 = MagicMock(spec=HttpRequest)
    mock_request2.get_host.return_value = site2.domain

    # Define a callable that returns different cookie ages based on the site
    def get_cookie_age(request):
        if request.get_host() == "site.com":
            return 3600  # 1 hour for site.com
        elif request.get_host() == "other-site.com":
            return 7200  # 2 hours for other-site.com
        return 1800  # 30 minutes default

    settings.GITHUB_SSO_SESSION_COOKIE_AGE = get_cookie_age

    # Act
    from django_github_sso import conf

    importlib.reload(conf)

    # Assert
    assert callable(conf.GITHUB_SSO_SESSION_COOKIE_AGE)
    assert conf.GITHUB_SSO_SESSION_COOKIE_AGE(mock_request1) == 3600
    assert conf.GITHUB_SSO_SESSION_COOKIE_AGE(mock_request2) == 7200

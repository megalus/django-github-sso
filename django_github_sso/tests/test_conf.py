import importlib


def test_conf_from_settings(settings):
    # Arrange
    settings.GITHUB_SSO_ENABLED = False

    # Act
    from django_github_sso import conf

    importlib.reload(conf)

    # Assert
    assert conf.GITHUB_SSO_ENABLED is False

import pytest

from django_github_sso.main import UserHelper

pytestmark = pytest.mark.django_db


def test_github_sso_model(github_mock, auth_user_mock, callback_request, settings):
    # Act
    helper = UserHelper(github_mock, auth_user_mock, callback_request)
    user = helper.get_or_create_user()

    # Assert
    assert user.githubssouser.github_id == auth_user_mock.id
    assert user.githubssouser.picture_url == auth_user_mock.avatar_url
    assert user.githubssouser.user_name == auth_user_mock.login

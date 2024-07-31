import importlib
from copy import deepcopy

import pytest

from django_github_sso import conf
from django_github_sso.main import UserHelper
from django_github_sso.models import User

pytestmark = pytest.mark.django_db


def test_user_email(github_mock, auth_user_mock, callback_request):
    # Act
    helper = UserHelper(github_mock, auth_user_mock, callback_request)
    helper.email_is_valid()

    # Assert
    assert helper.user_email.email == "peter@dailybugle.info"


@pytest.mark.parametrize(
    "allowable_domains, expected_result", [(["dailyplanet.com"], False), ([], True)]
)
def test_email_is_valid(
    github_mock,
    auth_user_mock,
    callback_request,
    allowable_domains,
    expected_result,
    settings,
):
    # Arrange
    settings.GITHUB_SSO_ALLOWABLE_DOMAINS = allowable_domains
    importlib.reload(conf)

    # Act
    helper = UserHelper(github_mock, auth_user_mock, callback_request)

    # Assert
    assert helper.email_is_valid()[0] == expected_result


@pytest.mark.parametrize("auto_create_super_user", [True, False])
def test_get_or_create_user(
    auto_create_super_user, callback_request, settings, github_mock, auth_user_mock
):
    # Arrange
    settings.GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER = auto_create_super_user
    importlib.reload(conf)

    # Act
    helper = UserHelper(github_mock, auth_user_mock, callback_request)
    user = helper.get_or_create_user()

    # Assert
    assert user.first_name == helper.first_name
    assert user.last_name == helper.family_name
    assert user.username == auth_user_mock.login
    assert user.email == helper.user_email.email
    assert user.is_active is True
    assert user.is_staff == auto_create_super_user
    assert user.is_superuser == auto_create_super_user


@pytest.mark.parametrize(
    "always_update_user_data, expected_is_equal", [(True, False), (False, True)]
)
def test_update_existing_user_record_for_different_emails(
    always_update_user_data,
    callback_request,
    expected_is_equal,
    github_mock,
    auth_user_mock,
    updated_github_mocks,
    settings,
):
    # Arrange
    User.objects.all().delete()
    settings.GITHUB_SSO_ALWAYS_UPDATE_USER_DATA = always_update_user_data
    settings.GITHUB_SSO_UNIQUE_EMAIL = False
    importlib.reload(conf)
    helper = UserHelper(github_mock, auth_user_mock, callback_request)
    helper.get_or_create_user()
    user = helper.get_or_create_user()
    original_first_name = user.first_name
    original_last_name = user.last_name
    original_email = user.email

    # Act
    updated_user_helper = UserHelper(*updated_github_mocks, callback_request)
    user = updated_user_helper.get_or_create_user()

    # Assert
    assert (original_first_name == user.first_name) == expected_is_equal
    assert (original_last_name == user.last_name) == expected_is_equal
    assert (original_email == user.email) == expected_is_equal


def test_add_all_users_to_staff_list(
    faker, github_mock, auth_user_mock, email_data_mock, callback_request, settings
):
    # Arrange
    settings.GITHUB_SSO_STAFF_LIST = ["*"]
    settings.GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER = False
    settings.GITHUB_SSO_CALLBACK_DOMAIN = "localhost:8000"
    importlib.reload(conf)

    emails = [
        faker.email(),
        faker.email(),
        faker.email(),
    ]

    # Act
    for email in emails:
        mock = deepcopy(github_mock)
        a_mock = deepcopy(auth_user_mock)
        e_mock = deepcopy(email_data_mock)
        e_mock.email = email
        a_mock.get_emails.return_value = [e_mock]
        a_mock.id = faker.random_int()
        a_mock.name = faker.name()
        a_mock.login = faker.user_name()
        mock.get_user.return_value = a_mock
        helper = UserHelper(mock, a_mock, callback_request)
        helper.get_or_create_user()
        helper.find_user()

    # Assert
    assert User.objects.filter(is_staff=True).count() == 3


def test_create_staff_from_list(
    github_mock, auth_user_mock, callback_request, settings, email_data_mock
):
    # Arrange
    settings.GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER = False
    settings.GITHUB_SSO_STAFF_LIST = [email_data_mock.email]
    settings.GITHUB_SSO_CALLBACK_DOMAIN = "localhost:8000"
    importlib.reload(conf)
    User.objects.all().delete()

    # Act
    helper = UserHelper(github_mock, auth_user_mock, callback_request)
    user = helper.get_or_create_user()

    # Assert
    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is False


def test_create_super_user_from_list(
    github_mock, auth_user_mock, callback_request, settings, email_data_mock
):
    # Arrange
    settings.GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER = False
    settings.GITHUB_SSO_SUPERUSER_LIST = [email_data_mock.email]
    settings.GITHUB_SSO_CALLBACK_DOMAIN = "localhost:8000"
    importlib.reload(conf)
    User.objects.all().delete()

    # Act
    helper = UserHelper(github_mock, auth_user_mock, callback_request)
    user = helper.get_or_create_user()

    # Assert
    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is True


def test_duplicated_emails(github_mock, auth_user_mock, callback_request):
    # Arrange
    helper = UserHelper(github_mock, auth_user_mock, callback_request)
    user = helper.get_or_create_user()
    user.email = user.email.upper()
    user.username = user.username.upper()
    user.save()

    # Act
    same_user_helper = UserHelper(github_mock, auth_user_mock, callback_request)
    same_user_helper.get_or_create_user()
    same_user = same_user_helper.find_user()

    # Assert
    assert user.id == same_user.id
    assert User.objects.count() == 1

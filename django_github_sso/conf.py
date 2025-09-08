from typing import Any, Callable

from django.conf import settings
from django.http import HttpRequest
from loguru import logger


class GitHubSSOSettings:
    """
    Settings class for Django GitHub SSO.

    This class implements properties for all settings, with some accepting
    callable values that will receive the Django request.
    """

    def _get_setting(
        self, name: str, default: Any = None, accept_callable: bool = True
    ) -> Any:
        """Get a setting from Django settings."""
        value = getattr(settings, name, default)
        if not accept_callable and callable(value):
            raise TypeError(f"The setting {name} cannot be a callable.")
        return value

    # Configurations without callable
    @property
    def GITHUB_SSO_ENABLED(self) -> bool:
        return self._get_setting("GITHUB_SSO_ENABLED", True, accept_callable=False)

    @property
    def GITHUB_SSO_ENABLE_LOGS(self) -> bool:
        return self._get_setting("GITHUB_SSO_ENABLE_LOGS", True, accept_callable=False)

    @property
    def SSO_USE_ALTERNATE_W003(self) -> bool:
        return self._get_setting("SSO_USE_ALTERNATE_W003", False, accept_callable=False)

    # Configurations with optional callable

    @property
    def GITHUB_SSO_LOGO_URL(self) -> str | Callable[[HttpRequest], str]:
        return self._get_setting(
            "GITHUB_SSO_LOGO_URL",
            "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png",
        )

    @property
    def GITHUB_SSO_TEXT(self) -> str | Callable[[HttpRequest], str]:
        return self._get_setting("GITHUB_SSO_TEXT", "Sign in with GitHub")

    # Configurations with optional callable
    @property
    def GITHUB_SSO_ADMIN_ENABLED(self) -> bool | Callable[[HttpRequest], str] | None:
        return self._get_setting("GITHUB_SSO_ADMIN_ENABLED", None)

    @property
    def GITHUB_SSO_PAGES_ENABLED(self) -> bool | Callable[[HttpRequest], str] | None:
        return self._get_setting("GITHUB_SSO_PAGES_ENABLED", None)

    @property
    def GITHUB_SSO_CLIENT_ID(self) -> str | Callable[[HttpRequest], str] | None:
        return self._get_setting("GITHUB_SSO_CLIENT_ID", None)

    @property
    def GITHUB_SSO_CLIENT_SECRET(self) -> str | Callable[[HttpRequest], str] | None:
        return self._get_setting("GITHUB_SSO_CLIENT_SECRET", None)

    @property
    def GITHUB_SSO_SCOPES(self) -> list[str] | Callable[[HttpRequest], list[str]]:
        return self._get_setting(
            "GITHUB_SSO_SCOPES", ["read:user", "user:email", "read:org"]
        )

    @property
    def GITHUB_SSO_TIMEOUT(self) -> int | Callable[[HttpRequest], int]:
        return self._get_setting("GITHUB_SSO_TIMEOUT", 10)

    @property
    def GITHUB_SSO_ALLOWABLE_DOMAINS(
        self,
    ) -> list[str] | Callable[[HttpRequest], list[str]]:
        return self._get_setting("GITHUB_SSO_ALLOWABLE_DOMAINS", [])

    @property
    def GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER(
        self,
    ) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER", False)

    @property
    def GITHUB_SSO_SESSION_COOKIE_AGE(self) -> int | Callable[[HttpRequest], int]:
        return self._get_setting("GITHUB_SSO_SESSION_COOKIE_AGE", 3600)

    @property
    def GITHUB_SSO_SUPERUSER_LIST(
        self,
    ) -> list[str] | Callable[[HttpRequest], list[str]]:
        return self._get_setting("GITHUB_SSO_SUPERUSER_LIST", [])

    @property
    def GITHUB_SSO_STAFF_LIST(self) -> list[str] | Callable[[HttpRequest], list[str]]:
        return self._get_setting("GITHUB_SSO_STAFF_LIST", [])

    @property
    def GITHUB_SSO_CALLBACK_DOMAIN(self) -> str | Callable[[HttpRequest], str] | None:
        return self._get_setting("GITHUB_SSO_CALLBACK_DOMAIN", None)

    @property
    def GITHUB_SSO_AUTO_CREATE_USERS(self) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_AUTO_CREATE_USERS", True)

    @property
    def GITHUB_SSO_AUTHENTICATION_BACKEND(
        self,
    ) -> str | Callable[[HttpRequest], str] | None:
        return self._get_setting("GITHUB_SSO_AUTHENTICATION_BACKEND", None)

    @property
    def GITHUB_SSO_PRE_VALIDATE_CALLBACK(self) -> str | Callable[[HttpRequest], str]:
        return self._get_setting(
            "GITHUB_SSO_PRE_VALIDATE_CALLBACK",
            "django_github_sso.hooks.pre_validate_user",
        )

    @property
    def GITHUB_SSO_PRE_CREATE_CALLBACK(self) -> str | Callable[[HttpRequest], str]:
        return self._get_setting(
            "GITHUB_SSO_PRE_CREATE_CALLBACK",
            "django_github_sso.hooks.pre_create_user",
        )

    @property
    def GITHUB_SSO_PRE_LOGIN_CALLBACK(self) -> str | Callable[[HttpRequest], str]:
        return self._get_setting(
            "GITHUB_SSO_PRE_LOGIN_CALLBACK",
            "django_github_sso.hooks.pre_login_user",
        )

    @property
    def GITHUB_SSO_NEXT_URL(self) -> str | Callable[[HttpRequest], str]:
        return self._get_setting("GITHUB_SSO_NEXT_URL", "admin:index")

    @property
    def GITHUB_SSO_LOGIN_FAILED_URL(self) -> str | Callable[[HttpRequest], str]:
        return self._get_setting("GITHUB_SSO_LOGIN_FAILED_URL", "admin:index")

    @property
    def GITHUB_SSO_SAVE_ACCESS_TOKEN(self) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_SAVE_ACCESS_TOKEN", False)

    @property
    def GITHUB_SSO_ALWAYS_UPDATE_USER_DATA(
        self,
    ) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_ALWAYS_UPDATE_USER_DATA", False)

    @property
    def GITHUB_SSO_LOGOUT_REDIRECT_PATH(self) -> str | Callable[[HttpRequest], str]:
        return self._get_setting("GITHUB_SSO_LOGOUT_REDIRECT_PATH", "admin:index")

    @property
    def GITHUB_SSO_TOKEN_TIMEOUT(self) -> int | Callable[[HttpRequest], int]:
        return self._get_setting("GITHUB_SSO_TOKEN_TIMEOUT", 10)

    @property
    def GITHUB_SSO_ALLOWABLE_ORGS(
        self,
    ) -> list[str] | Callable[[HttpRequest], list[str]]:
        return self._get_setting("GITHUB_SSO_ALLOWABLE_ORGS", [])

    @property
    def GITHUB_SSO_NEEDED_REPOS(self) -> list[str] | Callable[[HttpRequest], list[str]]:
        return self._get_setting("GITHUB_SSO_NEEDED_REPOS", [])

    @property
    def GITHUB_SSO_UNIQUE_EMAIL(self) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_UNIQUE_EMAIL", False)

    @property
    def GITHUB_SSO_ALLOW_ALL_USERS(self) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_ALLOW_ALL_USERS", False)

    @property
    def GITHUB_SSO_CHECK_ONLY_PRIMARY_EMAIL(
        self,
    ) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_CHECK_ONLY_PRIMARY_EMAIL", True)

    @property
    def GITHUB_SSO_ACCEPT_OUTSIDE_COLLABORATORS(
        self,
    ) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_ACCEPT_OUTSIDE_COLLABORATORS", False)

    @property
    def GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES(
        self,
    ) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES", False)

    @property
    def GITHUB_SSO_SAVE_BASIC_GITHUB_INFO(self) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_SAVE_BASIC_GITHUB_INFO", True)

    @property
    def GITHUB_SSO_SHOW_FAILED_LOGIN_MESSAGE(
        self,
    ) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_SHOW_FAILED_LOGIN_MESSAGE", False)

    @property
    def GITHUB_SSO_ENABLE_MESSAGES(self) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("GITHUB_SSO_ENABLE_MESSAGES", True)

    @property
    def SSO_ADMIN_ROUTE(
        self,
    ) -> str | Callable[[HttpRequest], str]:
        return self._get_setting("SSO_ADMIN_ROUTE", "admin:index")

    @property
    def SSO_SHOW_FORM_ON_ADMIN_PAGE(
        self,
    ) -> bool | Callable[[HttpRequest], bool]:
        return self._get_setting("SSO_SHOW_FORM_ON_ADMIN_PAGE", True)


# Create a single instance of the settings class
_gh_sso_settings = GitHubSSOSettings()


def __getattr__(name: str) -> Any:
    """
    Implement PEP 562 __getattr__ to lazily load settings.

    This function is called when an attribute is not found in the module's
    global namespace. It delegates to the _gh_sso_settings instance.
    """
    return getattr(_gh_sso_settings, name)


if _gh_sso_settings.SSO_USE_ALTERNATE_W003:
    from django_github_sso.checks.warnings import register_sso_check  # noqa

if _gh_sso_settings.GITHUB_SSO_ENABLE_LOGS:
    logger.enable("django_github_sso")
else:
    logger.disable("django_github_sso")

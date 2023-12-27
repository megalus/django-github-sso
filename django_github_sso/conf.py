from django.conf import settings

GITHUB_SSO_CLIENT_ID = getattr(settings, "GITHUB_SSO_CLIENT_ID", None)
GITHUB_SSO_CLIENT_SECRET = getattr(settings, "GITHUB_SSO_CLIENT_SECRET", None)
GITHUB_SSO_SCOPES = getattr(
    settings, "GITHUB_SSO_SCOPES", ["read:user", "user:email", "read:org"]
)
GITHUB_SSO_TIMEOUT = getattr(settings, "GITHUB_SSO_TIMEOUT", 10)

GITHUB_SSO_ALLOWABLE_DOMAINS = getattr(settings, "GITHUB_SSO_ALLOWABLE_DOMAINS", [])
GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER = getattr(
    settings, "GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER", False
)
GITHUB_SSO_SESSION_COOKIE_AGE = getattr(settings, "GITHUB_SSO_SESSION_COOKIE_AGE", 3600)
GITHUB_SSO_ENABLED = getattr(settings, "GITHUB_SSO_ENABLED", True)
GITHUB_SSO_SUPERUSER_LIST = getattr(settings, "GITHUB_SSO_SUPERUSER_LIST", [])
GITHUB_SSO_STAFF_LIST = getattr(settings, "GITHUB_SSO_STAFF_LIST", [])
GITHUB_SSO_CALLBACK_DOMAIN = getattr(settings, "GITHUB_SSO_CALLBACK_DOMAIN", None)
GITHUB_SSO_AUTO_CREATE_USERS = getattr(settings, "GITHUB_SSO_AUTO_CREATE_USERS", True)

GITHUB_SSO_AUTHENTICATION_BACKEND = getattr(
    settings, "GITHUB_SSO_AUTHENTICATION_BACKEND", None
)

GITHUB_SSO_PRE_LOGIN_CALLBACK = getattr(
    settings,
    "GITHUB_SSO_PRE_LOGIN_CALLBACK",
    "django_github_sso.hooks.pre_login_user",
)

GITHUB_SSO_LOGO_URL = getattr(
    settings,
    "GITHUB_SSO_LOGO_URL",
    "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png",
)

GITHUB_SSO_TEXT = getattr(settings, "GITHUB_SSO_TEXT", "Sign in with GitHub")
GITHUB_SSO_NEXT_URL = getattr(settings, "GITHUB_SSO_NEXT_URL", "admin:index")
GITHUB_SSO_LOGIN_FAILED_URL = getattr(
    settings, "GITHUB_SSO_LOGIN_FAILED_URL", "admin:index"
)
GITHUB_SSO_SAVE_ACCESS_TOKEN = getattr(settings, "GITHUB_SSO_SAVE_ACCESS_TOKEN", False)
GITHUB_SSO_ALWAYS_UPDATE_USER_DATA = getattr(
    settings, "GITHUB_SSO_ALWAYS_UPDATE_USER_DATA", False
)
GITHUB_SSO_LOGOUT_REDIRECT_PATH = getattr(
    settings, "GITHUB_SSO_LOGOUT_REDIRECT_PATH", "admin:index"
)
SSO_USE_ALTERNATE_W003 = getattr(settings, "SSO_USE_ALTERNATE_W003", False)

if SSO_USE_ALTERNATE_W003:
    from django_github_sso.checks.warnings import register_sso_check  # noqa

GITHUB_SSO_TOKEN_TIMEOUT = getattr(settings, "GITHUB_SSO_TOKEN_TIMEOUT", 10)

GITHUB_SSO_ALLOWABLE_ORGS = getattr(settings, "GITHUB_SSO_ALLOWABLE_ORGS", [])

GITHUB_SSO_NEEDED_REPOS = getattr(settings, "GITHUB_SSO_NEEDED_REPOS", [])

GITHUB_SSO_UNIQUE_EMAIL = getattr(settings, "GITHUB_SSO_UNIQUE_EMAIL", False)

GITHUB_SSO_ALLOW_ALL_USERS = getattr(settings, "GITHUB_SSO_ALLOW_ALL_USERS", False)

GITHUB_SSO_CHECK_ONLY_PRIMARY_EMAIL = getattr(
    settings, "GITHUB_SSO_CHECK_ONLY_PRIMARY_EMAIL", True
)

GITHUB_SSO_ACCEPT_OUTSIDE_COLLABORATORS = getattr(
    settings, "GITHUB_SSO_ACCEPT_OUTSIDE_COLLABORATORS", False
)

GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES = getattr(
    settings, "GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES", False
)

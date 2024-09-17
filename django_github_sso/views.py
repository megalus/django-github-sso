import importlib
from urllib.parse import urlparse

from django.contrib.auth import login
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from github import Auth, Github
from loguru import logger

from django_github_sso import conf
from django_github_sso.main import GithubAuth, UserHelper
from django_github_sso.utils import send_message


@require_http_methods(["GET"])
def start_login(request: HttpRequest) -> HttpResponseRedirect:
    # Get the next url
    next_param = request.GET.get(key="next")
    if next_param:
        clean_param = (
            next_param
            if next_param.startswith("http") or next_param.startswith("/")
            else f"//{next_param}"
        )
    else:
        clean_param = reverse(conf.GITHUB_SSO_NEXT_URL)
    next_path = urlparse(clean_param).path

    github_auth = GithubAuth(request)
    auth_url, state = github_auth.get_auth_info()

    # Save data on Session
    if not request.session.session_key:
        request.session.create()
    request.session.set_expiry(conf.GITHUB_SSO_TIMEOUT * 60)
    request.session["sso_state"] = state
    request.session["sso_next_url"] = next_path
    request.session.save()

    # Redirect User
    return HttpResponseRedirect(auth_url)


@require_http_methods(["GET"])
def callback(request: HttpRequest) -> HttpResponseRedirect:
    login_failed_url = reverse(conf.GITHUB_SSO_LOGIN_FAILED_URL)
    github = GithubAuth(request)
    code = request.GET.get("code")
    state = request.GET.get("state")

    # Check if GitHub SSO is enabled
    if not conf.GITHUB_SSO_ENABLED:
        send_message(request, _("GitHub SSO not enabled."))
        return HttpResponseRedirect(login_failed_url)

    # Check for at least one filter or allow all users
    if (
        not conf.GITHUB_SSO_ALLOWABLE_DOMAINS
        and not conf.GITHUB_SSO_ALLOWABLE_ORGS
        and not conf.GITHUB_SSO_NEEDED_REPOS
        and not conf.GITHUB_SSO_ALLOW_ALL_USERS
    ):
        send_message(
            request,
            _(
                "No filter defined for GitHub SSO allowable users. "
                "Please contact your administrator."
            ),
        )
        return HttpResponseRedirect(login_failed_url)

    # First, check for authorization code
    if not code:
        send_message(request, _("Authorization Code not received from SSO."))
        return HttpResponseRedirect(login_failed_url)

    # Then, check state.
    request_state = request.session.get("sso_state")
    next_url = request.session.get("sso_next_url")

    if not request_state or state != request_state:
        send_message(request, _("State Mismatch. Time expired?"))
        return HttpResponseRedirect(login_failed_url)

    auth_result = github.get_user_token(code, state)
    if "error" in auth_result:
        send_message(
            request,
            _(
                f"Authorization Error received from SSO: "
                f"{auth_result['error_description']}."
            ),
        )
        return HttpResponseRedirect(login_failed_url)

    access_token = auth_result["access_token"]

    # Get User Info from GitHub
    try:
        auth = Auth.Token(access_token)
        g = Github(auth=auth)
        github_user = g.get_user()
    except Exception as error:
        send_message(request, str(error))
        return HttpResponseRedirect(login_failed_url)

    user_helper = UserHelper(g, github_user, request)

    # Run Pre-Validate Callback
    module_path = ".".join(conf.GITHUB_SSO_PRE_VALIDATE_CALLBACK.split(".")[:-1])
    pre_validate_fn = conf.GITHUB_SSO_PRE_VALIDATE_CALLBACK.split(".")[-1]
    module = importlib.import_module(module_path)
    user_is_valid = getattr(module, pre_validate_fn)(github_user, request)

    # Check if User Info is valid to login
    result, message = user_helper.email_is_valid()
    if not result or not user_is_valid:
        send_message(
            request,
            _(
                f"Email address not allowed: {user_helper.user_email.email}. "
                f"Please contact your administrator."
            ),
        )
        if conf.GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES:
            send_message(request, message, level="warning")
        return HttpResponseRedirect(login_failed_url)

    result, message = user_helper.user_is_valid()
    if not result:
        send_message(
            request,
            _(
                f"GitHub User not allowed: {github_user.login}. "
                f"Please contact your administrator."
            ),
        )
        if conf.GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES:
            send_message(request, message, level="warning")
        return HttpResponseRedirect(login_failed_url)

    # Add Access Token in Session
    if conf.GITHUB_SSO_SAVE_ACCESS_TOKEN:
        request.session["github_sso_access_token"] = access_token

    # Run Pre-Create Callback
    module_path = ".".join(conf.GITHUB_SSO_PRE_CREATE_CALLBACK.split(".")[:-1])
    pre_login_fn = conf.GITHUB_SSO_PRE_CREATE_CALLBACK.split(".")[-1]
    module = importlib.import_module(module_path)
    extra_users_args = getattr(module, pre_login_fn)(github_user, request)

    # Get or Create User
    if conf.GITHUB_SSO_AUTO_CREATE_USERS:
        user = user_helper.get_or_create_user(extra_users_args)
    else:
        user = user_helper.find_user()

    if not user or not user.is_active:
        failed_login_message = (
            f"User not found - User: '{github_user.login}', "
            f"Email: '{user_helper.user_email.email}'"
        )
        if not user and not conf.GITHUB_SSO_AUTO_CREATE_USERS:
            failed_login_message += ". Auto-Create is disabled."

        if user and not user.is_active:
            failed_login_message = f"User is not active: '{github_user.login}'"

        if conf.GITHUB_SSO_SHOW_FAILED_LOGIN_MESSAGE:
            send_message(request, _(failed_login_message), level="warning")
        else:
            logger.warning(failed_login_message)

        return HttpResponseRedirect(login_failed_url)

    # Save Session
    request.session.save()

    # Run Pre-Login Callback
    module_path = ".".join(conf.GITHUB_SSO_PRE_LOGIN_CALLBACK.split(".")[:-1])
    pre_login_fn = conf.GITHUB_SSO_PRE_LOGIN_CALLBACK.split(".")[-1]
    module = importlib.import_module(module_path)
    getattr(module, pre_login_fn)(user, request)

    # Login User
    login(request, user, conf.GITHUB_SSO_AUTHENTICATION_BACKEND)
    request.session.set_expiry(conf.GITHUB_SSO_SESSION_COOKIE_AGE)

    return HttpResponseRedirect(next_url or reverse(conf.GITHUB_SSO_NEXT_URL))

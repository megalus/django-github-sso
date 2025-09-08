import importlib
from urllib.parse import urlparse

from django.contrib.auth import login
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from github import Auth, Github
from loguru import logger

from django_github_sso.main import GithubAuth, UserHelper
from django_github_sso.utils import send_message


@require_http_methods(["GET"])
def start_login(request: HttpRequest) -> HttpResponseRedirect:
    github_auth = GithubAuth(request)
    # Get the next url
    next_param = request.GET.get(key="next")
    if next_param:
        clean_param = (
            next_param
            if next_param.startswith("http") or next_param.startswith("/")
            else f"//{next_param}"
        )
    else:
        next_url = github_auth.get_sso_value("next_url")
        clean_param = reverse(next_url)
    next_path = urlparse(clean_param).path

    auth_url, state = github_auth.get_auth_info()

    # Save data on Session
    if not request.session.session_key:
        request.session.create()

    timeout = github_auth.get_sso_value("timeout")
    request.session.set_expiry(timeout * 60)

    request.session["sso_state"] = state
    request.session["sso_next_url"] = next_path
    request.session.save()

    # Redirect User
    return HttpResponseRedirect(auth_url)


@require_http_methods(["GET"])
def callback(request: HttpRequest) -> HttpResponseRedirect:
    github = GithubAuth(request)
    login_failed_url = reverse(github.get_sso_value("login_failed_url"))
    code = request.GET.get("code")
    state = request.GET.get("state")

    next_url_from_session = request.session.get("sso_next_url")
    next_url_from_conf = reverse(github.get_sso_value("next_url"))
    next_url = next_url_from_session if next_url_from_session else next_url_from_conf
    logger.debug(f"Next URL after login: {next_url}")

    # Check if GitHub SSO is enabled
    enabled, message = github.check_enabled(next_url)
    if not enabled:
        send_message(request, _("GitHub SSO not enabled."))
        return HttpResponseRedirect(login_failed_url)

    # Check for at least one filter or allow all users

    allowable_domains = github.get_sso_value("allowable_domains")
    allowable_orgs = github.get_sso_value("allowable_orgs")
    needed_repos = github.get_sso_value("needed_repos")
    allow_all_users = github.get_sso_value("allow_all_users")

    if (
        not allowable_domains
        and not allowable_orgs
        and not needed_repos
        and not allow_all_users
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
    pre_validate_callback = github.get_sso_value("pre_validate_callback")
    module_path = ".".join(pre_validate_callback.split(".")[:-1])
    pre_validate_fn = pre_validate_callback.split(".")[-1]
    module = importlib.import_module(module_path)
    user_is_valid = getattr(module, pre_validate_fn)(github_user, request)

    # Check if User Info is valid to login
    show_additional_error_messages = github.get_sso_value("show_additional_error_messages")
    result, message = user_helper.email_is_valid()
    if not result or not user_is_valid:
        send_message(
            request,
            _(
                f"Email address not allowed: {user_helper.user_email.email}. "
                f"Please contact your administrator."
            ),
        )
        if show_additional_error_messages:
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
        if show_additional_error_messages:
            send_message(request, message, level="warning")
        return HttpResponseRedirect(login_failed_url)

    # Add Access Token in Session
    save_access_token = github.get_sso_value("save_access_token")
    if save_access_token:
        request.session["github_sso_access_token"] = access_token

    # Run Pre-Create Callback
    pre_create_callback = github.get_sso_value("pre_create_callback")
    module_path = ".".join(pre_create_callback.split(".")[:-1])
    pre_login_fn = pre_create_callback.split(".")[-1]
    module = importlib.import_module(module_path)
    extra_users_args = getattr(module, pre_login_fn)(github_user, request)

    # Get or Create User
    auto_create_users = github.get_sso_value("auto_create_users")
    if auto_create_users:
        user = user_helper.get_or_create_user(extra_users_args)
    else:
        user = user_helper.find_user()

    if not user or not user.is_active:
        failed_login_message = (
            f"User not found - User: '{github_user.login}', "
            f"Email: '{user_helper.user_email.email}'"
        )
        if not user and not auto_create_users:
            failed_login_message += ". Auto-Create is disabled."

        if user and not user.is_active:
            failed_login_message = f"User is not active: '{github_user.login}'"

        show_failed_login_message = github.get_sso_value("show_failed_login_message")
        if show_failed_login_message:
            send_message(request, _(failed_login_message), level="warning")
        else:
            logger.warning(failed_login_message)

        return HttpResponseRedirect(login_failed_url)

    # Save Session
    request.session.save()

    # Run Pre-Login Callback
    pre_login_callback = github.get_sso_value("pre_login_callback")
    module_path = ".".join(pre_login_callback.split(".")[:-1])
    pre_login_fn = pre_login_callback.split(".")[-1]
    module = importlib.import_module(module_path)
    getattr(module, pre_login_fn)(user, request)

    # Get Authentication Backend
    # If exists, lets make a sanity check on it
    # Because Django does not raise errors if backend is wrong
    authentication_backend = github.get_sso_value("authentication_backend")
    if authentication_backend:
        module_path = ".".join(authentication_backend.split(".")[:-1])
        backend_auth_class = authentication_backend.split(".")[-1]
        try:
            module = importlib.import_module(module_path)
            getattr(module, backend_auth_class)
        except (ImportError, AttributeError) as error:
            raise ImportError(
                f"Authentication Backend invalid: {authentication_backend}"
            ) from error

    # Login User
    session_cookie_age = github.get_sso_value("session_cookie_age")
    login(request, user, authentication_backend)
    request.session.set_expiry(session_cookie_age)

    return HttpResponseRedirect(next_url)

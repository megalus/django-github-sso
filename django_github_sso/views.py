import importlib
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from github import Auth, Github

from django_github_sso import conf
from django_github_sso.main import GithubAuth, UserHelper


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
        messages.add_message(request, messages.ERROR, _("GitHub SSO not enabled."))
        return HttpResponseRedirect(login_failed_url)

    # Check for at least one filter or allow all users
    if (
        not conf.GITHUB_SSO_ALLOWABLE_DOMAINS
        and not conf.GITHUB_SSO_ALLOWABLE_ORGS
        and not conf.GITHUB_SSO_NEEDED_REPOS
        and not conf.GITHUB_SSO_ALLOW_ALL_USERS
    ):
        messages.add_message(
            request,
            messages.ERROR,
            _(
                "No filter defined for GitHub SSO allowable users. "
                "Please contact your administrator."
            ),
        )
        return HttpResponseRedirect(login_failed_url)

    # First, check for authorization code
    if not code:
        messages.add_message(
            request, messages.ERROR, _("Authorization Code not received from SSO.")
        )
        return HttpResponseRedirect(login_failed_url)

    # Then, check state.
    request_state = request.session.get("sso_state")
    next_url = request.session.get("sso_next_url")

    if not request_state or state != request_state:
        messages.add_message(
            request, messages.ERROR, _("State Mismatch. Time expired?")
        )
        return HttpResponseRedirect(login_failed_url)

    auth_result = github.get_user_token(code, state)
    if "error" in auth_result:
        messages.add_message(
            request,
            messages.ERROR,
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
        messages.add_message(request, messages.ERROR, str(error))
        return HttpResponseRedirect(login_failed_url)

    user_helper = UserHelper(g, github_user, request)

    # Check if User Info is valid to login
    result, message = user_helper.email_is_valid()
    if not result:
        messages.add_message(
            request,
            messages.ERROR,
            _(
                f"Email address not allowed: {user_helper.user_email.email}. "
                f"Please contact your administrator."
            ),
        )
        if conf.GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES:
            messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(login_failed_url)

    result, message = user_helper.user_is_valid()
    if not result:
        messages.add_message(
            request,
            messages.ERROR,
            _(
                f"GitHub User not allowed: {github_user.login}. "
                f"Please contact your administrator."
            ),
        )
        if conf.GITHUB_SSO_SHOW_ADDITIONAL_ERROR_MESSAGES:
            messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(login_failed_url)

    # Get or Create User
    if conf.GITHUB_SSO_AUTO_CREATE_USERS:
        user = user_helper.get_or_create_user()
    else:
        user = user_helper.find_user()

    if not user or not user.is_active:
        return HttpResponseRedirect(login_failed_url)

    # Add Access Token in Session
    if conf.GITHUB_SSO_SAVE_ACCESS_TOKEN:
        request.session["github_sso_access_token"] = access_token

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

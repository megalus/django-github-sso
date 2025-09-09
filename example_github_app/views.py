import httpx
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LogoutView
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseRedirect,
)
from django.shortcuts import render, resolve_url
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_microsoft_sso.main import MicrosoftAuth
from loguru import logger


def debug_login_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """

    def user_is_required(user):
        can_login = user.is_authenticated and user.is_active
        logger.debug(
            f"User is: {user}, Active: {user.is_active}, "
            f"Authenticated: {user.is_authenticated}"
        )
        logger.debug(f"User is Authenticated: {can_login}")
        return can_login

    actual_decorator = user_passes_test(
        user_is_required,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


@debug_login_required
def secret_page(request) -> HttpResponse:
    logout_url = reverse("logout")
    return render(
        request,
        "secret_page.html",
        {"logout_url": logout_url},
    )


@require_http_methods(["POST", "OPTIONS"])
def microsoft_slo_view(request: HttpRequest) -> HttpResponseBase:
    """
    Logout the User from Microsoft SSO and Django.

    Use this View for your logout URL.

    """
    # Logout from Microsoft
    try:
        auth = MicrosoftAuth(request)
        slo_enabled = auth.get_sso_value("SLO_ENABLED")
        sso_enabled = auth.get_sso_value("ENABLED")

        if slo_enabled and sso_enabled:
            microsoft = MicrosoftAuth(request)
            logout_redirect_path = auth.get_sso_value("LOGOUT_REDIRECT_PATH")
            homepage = resolve_url(logout_redirect_path)
            if not homepage.startswith("http"):
                homepage = request.build_absolute_uri(homepage)
            next_page = microsoft.get_logout_url(homepage=homepage)
            return LogoutView.as_view(next_page=next_page)(request)
    except Exception as e:
        logger.error(f"Error during Microsoft SLO process: {e}")

    redirect_url = (
        reverse("admin:index")
        if request.path.startswith(reverse("admin:index"))
        else reverse("index")
    )

    # Logout from Google (in case you're using both packages)
    token = request.session.get("google_sso_access_token")
    if token:
        httpx.post(
            "https://oauth2.googleapis.com/revoke", params={"token": token}, timeout=10
        )

    return LogoutView.as_view(next_page=redirect_url)(request)


def index(request) -> HttpResponse:
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("secret"))
    return render(request, "login.html", {})

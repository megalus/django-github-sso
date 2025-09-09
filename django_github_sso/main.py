from dataclasses import dataclass
from typing import Any, List, Type

import httpx
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Field, Q
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from github import AuthenticatedUser, Github, Organization, Repository
from github.AuthenticatedUser import EmailData
from loguru import logger
from requests_oauthlib import OAuth2Session

from django_github_sso import conf
from django_github_sso.models import GitHubSSOUser


@dataclass
class GithubAuth:
    request: HttpRequest

    def get_sso_value(self, key: str) -> Any:
        """
        Get SSO value from configuration, handling callable values.

        If the configuration value is a callable, it will be called with the request.
        Otherwise, the value will be returned as is.

        def get_client_id(request):
            client_ids = {
                "example.com": "your-client-id",
                "other.com": "your-other-client-id",
            }
            return client_ids.get(request.site.domain, None)

        GITHUB_SSO_CLIENT_ID = get_client_id

        Args:
            key: The configuration key without the GITHUB_SSO_ prefix

        Returns:
            The configuration value

        Raises:
            ValueError: If the configuration key is not found
        """
        github_sso_conf = f"GITHUB_SSO_{key.upper()}"
        if hasattr(conf, github_sso_conf):
            value = getattr(conf, github_sso_conf)
            if callable(value):
                logger.debug(
                    f"Value from conf {github_sso_conf} is a callable. Calling it."
                )
                return value(self.request)
            return value
        raise ValueError(f"SSO Configuration '{github_sso_conf}' not found in settings.")

    @property
    def scopes(self) -> list[str]:
        return self.get_sso_value("scopes")

    def get_netloc(self):
        callback_domain = self.get_sso_value("callback_domain")
        if callback_domain:
            logger.debug("Find Netloc using GITHUB_SSO_CALLBACK_DOMAIN")
            return callback_domain

        site = get_current_site(self.request)
        logger.debug("Find Netloc using Site domain")
        return site.domain

    def get_redirect_uri(self) -> str:
        if "HTTP_X_FORWARDED_PROTO" in self.request.META:
            scheme = self.request.META["HTTP_X_FORWARDED_PROTO"]
        else:
            scheme = self.request.scheme
        netloc = self.get_netloc()
        path = reverse("django_github_sso:oauth_callback")
        callback_uri = f"{scheme}://{netloc}{path}"
        logger.debug(f"Callback URI: {callback_uri}")
        return callback_uri

    def get_auth_info(self) -> tuple[str, str]:
        github = OAuth2Session(
            self.get_sso_value("client_id"),
            redirect_uri=self.get_redirect_uri(),
            scope=self.scopes,
        )
        authorization_url, state = github.authorization_url(
            "https://github.com/login/oauth/authorize"
        )

        return authorization_url, state

    def get_user_token(self, code, state):
        data = {
            "client_id": self.get_sso_value("client_id"),
            "client_secret": self.get_sso_value("client_secret"),
            "code": code,
            "redirect_uri": self.get_redirect_uri(),
            "state": state,
        }
        headers = {"Accept": "application/json"}
        response = httpx.post(
            "https://github.com/login/oauth/access_token",
            data=data,
            headers=headers,
            timeout=self.get_sso_value("token_timeout"),
        )
        return response.json()

    def check_enabled(self, next_url: str) -> tuple[bool, str]:
        response = True, ""
        if not conf.GITHUB_SSO_ENABLED:
            response = False, "GitHub SSO not enabled."
        else:
            admin_route = conf.SSO_ADMIN_ROUTE
            if callable(admin_route):
                admin_route = admin_route(self.request)

            admin_enabled = self.get_sso_value("admin_enabled")
            if admin_enabled is False and next_url.startswith(reverse(admin_route)):
                response = False, "GitHub SSO not enabled for Admin."

            pages_enabled = self.get_sso_value("pages_enabled")
            if pages_enabled is False and not next_url.startswith(reverse(admin_route)):
                response = False, "GitHub SSO not enabled for Pages."

        if response[1]:
            logger.debug(f"SSO Enable Check failed: {response[1]}")

        return response


@dataclass
class UserHelper:
    github: Github
    user: AuthenticatedUser
    request: Any
    user_email: EmailData | None = None
    user_changed: bool = False

    @property
    def first_name(self) -> str:
        return self.get_user_name().split(" ")[0]

    @property
    def family_name(self) -> str:
        return " ".join(self.get_user_name().split(" ")[1:])

    def get_user_emails(self) -> List[EmailData]:
        return self.user.get_emails()

    def get_user_orgs(self) -> List[Organization]:
        return self.user.get_orgs()

    def get_user_repos(self) -> List[Repository]:
        return self.user.get_repos()

    def get_user_name(self) -> str:
        return self.user.name or ""

    def get_user_id(self) -> int:
        return self.user.id

    def get_user_avatar_url(self) -> str:
        return self.user.avatar_url

    def get_user_login(self) -> str:
        return self.user.login

    def get_user_email(self) -> str:
        return self.user_email.email

    @property
    def user_model(self) -> Type[User]:
        return get_user_model()

    @property
    def email_field_name(self) -> str:
        return self.user_model.get_email_field_name()

    @property
    def username_field(self) -> Field:
        return self.user_model._meta.get_field(self.user_model.USERNAME_FIELD)

    def email_is_valid(self) -> tuple[bool, str]:
        auth = GithubAuth(self.request)
        message = ""
        user_email_info = self.get_user_emails()
        user_emails = [data for data in user_email_info if data.primary is True]
        if user_emails:
            self.user_email = user_emails[0]
        else:
            message = "No primary email found."
            logger.warning(message)
            return False, message

        allowable_domains = auth.get_sso_value("allowable_domains")
        valid_domain = not allowable_domains or allowable_domains == ["*"]
        for email_domain in allowable_domains:
            check_only_primary_email = auth.get_sso_value("check_only_primary_email")
            if check_only_primary_email:
                if email_domain in self.user_email.email:
                    valid_domain = True
                    break
            else:
                for email in user_email_info:
                    if email.email in email_domain and email.verified:
                        valid_domain = True
                        self.user_email = email
                        break

        if not valid_domain:
            message = (
                f"No email found in allowable domains "
                f"(Primary Email: {self.user_email.email})."
            )
            logger.warning(message)
            return False, message

        if not self.user_email.verified:
            message = f"Email {self.user_email.email} is not verified."
            logger.warning(message)

        return True, message

    def user_is_valid(self) -> tuple[bool, str]:
        auth = GithubAuth(self.request)
        message = ""
        org_found = None
        user_orgs = self.get_user_orgs()
        allowable_orgs = auth.get_sso_value("allowable_orgs")
        valid_org = not allowable_orgs
        accept_outside_collaborators = auth.get_sso_value("accept_outside_collaborators")
        for allowable_org in allowable_orgs:
            for user_org in user_orgs:
                if allowable_org.lower() == user_org.name.lower():
                    org_found = user_org.name
                    if not accept_outside_collaborators:
                        org_members = user_org.get_members()
                        for org_member in org_members:
                            if org_member.login == self.user.login:
                                valid_org = True
                                break
                    else:
                        valid_org = True
                        break

        if not valid_org:
            message = (
                f"User {self.user.login} is not member "
                f"in {org_found if org_found else 'any allowable orgs'}."
            )
            logger.warning(message)
            return False, message

        needed_repos = auth.get_sso_value("needed_repos")
        valid_repo = not needed_repos
        if not valid_repo:
            user_repos = self.get_user_repos()
            found_repos = []
            for allowable_repo in needed_repos:
                for user_repo in user_repos:
                    if allowable_repo == user_repo.full_name:
                        found_repos.append(user_repo.name)
            if len(found_repos) == len(needed_repos):
                valid_repo = True

        if not valid_repo:
            message = (
                f"User {self.user.login} does not have access to needed "
                f"Repository. Tip: use repository full name (org/name)"
            )
            logger.warning(message)
            return False, message

        return True, message

    def get_or_create_user(self, extra_users_args: dict | None = None):
        auth = GithubAuth(self.request)
        self.email_is_valid()
        user_defaults = extra_users_args or {}

        unique_email = auth.get_sso_value("unique_email")
        if unique_email:
            if self.username_field.name not in user_defaults:
                user_defaults[self.username_field.name] = self.get_user_email()
            user, created = self.user_model.objects.get_or_create(
                **{
                    f"{self.email_field_name}__iexact": self.get_user_email(),
                    "defaults": user_defaults,
                },
            )
        else:
            query = self.user_model.objects.filter(
                githubssouser__user_name__iexact=self.get_user_login()
            )
            if query.exists():
                user = query.get()
                created = False
            else:
                username = user_defaults.pop(
                    self.username_field.name, self.get_user_login()
                )
                create_query = {
                    f"{self.username_field.attname}__iexact": username,
                    "defaults": user_defaults,
                }
                if self.username_field.attname not in user_defaults:
                    user_defaults[self.username_field.attname] = username
                user, created = self.user_model.objects.get_or_create(**create_query)
        self.check_first_super_user(user)
        self.check_for_update(created, user)
        if self.user_changed:
            user.save()

        save_basic_info = auth.get_sso_value("save_basic_github_info")
        if save_basic_info:
            GitHubSSOUser.objects.update_or_create(
                user=user,
                defaults={
                    "github_id": self.get_user_id(),
                    "picture_url": self.get_user_avatar_url(),
                    "user_name": self.get_user_login(),
                },
            )

        return user

    def check_for_update(self, created, user):
        auth = GithubAuth(self.request)
        always_update_user_data = auth.get_sso_value("always_update_user_data")
        if created or always_update_user_data:
            user.first_name = self.first_name
            user.last_name = self.family_name
            setattr(user, self.username_field.name, self.get_user_login())
            setattr(user, self.email_field_name, self.get_user_email())
            user.set_unusable_password()
            self.check_for_permissions(user)
            self.user_changed = True

    def check_first_super_user(self, user):
        auth = GithubAuth(self.request)
        auto_create_first_superuser = auth.get_sso_value("auto_create_first_superuser")
        if auto_create_first_superuser:
            superuser_exists = self.user_model.objects.filter(is_superuser=True).exists()
            if not superuser_exists:
                message_text = _(
                    f"GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER is True. "
                    f"Adding SuperUser status to: {self.get_user_name()}"
                )
                messages.add_message(self.request, messages.INFO, message_text)
                logger.warning(message_text)
                user.is_superuser = True
                user.is_staff = True
                self.user_changed = True

    def check_for_permissions(self, user):
        user_email = getattr(user, self.email_field_name)
        auth = GithubAuth(self.request)
        staff_list = auth.get_sso_value("staff_list")
        if (
            user_email in staff_list
            or self.get_user_login() in staff_list
            or "*" in staff_list
        ):
            message_text = _(
                f"User @{self.get_user_login()} ({user_email}) "
                f"in GITHUB_SSO_STAFF_LIST. "
                f"Added Staff Permission."
            )
            messages.add_message(self.request, messages.INFO, message_text)
            logger.debug(message_text)
            user.is_staff = True
        superuser_list = auth.get_sso_value("superuser_list")
        if user_email in superuser_list or self.get_user_login() in superuser_list:
            message_text = _(
                f"User @{self.get_user_login()} ({user_email}) in "
                f"GITHUB_SSO_SUPERUSER_LIST. "
                f"Added SuperUser Permission."
            )
            messages.add_message(self.request, messages.INFO, message_text)
            logger.debug(message_text)
            user.is_superuser = True
            user.is_staff = True

    def find_user(self):
        auth = GithubAuth(self.request)
        user_model = get_user_model()
        unique_email = auth.get_sso_value("unique_email")
        if unique_email:
            query = user_model.objects.filter(
                **{f"{self.email_field_name}__iexact": self.get_user_email()}
            )
        else:
            username_query = {
                f"{self.username_field.attname}__iexact": self.get_user_login()
            }
            query = user_model.objects.filter(
                Q(githubssouser__user_name__iexact=self.get_user_login())
                | Q(**username_query)
            )

        return query.get() if query.exists() else None

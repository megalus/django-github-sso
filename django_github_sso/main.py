from dataclasses import dataclass
from typing import Any

import httpx
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Field, Model, Q
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

    @property
    def scopes(self) -> list[str]:
        return conf.GITHUB_SSO_SCOPES

    def get_netloc(self):
        if conf.GITHUB_SSO_CALLBACK_DOMAIN:
            logger.debug("Find Netloc using GITHUB_SSO_CALLBACK_DOMAIN")
            return conf.GITHUB_SSO_CALLBACK_DOMAIN

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
            conf.GITHUB_SSO_CLIENT_ID,
            redirect_uri=self.get_redirect_uri(),
            scope=self.scopes,
        )
        authorization_url, state = github.authorization_url(
            "https://github.com/login/oauth/authorize"
        )

        return authorization_url, state

    def get_user_token(self, code, state):
        data = {
            "client_id": conf.GITHUB_SSO_CLIENT_ID,
            "client_secret": conf.GITHUB_SSO_CLIENT_SECRET,
            "code": code,
            "redirect_uri": self.get_redirect_uri(),
            "state": state,
        }
        headers = {"Accept": "application/json"}
        response = httpx.post(
            "https://github.com/login/oauth/access_token",
            data=data,
            headers=headers,
            timeout=conf.GITHUB_SSO_TOKEN_TIMEOUT,
        )
        return response.json()


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

    def get_user_emails(self) -> list[EmailData]:
        return self.user.get_emails()

    def get_user_orgs(self) -> list[Organization]:
        return self.user.get_orgs()

    def get_user_repos(self) -> list[Repository]:
        return self.user.get_repos()

    def get_user_name(self) -> str:
        return self.user.name

    def get_user_id(self) -> int:
        return self.user.id

    def get_user_avatar_url(self) -> str:
        return self.user.avatar_url

    def get_user_login(self) -> str:
        return self.user.login

    def get_user_email(self) -> str:
        return self.user_email.email

    @property
    def user_model(self) -> AbstractUser | Model:
        return get_user_model()

    @property
    def username_field(self) -> Field:
        return self.user_model._meta.get_field(self.user_model.USERNAME_FIELD)

    def email_is_valid(self) -> tuple[bool, str]:
        message = ""
        user_email_info = self.get_user_emails()
        user_emails = [data for data in user_email_info if data.primary is True]
        if user_emails:
            self.user_email = user_emails[0]
        else:
            message = "No primary email found."
            logger.warning(message)
            return False, message

        valid_domain = not conf.GITHUB_SSO_ALLOWABLE_DOMAINS
        for email_domain in conf.GITHUB_SSO_ALLOWABLE_DOMAINS:
            if conf.GITHUB_SSO_CHECK_ONLY_PRIMARY_EMAIL:
                if self.user_email.email in email_domain:
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

        if self.user_email.verified is False:
            message = f"Email {self.user_email.email} is not verified."
            logger.warning(message)

        return True, message

    def user_is_valid(self) -> tuple[bool, str]:
        message = ""
        org_found = None
        user_orgs = self.get_user_orgs()
        valid_org = not conf.GITHUB_SSO_ALLOWABLE_ORGS
        for allowable_org in conf.GITHUB_SSO_ALLOWABLE_ORGS:
            for user_org in user_orgs:
                if allowable_org.lower() == user_org.name.lower():
                    org_found = user_org.name
                    if not conf.GITHUB_SSO_ACCEPT_OUTSIDE_COLLABORATORS:
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

        valid_repo = not conf.GITHUB_SSO_NEEDED_REPOS
        if not valid_repo:
            user_repos = self.get_user_repos()
            found_repos = []
            for allowable_repo in conf.GITHUB_SSO_NEEDED_REPOS:
                for user_repo in user_repos:
                    if allowable_repo == user_repo.full_name:
                        found_repos.append(user_repo.name)
            if len(found_repos) == len(conf.GITHUB_SSO_NEEDED_REPOS):
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
        self.email_is_valid()
        user_defaults = extra_users_args or {}

        if conf.GITHUB_SSO_UNIQUE_EMAIL:
            if self.username_field.name not in user_defaults:
                user_defaults[self.username_field.name] = self.get_user_email()
            user, created = self.user_model.objects.get_or_create(
                email__iexact=self.get_user_email(),
                defaults=user_defaults,
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

        if conf.GITHUB_SSO_SAVE_BASIC_GITHUB_INFO:
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
        if created or conf.GITHUB_SSO_ALWAYS_UPDATE_USER_DATA:
            user.first_name = self.first_name
            user.last_name = self.family_name
            setattr(user, self.username_field.name, self.get_user_login())
            user.email = self.get_user_email()
            user.set_unusable_password()
            self.check_for_permissions(user)
            self.user_changed = True

    def check_first_super_user(self, user):
        if conf.GITHUB_SSO_AUTO_CREATE_FIRST_SUPERUSER:
            superuser_exists = self.user_model.objects.filter(
                is_superuser=True
            ).exists()
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
        if (
            user.email in conf.GITHUB_SSO_STAFF_LIST
            or self.get_user_login() in conf.GITHUB_SSO_STAFF_LIST
            or "*" in conf.GITHUB_SSO_STAFF_LIST
        ):
            message_text = _(
                f"User @{self.get_user_login()} ({user.email} "
                f"in GITHUB_SSO_STAFF_LIST. "
                f"Added Staff Permission."
            )
            messages.add_message(self.request, messages.INFO, message_text)
            logger.debug(message_text)
            user.is_staff = True
        if (
            user.email in conf.GITHUB_SSO_SUPERUSER_LIST
            or self.get_user_login() in conf.GITHUB_SSO_SUPERUSER_LIST
        ):
            message_text = _(
                f"User @{self.get_user_login()} ({user.email}) in "
                f"GITHUB_SSO_SUPERUSER_LIST. "
                f"Added SuperUser Permission."
            )
            messages.add_message(self.request, messages.INFO, message_text)
            logger.debug(message_text)
            user.is_superuser = True
            user.is_staff = True

    def find_user(self):
        user_model = get_user_model()
        if conf.GITHUB_SSO_UNIQUE_EMAIL:
            query = user_model.objects.filter(email__iexact=self.get_user_email())
        else:
            username_query = {
                f"{self.username_field.attname}__iexact": self.get_user_login()
            }
            query = user_model.objects.filter(
                Q(githubssouser__user_name__iexact=self.get_user_login())
                | Q(**username_query)
            )
        if query.exists():
            return query.get()

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoGithubSsoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_github_sso"
    verbose_name = _("Github SSO User")

    def ready(self):
        import django_github_sso.templatetags  # noqa

from django.contrib import messages
from loguru import logger

try:
    from django_microsoft_sso import conf
except ImportError:
    conf = None


def send_message(request, message, level: str = "error"):
    getattr(logger, level.lower())(message)
    if conf and conf.MICROSOFT_SSO_ENABLE_MESSAGES:
        messages.add_message(request, getattr(messages, level.upper()), message)


def show_credential(credential):
    return f"{credential[:5]}...{credential[-5:]}"

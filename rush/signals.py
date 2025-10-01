from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

from rush.logger import get_logger

logger = get_logger()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"User '{user.username}' logged in from IP {get_client_ip(request)}.")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"User '{user.username}' logged out from IP {get_client_ip(request)}.")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    logger.warning(
        f"Failed login attempt with username '{credentials.get('username')}' from IP {get_client_ip(request)}."
    )


def get_client_ip(request):
    """Helper to extract IP address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

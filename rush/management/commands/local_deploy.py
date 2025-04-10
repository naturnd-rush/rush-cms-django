from django.conf import settings
from django.core.management.base import BaseCommand

from rush.views.deploy import _deploy, _get_deploy_file_logger


class Command(BaseCommand):
    help = "Attempt to deploy the admin site locally (for testing purposes.)"

    def handle(self, *args, **options):
        logger = _get_deploy_file_logger(settings.DEPLOY_LOGS_DIR, "deploy_")
        _deploy(logger)

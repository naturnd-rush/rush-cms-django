import json

from django.core.management.base import BaseCommand

from rush.models import DeployLog, DeployStatus
from rush.views.deploy import DeployRunner


class Command(BaseCommand):
    help = "Attempt to deploy the admin site locally (for testing purposes.)"

    def handle(self, *args, **options):
        runner = DeployRunner(needs_auth=False)
        runner.run()

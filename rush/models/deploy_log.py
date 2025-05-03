import os
import uuid

from django.conf import settings
from django.db import models


class DeployStatus(models.TextChoices):
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class DeployLog(models.Model):
    """
    A file that records the logs from a deploy.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    status = models.CharField(max_length=255, choices=DeployStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def _display_created_at(self) -> str:
        """
        Human-readable datetime representing when this deploy log was created.
        """
        return self.created_at.strftime("%Y-%m-%dT%H:%M:%S")

    def filepath(self) -> str:
        """
        The time-stamped filepath where the deploy log exists on disk.
        """
        dt = self._display_created_at()
        os.makedirs(settings.DEPLOY_LOGS_DIR, exist_ok=True)
        filename = f"deploy-{dt}.log"
        return os.path.join(settings.DEPLOY_LOGS_DIR, filename)

    def __str__(self):
        dt = self._display_created_at()
        if DeployStatus.IN_PROGRESS == self.status:
            return f"<Deploy started at {dt} is IN_PROGRESS>"
        return f"Deploy {self.status.upper()} at {dt}."

    def get_log_contents(self) -> str:
        try:
            with open(self.filepath(), "r") as f:
                return f.read()
        except FileNotFoundError:
            return "Log file not found."
        except Exception as e:
            return f"Error reading log file: {str(e)}"

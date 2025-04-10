import os
import uuid

from django.conf import settings
from django.db import models


class DeployLog(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    filename = models.CharField(max_length=255)

    def __str__(self):
        return f"Deploy Log - {self.filename}"

    def get_file_path(self):
        # For getting the actual path of the deploy log file on the server
        return os.path.join(settings.DEPLOY_LOGS_DIR, self.filename)

    def get_log_contents(self):
        try:
            with open(self.get_file_path(), "r") as f:
                return f.read()
        except FileNotFoundError:
            return "Log file not found."
        except Exception as e:
            return f"Error reading log file: {str(e)}"

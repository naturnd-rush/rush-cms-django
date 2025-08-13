import uuid

from django.db import models


class LayerGroup(models.Model):
    """
    The title of a group of layers in the legend.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    group_name = models.CharField(max_length=255)
    group_description = models.TextField(blank=True, help_text="Optional description.")

    def __str__(self):
        return self.group_name

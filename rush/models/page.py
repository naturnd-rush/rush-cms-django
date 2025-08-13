import uuid

from django.db import models


class Page(models.Model):
    """
    A static webpage on the website.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255, help_text="The title of the webpage.")
    content = models.TextField(help_text="The content that will appear on the webpage.")

    def __str__(self):
        return f"{self.title} - Page"

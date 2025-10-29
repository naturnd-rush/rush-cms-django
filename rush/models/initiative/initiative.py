import uuid

from django.core.validators import URLValidator
from django.db import models


class Initiative(models.Model):
    """
    A project, group, or resource relevant to answering one or more questions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    link = models.CharField(max_length=2048, validators=[URLValidator()])
    image = models.ImageField(upload_to="initiative_images/", null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField(to="InitiativeTag", related_name="initiatives")

    def __str__(self):
        return self.title

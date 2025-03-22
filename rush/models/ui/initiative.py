import uuid

from django.db import models


class Initiative(models.Model):
    """
    A project, group, or resource relevant to answering one or more questions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    image = models.ImageField(upload_to="initiative_images/", null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField(to="InitiativeTag", related_name="initiatives")

    def __str__(self):
        return self.title


class InitiativeTag(models.Model):
    """
    A descriptive word or phrase that represents a category of initiatives.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

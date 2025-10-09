import uuid
from django.utils.text import slugify

from django.db import models
from simple_history.models import HistoricalRecords


class Question(models.Model):
    """
    A question that ties together one or more map layers into a data-driven narrative.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(upload_to="question_images/", null=True, blank=True)
    initiatives = models.ManyToManyField(to="Initiative", blank=True)
    questions = models.ManyToManyField(to="Layer", related_name="questions")
    # Allow NULL in the DB for the initial migration state; blank=True keeps the
    # admin form optional. Slugs are generated on save when missing.
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/questions/{self.slug}/"

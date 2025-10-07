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
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # Ensure unique slug by adding numbers if duplicate exists
            while Question.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/questions/{self.slug}/"

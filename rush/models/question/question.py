import uuid

from django.db import models

from rush.models.question import DuplicateSlug


class Question(models.Model):
    """
    A question that ties together one or more map layers into a data-driven narrative.
    """

    class Meta:
        ordering = ["display_order"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(upload_to="question_images/", null=True, blank=True)
    initiatives = models.ManyToManyField(to="Initiative", blank=True)
    questions = models.ManyToManyField(to="Layer", related_name="questions")
    slug = models.SlugField(max_length=255, unique=True)
    display_order = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True, editable=True)

    def __str__(self):
        return self.title

import uuid

from django.core.exceptions import ValidationError
from django.db import models


class Question(models.Model):
    """
    A question that ties together one or more map layers into a data-driven narrative.
    """

    class Meta:
        ordering = ["display_order"]

    class DuplicateSlug(ValidationError):
        """
        The slug on this instance is duplicated by another Question in the database.
        """

        ...

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(upload_to="question_images/", null=True, blank=True)
    initiatives = models.ManyToManyField(to="Initiative", blank=True)
    questions = models.ManyToManyField(to="Layer", related_name="questions")
    slug = models.SlugField(max_length=255, unique=True)
    display_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def clean_slug(self):
        if same_slug_q := Question.objects.exclude(pk=self.id).filter(slug=self.slug).first():
            raise self.DuplicateSlug(
                'Question with id "{}" has the same slug as this question "{}"!'.format(
                    same_slug_q.id,
                    self.id,
                )
            )

    def __str__(self):
        return self.title

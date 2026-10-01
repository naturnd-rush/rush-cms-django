import uuid

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from rush.models.question import Question
from rush.models.utils import SummernoteTextCleaner


class QuestionTab(models.Model):
    """
    A subtab of the question where content can go.
    """

    class Meta:
        ordering = ["display_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["question", "slug"],
                name="unique_slug_per_question",
            ),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    icon = models.ForeignKey(to="Icon", on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=255)
    content = models.TextField()
    content_strict_clean = models.BooleanField(default=True)
    question = models.ForeignKey(
        # Delete all QuestionTabs when a Question is deleted.
        to=Question,
        on_delete=models.CASCADE,
        related_name="tabs",
    )
    slug = models.SlugField(max_length=255)
    display_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, db_index=True, editable=True
    )

    # the zoom level to adjust to when a question tab is selected
    zoom = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(23),
        ],
        help_text="automatically zooms the map when a question tab is clicked. defaults to None,"
        + " which means that the map will stay at its current zoom level.",
    )
    # the lat and long to center the map on when a question tab is selected.
    center_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    center_long = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    def clean(self) -> None:
        self.content = SummernoteTextCleaner.clean(
            self.content, strict_clean=self.content_strict_clean
        )

    def __str__(self):
        return f"{self.title} for question: '{self.question.title}'"

import uuid

import django.db.models as models
from simple_history.models import HistoricalRecords


class Question(models.Model):
    """
    A question with potentially nested sub-questions that together describe a human's
    relationship with some specific layer on a map.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    image = models.ImageField(upload_to="question_images/", null=True, blank=True)
    content = models.TextField()
    initiatives = models.ManyToManyField(to="Initiative")
    history = HistoricalRecords()
    layer = models.ForeignKey(
        to="Layer",
        # Prevent a Layer from being deleted if a Question relies on it
        on_delete=models.PROTECT,
    )
    sub_question = models.ForeignKey(
        to="SubQuestion",
        null=True,
        blank=True,
        # If a SubQuestion is deleted, nothing happens to this Question
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return self.title


class SubQuestionDiplay(models.TextChoices):
    """
    The way in which a sub-question should be displayed, as interpreted by front-end code.
    """

    FULL_WINDOW = "full_window"
    CARD = "card"


class SubQuestion(models.Model):
    """
    A nested section of information about the parent question, which shall be displayed
    after a button with the specified "button_text" is clicked.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    content = models.TextField()

    button_text = models.CharField(max_length=255)
    display = models.CharField(max_length=255, choices=SubQuestionDiplay.choices)

    sub_question = models.ForeignKey(
        to="self",
        null=True,
        blank=True,
        # If a SubQuestion is deleted, nothing happens to this SubQuestion
        on_delete=models.DO_NOTHING,
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.title} - {self.subtitle}"

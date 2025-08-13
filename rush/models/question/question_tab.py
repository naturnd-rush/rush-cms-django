import uuid

from django.db import models
from simple_history.models import HistoricalRecords

from rush.models.question.question import Question


class QuestionTab(models.Model):
    """
    A subtab of the question where content can go.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    question = models.ForeignKey(
        null=True,
        # Delete all QuestionTabs when a Question is deleted.
        to=Question,
        on_delete=models.CASCADE,
        related_name="tabs",
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.title} for question: '{self.question.title}'"

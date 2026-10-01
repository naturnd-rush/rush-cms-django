import uuid

from django.db import models


class LayerOnQuestionTab(models.Model):
    """
    Through table for the layers that get toggled on when a QuestionTab is selected.
    The layers don't need to be on the tab's Question.
    """

    class Meta:
        verbose_name = "Layer on question tab"
        constraints = [
            models.UniqueConstraint(
                fields=["question_tab", "layer"],
                name="unique_layer_per_question_tab",
            ),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    question_tab = models.ForeignKey("QuestionTab", on_delete=models.CASCADE)
    layer = models.ForeignKey("Layer", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.layer} on {self.question_tab}"

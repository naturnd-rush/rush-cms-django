import uuid

from django.db import models


class LayerGroupOnQuestion(models.Model):
    """
    A group of layers applied to a single question. For example, a question about
    the environmental health might have a "Forests" group, with layers describing
    forest health, flora composition, soil data, etc.
    """

    class Meta:
        ordering = ["display_order"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    group_name = models.CharField(max_length=255)
    group_description = models.CharField(
        max_length=1024,
        blank=True,
        help_text="An optional description for the group.",
    )
    question = models.ForeignKey(to="Question", on_delete=models.CASCADE)
    display_order = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True, editable=True)

    def __str__(self):
        return self.group_name

import uuid

from django.db import models
from django.db.models import Max


class LayerGroupOnQuestion(models.Model):
    """
    A group of layers applied to a single question. For example, a question about
    the environmental health might have a "Forests" group, with layers describing
    forest health, flora composition, soil data, etc.
    """

    class Meta:
        ordering = ["display_order"]

    class Behaviour(models.TextChoices):
        """
        Hidden (in the form) group behaviour that lets superusers specify
        """

        DEFAULT = "default"
        ALL_LAYERS = "all_layers"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    group_name = models.CharField(max_length=255)
    group_description = models.CharField(
        max_length=1024,
        blank=True,
        help_text="An optional description for the group.",
    )
    question = models.ForeignKey(to="Question", on_delete=models.CASCADE, related_name="layer_groups")
    display_order = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True, editable=True)

    behaviour = models.CharField(max_length=255, default=Behaviour.DEFAULT, choices=Behaviour.choices)

    def max_display_order(self) -> int:
        """
        The maximum `display_order` currently being used by related layers in this group.
        """
        max_order = self.layers.aggregate(Max("display_order"))["display_order__max"]  # type: ignore
        if not max_order:
            return 0
        return max_order

    def __str__(self):
        return self.group_name

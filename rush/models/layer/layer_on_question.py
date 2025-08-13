import uuid

from django.db import models

from rush.models.layer.layer_group import LayerGroup


class LayerOnQuestion(models.Model):
    """
    Connect each question card to multiple Layers.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    layer = models.ForeignKey(to="Layer", on_delete=models.CASCADE)
    question = models.ForeignKey(to="Question", on_delete=models.CASCADE)

    active_by_default = models.BooleanField(
        default=False,
        help_text="Whether the layer is active by default when a new question is loaded.",
    )
    layer_group = models.ForeignKey(
        to=LayerGroup,
        on_delete=models.CASCADE,
        help_text="The title of the layer group.",
    )

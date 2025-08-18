import uuid

from django.db import models


class StylesOnLayer(models.Model):
    """
    Through table for adding multiple Styles on a single Layer with the ability to
    reuse styles on other Layers.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)

    style = models.ForeignKey("Style", on_delete=models.CASCADE)
    layer = models.ForeignKey("Layer", on_delete=models.CASCADE)

    # Some expression that will be matched against a GeoJSON feature's properties
    # to decide whether this style will be applied to any given feature on the map.
    # The default is True, which means this style will be applied to all Features by default!
    feature_mapping = models.TextField(default="true")

    # Optional HTML text field for describing what the popup template will be used
    popup = models.TextField(null=True, blank=True)

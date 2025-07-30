import uuid

import django.db.models as models
from simple_history.models import HistoricalRecords


class Layer(models.Model):
    """
    MapData + Styling + Legend information combo.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255)
    description = models.TextField(
        help_text="The layer description that will appear in the map legend to help people understand what the layer data represents."
    )
    map_data = models.ForeignKey(
        to="MapData",
        # MapData deletion should fail if a Layer references it.
        on_delete=models.PROTECT,
    )
    styles = models.ManyToManyField("Style", through="StylesOnLayer")
    serialized_leaflet_json = models.JSONField(default=dict)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

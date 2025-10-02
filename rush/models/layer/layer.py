import uuid
from typing import Any, Dict

import django.db.models as models
from simple_history.models import HistoricalRecords

from rush.logger import get_logger
from rush.models.base import BaseModel

logger = get_logger()


class Layer(BaseModel):
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

    def log_changes_dict(self) -> Dict[str, Any]:
        data = super().log_changes_dict() | {
            "styles": [style.log_changes_dict() for style in self.styles.all()],
            "map_data": str(self.map_data),
        }
        data.pop("serialized_leaflet_json")  # Too big to include in logs...
        logger.debug(f"Serialization data: {data}")
        return data

import uuid

import django.db.models as models
from simple_history.models import HistoricalRecords


class Provider(models.TextChoices):
    GEOJSON = "geojson"
    OPEN_GREEN_MAP = "open_green_map"  # TODO: Implement me!
    # ESRI_FEATURE_SERVER = "esri_feature_server"  # TODO: Not sure how this gets implemented with the current MapData model
    # GENERIC_REST = "generic_rest"  # TODO: Not sure how this gets implemented with the current MapData model


class MapData(models.Model):

    # TODO: Add on_create validation
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255, unique=True)
    provider = models.CharField(max_length=255, choices=Provider.choices)
    geojson = models.JSONField(null=True, blank=True)

    # Open Green Map metadata
    ogm_map_id = models.CharField(max_length=1024, null=True, blank=True)
    feature_url_template = models.CharField(max_length=1024, null=True, blank=True)
    icon_url_template = models.CharField(max_length=1024, null=True, blank=True)
    image_url_template = models.CharField(max_length=1024, null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        # better plural name in the admin table list
        verbose_name_plural = "Map Data"

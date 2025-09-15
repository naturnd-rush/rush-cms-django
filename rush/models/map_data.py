import uuid
from typing import List

import django.db.models as models
from simple_history.models import HistoricalRecords


class Provider(models.TextChoices):
    GEOJSON = "geojson"
    OPEN_GREEN_MAP = "open_green_map"
    # ESRI_FEATURE_SERVER = "esri_feature_server"  # TODO: Not sure how this gets implemented with the current MapData model
    # GENERIC_REST = "generic_rest"  # TODO: Not sure how this gets implemented with the current MapData model


class OpenGreenMapProvider(models.Model):
    """
    The map data is provided by Open Green Maps, see their API schema: https://docs.giscollective.com/en/Rest-api/.

    NOTE: I'm storing URLs/links with a maximum length of 2000 characers following this stack-overflow post:
    https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers:
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    map_link = models.CharField(max_length=2000)
    campagn_link = models.CharField(max_length=2000, null=True, blank=True)


class MapData(models.Model):

    # TODO: Add on_create validation
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255, unique=True)

    provider = models.CharField(max_length=255, choices=Provider.choices)
    geojson = models.JSONField(null=True, blank=True)
    ogm_provider = models.ForeignKey(to=OpenGreenMapProvider, null=True, blank=True, on_delete=models.CASCADE)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        # better plural name in the admin table list
        verbose_name_plural = "Map Data"

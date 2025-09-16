import uuid

import django.db.models as models
from simple_history.models import HistoricalRecords


class Provider(models.TextChoices):
    GEOJSON = "geojson"
    OPEN_GREEN_MAP = "open_green_map"
    # ESRI_FEATURE_SERVER = "esri_feature_server"  # TODO: Not sure how this gets implemented with the current MapData model
    # GENERIC_REST = "generic_rest"  # TODO: Not sure how this gets implemented with the current MapData model

    def find_or_create(self, map_data: "MapData") -> "Provider":
        """
        Find the `Provider` on a given `MapData` instance. Or, if none is found, create
        a new one on the `MapData` instance and return it.
        """
        ...

    def switch(self, map_data: "MapData", new_provider: "Provider") -> None:
        """
        Switch the given `MapData` instance to a new `Provider` type, e.g., GEOJSON --> OPEN_GREEN_MAP.
        This function does nothing if `new_provider` is the same as the current `MapData.provider`.
        WARNING: This function will delete any data relevant to the old provider.
        """
        ...

    def _delete(self, map_data: "MapData") -> bool:
        """
        Delete the `Provider`'s data off of the given `MapData` instance, if it exists,
        and return `True` if any data was deleted, or `False` otherwise.
        """
        ...


class OpenGreenMapProvider(models.Model):
    """
    The map data is provided by Open Green Maps, see their API schema: https://docs.giscollective.com/en/Rest-api/.

    NOTE: I'm storing URLs/links with a maximum length of 2000 characers following this stack-overflow post:
    https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers:
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    map_link = models.CharField(max_length=2000)
    campaign_link = models.CharField(max_length=2000, null=True, blank=True)


class GeoJsonProvider(models.Model):
    """
    The map data is provided by the user copy-pasting raw GEOJson data into the RUSH admin site.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    geojson = models.JSONField(default=dict, null=False)


class MapData(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255, unique=True)

    provider = models.CharField(max_length=255, choices=Provider.choices)
    # geojson = models.JSONField(null=True, blank=True, default="")
    geojson_provider = models.ForeignKey(to=GeoJsonProvider, null=True, blank=True, on_delete=models.CASCADE)
    ogm_provider = models.ForeignKey(to=OpenGreenMapProvider, null=True, blank=True, on_delete=models.CASCADE)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        # better plural name in the admin table list
        verbose_name_plural = "Map Data"

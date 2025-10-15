import json
import uuid

import django.db.models as models
from django.conf import settings
from simple_history.models import HistoricalRecords
from storages.backends.s3 import S3Storage

from rush.models.validators import validate_tiff

backblaze_raster_storage = S3Storage(
    bucket_name=settings.BACKBLAZE_RASTER_BUCKET_NAME,
    endpoint_url=settings.BACKBLAZE_ENDPOINT_URL,
    access_key=settings.BACKBLAZE_APP_KEY_ID,
    secret_key=settings.BACKBLAZE_APP_KEY,
    region_name=settings.BACKBLAZE_REGION_NAME,
    default_acl="public-read",
)


class MapData(models.Model):

    class ProviderState(models.TextChoices):
        UNSET = "unset"
        GEOJSON = "geojson"
        GEOTIFF = "geotiff"  # for raster image data
        OPEN_GREEN_MAP = "open_green_map"

    class NoGeoJsonData(Exception):
        """
        There is no GeoJSON data available for this MapData object right now.
        """

        ...

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255, unique=True)
    provider_state = models.CharField(max_length=255, choices=ProviderState.choices, default=ProviderState.UNSET)

    # Geojson provider fields
    _geojson = models.JSONField(default=dict, null=True, blank=True)

    # Open green map provider fields
    map_link = models.CharField(max_length=2000, null=True, blank=True)
    campaign_link = models.CharField(max_length=2000, null=True, blank=True)

    # Geotiff provider fields
    geotiff = models.FileField(
        null=True,
        blank=True,
        storage=backblaze_raster_storage,
        validators=[validate_tiff],
        help_text="A GeoTIFF file to upload. It may take up to a couple minutes to upload depending on the file size.",
    )

    history = HistoricalRecords()

    def has_geojson_data(self) -> bool:
        try:
            self.get_raw_geojson_data()
            return True
        except self.NoGeoJsonData:
            return False

    def get_raw_geojson_data(self) -> str:
        """
        Get the raw GeoJSON data from this MapData object, or raise `NoGeoJsonData` if none exists.
        """
        if self.provider_state == self.ProviderState.GEOJSON and self._geojson:
            return json.dumps(self._geojson)
        # NOTE: Other ProviderState's may be supported in the future.
        raise self.NoGeoJsonData

    def __str__(self):
        # Don't change me. Breaks graphql API getMapDataByName for clients.
        return f"{self.name} ({self.provider_state.upper()})"

    def __repr__(self):
        return "<MapData '{}', provided by: {}, {}>".format(
            self.name,
            self.provider_state,
            self.id,
        )

    class Meta:
        # better plural name in the admin table list
        verbose_name_plural = "Map Data"

import json
import sys
import uuid
from typing import Iterable

import django.db.models as models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import URLValidator
from silk.profiling.dynamic import silk_profile
from storages.backends.s3 import S3Storage

from rush.models import MimeType
from rush.models.validators import FiletypeValidator
from rush.storage import BackblazeStorageFactory


def get_raster_storage() -> S3Storage | FileSystemStorage:
    """
    Get storage for raster image files (GeoTIFF).
    """
    if settings.DEBUG or "pytest" in sys.modules:
        # Don't try to connect to Backblaze in a dev environment or during tests
        return FileSystemStorage(location=f"{settings.MEDIA_ROOT}/debug_raster_image_storage")
    return BackblazeStorageFactory.create_from_bucket_name(
        settings.BACKBLAZE_RASTER_BUCKET_NAME,
        validate_visibility=BackblazeStorageFactory.Visibility.PUBLIC,
        persistance=BackblazeStorageFactory.Persistance.HARD_DELETE,
        duplication=BackblazeStorageFactory.Duplication.LATEST_VERSION_ONLY,
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
    map_link = models.CharField(
        max_length=2000,
        null=True,
        blank=True,
        validators=[URLValidator(schemes=["https"])],
    )
    campaign_link = models.CharField(
        max_length=2000,
        null=True,
        blank=True,
        validators=[URLValidator(schemes=["https"])],
    )

    # Geotiff provider fields
    geotiff = models.FileField(
        null=True,
        blank=True,
        storage=get_raster_storage,
        validators=[FiletypeValidator(valid_names=["TIFF"])],
        help_text="A GeoTIFF file to upload. It may take up to a couple minutes to upload depending on the file size.",
    )

    def has_geojson_data(self) -> bool:
        try:
            self.get_raw_geojson_data()
            return True
        except self.NoGeoJsonData:
            return False

    @silk_profile("MapData save")
    def save(
        self,
        force_insert=False,
        force_update=False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            update_fields=update_fields,
            using=using,
        )

    @silk_profile("MapData get_raw_geojson_data")
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

import uuid

from django.core.validators import URLValidator
from django.db import models


class BasemapSource(models.Model):
    """
    The source location of a "basemap," which is a tile-set used to style maps.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    tile_url = models.CharField(max_length=2000, null=False, validators=[URLValidator(schemes=["https"])])
    max_zoom = models.PositiveIntegerField()
    attribution = models.TextField()

    def __str__(self):
        return self.tile_url

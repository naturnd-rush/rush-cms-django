import uuid

from django.db import models


class Region(models.Model):
    """
    Geographical region for grouping and filtering questions.
    """

    class Meta:
        ordering = ["name"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Region name (e.g., 'Downtown', 'West Side', 'Coastal Area')"
    )
    latitude = models.FloatField(
        help_text="Latitude coordinate for default map center"
    )
    longitude = models.FloatField(
        help_text="Longitude coordinate for default map center"
    )
    default_zoom = models.FloatField(
        default=12.0,
        help_text="Default zoom level for map view (e.g., 12.0 for city level)"
    )

    def __str__(self):
        return self.name

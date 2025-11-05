from django.db import models
from django.core.validators import URLValidator
import uuid


class BasemapSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    tile_url = models.CharField(max_length=2000,null=False,validators=[URLValidator(schemes=["https"])])
    max_zoom = models.PositiveIntegerField()
    attribution = models.TextField()


    def __str__(self):
        return self.tile_url

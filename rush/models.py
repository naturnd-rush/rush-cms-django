from django.db import models


class BasemapSource(models.Model):
    tile_url = models.CharField(max_length=512)
    max_zoom = models.PositiveIntegerField()
    attribution = models.TextField()

    def __str__(self):
        return self.tile_url

import uuid
from typing import Any, Dict, List

import django.db.models as models
from simple_history.models import HistoricalRecords


class MapData(models.Model):

    class ProviderState(models.TextChoices):
        UNSET = "unset"
        GEOJSON = "geojson"
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
            return self._geojson
        # NOTE: Other ProviderState's may be supported in the future.
        raise self.NoGeoJsonData

    # @classmethod
    # def get_formfield_map(cls) -> Dict[ProviderState, List[Dict[str, Any]]]:
    #     """
    #     The formfields to show in the edit/change form depending on the `ProviderState`.
    #     """
    #     return {
    #         cls.ProviderState.UNSET: [],
    #         cls.ProviderState.GEOJSON: [
    #             {
    #                 "name": "_geojson",
    #                 "required": True,
    #             },
    #         ],
    #         cls.ProviderState.OPEN_GREEN_MAP: [
    #             {
    #                 "name": "map_link",
    #                 "required": True,
    #             },
    #             {
    #                 "name": "campaign_link",
    #                 "required": False,
    #             },
    #         ],
    #     }

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<MapData '{}', provided by: {}, {}>".format(
            self.name,
            self.provider_state,
            self.id,
        )

    class Meta:
        # better plural name in the admin table list
        verbose_name_plural = "Map Data"

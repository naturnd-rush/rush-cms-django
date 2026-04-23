from json import dumps, loads
from logging import getLogger
from uuid import uuid4

from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import CASCADE, ForeignKey, Model, UUIDField
from django.db.transaction import atomic

from rush.models.map_data import MapData

logger = getLogger(__name__)


class Geometry(Model):
    """
    Postgis geometry object for storing map data geometries.
    """

    id = UUIDField(primary_key=True, default=uuid4, null=False)
    map_data = ForeignKey(to="MapData", on_delete=CASCADE)
    data = GeometryField(srid=4326)



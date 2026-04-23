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


class MapDataGeometryGenerator:
    """
    A map-data wrapper object that generates postgis geometries for it in the database. The
    database transaction is atomic, so it will never generate partial geometries for a map-data.
    """

    class GenerationFailed(Exception):
        """
        Base class for when the geometry generation failed for a map-data.
        """

        ...

    class MissingGeojson(GenerationFailed):
        """
        Cannot transform the given map-data into postgis geometry because it has no geojson.
        """

        def __init__(self, map_data_id: str):
            super().__init__(f"Missing geojson in map data: {map_data_id}.")

    class MalformedGeojsonData(GenerationFailed):
        """
        The geojson data is malformed / corrupted and could not be loaded for geometry generation.
        """

        def __init__(self, map_data_id: str, errors: dict):
            super().__init__(f"Malformed / corrupted geojson in map data: {map_data_id}.", {"errors": errors})

    class NoGeometry(GenerationFailed):
        """
        The map-data has geojson but it doesn't contain any *supported* geometries.
        """

        def __init__(self, map_data_id: str):
            super().__init__(f"The geojson in map-data '{map_data_id}' contains no supported geometries.")

    class UnsupportedGeometryType(GenerationFailed):
        """
        Cannot transform the given map data into postgis geometries because it contains an
        unsupported geometry type.
        """

        def __init__(self, geometry_type: str):
            super().__init__(f"Geometry type '{geometry_type}' is not supported.")

    def __init__(self, map_data: MapData):
        self._map_data = map_data

    @classmethod
    def _extract_raw_geometries(cls, geojson: dict | None, map_data_id: str) -> list[dict]:

        # Get the geometry type of this geojson. Returning empty lists here
        # is safe because recursive calls will just extend nothing.
        if geojson is None:
            return []
        geom_type = geojson.get("type")
        if geom_type is None:
            return []

        # recurse inside feature collections
        if "FeatureCollection" == geom_type:
            if "features" not in geojson:
                raise cls.MalformedGeojsonData(
                    map_data_id,
                    {
                        "geometry": "FeatureCollection",
                        "reason": "Missing 'features' key.",
                        "data": dumps(geojson),
                    },
                )
            result = []
            for feature in geojson["features"]:
                result.extend(cls._extract_raw_geometries(feature, map_data_id))
            return result

        # recurse inside geometry collections
        if geojson.get("type") == "GeometryCollection":
            if "geometries" not in geojson:
                raise cls.MalformedGeojsonData(
                    map_data_id,
                    {
                        "geometry": "GeometryCollection",
                        "reason": "Missing 'geometries' key.",
                        "data": dumps(geojson),
                    },
                )
            result = []
            for geometry in geojson["geometries"]:
                result.extend(cls._extract_raw_geometries(geometry, map_data_id))
            return result

        if geojson.get("type") == "Feature":
            # presumably ths feature contains one geometry object
            if "geometry" not in geojson:
                raise cls.MalformedGeojsonData(
                    map_data_id,
                    {
                        "geometry": "Feature",
                        "reason": "Missing 'geometry' key.",
                        "data": dumps(geojson),
                    },
                )
            return cls._extract_raw_geometries(geojson["geometry"], map_data_id)

        # base case: return a geometry
        return [geojson]

    def run(self) -> None:

        if self._map_data.geojson is None:
            # make sure the geojson data exists
            raise self.MissingGeojson(str(self._map_data.id))

        try:
            # load the geojson data into a python dict
            geojson_data = loads(self._map_data.geojson)
        except Exception as e:
            raise self.MalformedGeojsonData(str(self._map_data.id), {"json_loads": str(e)}) from e

        raw_geometries = self._extract_raw_geometries(geojson_data, str(self._map_data.id))
        if len(raw_geometries) == 0:
            # raise if no geometries were extracted
            raise self.NoGeometry(str(self._map_data.id))

        # iterate through the raw geometries and save them to the database
        with atomic():
            for raw_geometry in raw_geometries:
                raw_geometry_string = dumps(raw_geometry)
                try:
                    geometry_data = GEOSGeometry(raw_geometry_string, srid=4326)
                except Exception as e:
                    raise self.MalformedGeojsonData(
                        str(self._map_data.id),
                        {
                            "geometry": "raw geometry object",
                            "reason": str(e),
                            "data": dumps(raw_geometry_string),
                        },
                    )
                print(geometry_data)
                Geometry.objects.create(map_data=self._map_data, data=geometry_data)

        SUPPORTED_TYPES = {
            "Point",
            "MultiPoint",
            "LineString",
            "MultiLineString",
            "Polygon",
            "MultiPolygon",
        }

from json import loads

from django.db.models import CharField
from django.db.models.functions import Cast
from pytest import mark, raises

from rush.models.geometry import Geometry, MapDataGeometryGenerator
from rush.tests.models.helpers import create_test_map_data


@mark.django_db
@mark.parametrize(
    "geojson, expected_geometries",
    [
        # Raw geometry is returned as a list
        (
            {"type": "Point", "coordinates": [400.1, 20.0]},
            [{"type": "Point", "coordinates": [400.1, 20.0]}],
        ),
        # Feature unrwaps to geometry
        (
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1.0, 2.0]}, "properties": {}},
            [{"type": "Point", "coordinates": [1.0, 2.0]}],
        ),
        # Feature geometry that is none returns an empty list
        (
            {"type": "Feature", "geometry": None, "properties": {}},
            [],
        ),
        # Feature-collection returns a flat list of geometries
        (
            {
                "type": "FeatureCollection",
                "features": [
                    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1.0, 2.0]}, "properties": {}},
                    {
                        "type": "Feature",
                        "geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
                        "properties": {},
                    },
                ],
            },
            [
                {"type": "Point", "coordinates": [1.0, 2.0]},
                {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
            ],
        ),
        # Nested feature-collections also return a flat geometry list
        (
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "geometry": {"type": "Point", "coordinates": [1.0, 2.0]},
                                "properties": {},
                            },
                        ],
                    },
                    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [3.0, 4.0]}, "properties": {}},
                ],
            },
            [
                {"type": "Point", "coordinates": [1.0, 2.0]},
                {"type": "Point", "coordinates": [3.0, 4.0]},
            ],
        ),
        # Geometry-collection returns a flat list of geometries
        (
            {
                "type": "GeometryCollection",
                "geometries": [
                    {"type": "Point", "coordinates": [1.0, 2.0]},
                    {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
                ],
            },
            [
                {"type": "Point", "coordinates": [1.0, 2.0]},
                {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
            ],
        ),
        # Nested geometry-collections also return a flat geometry list
        (
            {
                "type": "GeometryCollection",
                "geometries": [
                    {
                        "type": "GeometryCollection",
                        "geometries": [
                            {"type": "Point", "coordinates": [1.0, 2.0]},
                        ],
                    },
                    {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
                ],
            },
            [
                {"type": "Point", "coordinates": [1.0, 2.0]},
                {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
            ],
        ),
        # Nested geometry-collection inside a feature-collection still returns a flat list of geometries
        # But... who would even do such a thing!
        (
            {
                "type": "FeatureCollection",
                "features": [
                    {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "GeometryCollection",
                            "geometries": [
                                {"type": "Point", "coordinates": [1.0, 2.0]},
                                {"type": "Point", "coordinates": [3.0, 4.0]},
                            ],
                        },
                        "properties": {},
                    },
                ],
            },
            [
                {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
                {"type": "Point", "coordinates": [1.0, 2.0]},
                {"type": "Point", "coordinates": [3.0, 4.0]},
            ],
        ),
    ],
)
def test_map_data_geometry_generator_extract_raw_geometries(geojson, expected_geometries):
    """
    Extracting raw-geometry objects into a flat list for saving to postgis.
    """
    map_data = create_test_map_data(geojson=geojson)
    generator = MapDataGeometryGenerator(map_data)
    assert map_data.geojson is not None
    geoms = generator._extract_raw_geometries(
        geojson=loads(map_data.geojson),
        map_data_id=str(map_data.id),
    )
    assert geoms == expected_geometries


@mark.django_db
@mark.parametrize(
    "geojson, exception_cls, exception_regex",
    [
        (
            None,
            MapDataGeometryGenerator.MissingGeojson,
            "Missing geojson in map data",
        ),
        (
            {"type": "FeatureCollection", "features_aint_here": {}, "properties": {}},
            MapDataGeometryGenerator.MalformedGeojsonData,
            "Missing 'features' key.",
        ),
        (
            {"type": "GeometryCollection", "geometries_aint_here": {}, "properties": {}},
            MapDataGeometryGenerator.MalformedGeojsonData,
            "Missing 'geometries' key.",
        ),
        (
            {"type": "Feature", "geometry_isnt_here": {}, "properties": {}},
            MapDataGeometryGenerator.MalformedGeojsonData,
            "Missing 'geometry' key.",
        ),
        (
            {"type": "Feature", "geometry": None, "properties": {}},
            MapDataGeometryGenerator.NoGeometry,
            "contains no supported geometries",
        ),
        (
            {"type": "Feature", "geometry": {}, "properties": {}},
            MapDataGeometryGenerator.NoGeometry,
            "contains no supported geometries",
        ),
        (
            {"type": "Feature", "geometry": {"Special-Point-Type": [100, 112.4]}, "properties": {}},
            MapDataGeometryGenerator.NoGeometry,
            "contains no supported geometries",
        ),
    ],
)
def test_map_data_geometry_generator_run_raises(geojson, exception_cls, exception_regex):
    """
    Geometry generation should fail if geojson is none, contains malformed geojson data, or contains no geometries.
    """
    map_data = create_test_map_data(geojson=geojson)
    assert Geometry.objects.all().count() == 0
    with raises(expected_exception=exception_cls, match=exception_regex):
        generator = MapDataGeometryGenerator(map_data)
        generator.run()


@mark.django_db
def test_map_data_geometry_generator_run():
    """
    Geometry generation should create valid corresponding postgis geometry objects in the database.
    """
    data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
            {
                "type": "Feature",
                "geometry": {
                    "type": "GeometryCollection",
                    "geometries": [
                        {"type": "Point", "coordinates": [3.0, 4.0]},
                    ],
                },
                "properties": {},
            },
        ],
    }
    map_data = create_test_map_data(geojson=data)
    assert Geometry.objects.all().count() == 0
    generator = MapDataGeometryGenerator(map_data)
    generator.run()
    assert Geometry.objects.filter(map_data=map_data).count() == 2
    geoms = list(Geometry.objects.filter(map_data=map_data))

    # point data is correct
    points = [x for x in geoms if x.data.geom_type == "Point"]
    assert len(points) == 1
    assert points[0].data.x == 3
    assert points[0].data.y == 4

    # line-string data is correct
    line_strings = [x for x in geoms if x.data.geom_type == "LineString"]
    assert len(line_strings) == 1
    assert line_strings[0].data[0][0] == 0
    assert line_strings[0].data[0][1] == 0
    assert line_strings[0].data[1][0] == 1
    assert line_strings[0].data[1][1] == 1

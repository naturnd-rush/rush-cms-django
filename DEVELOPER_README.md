## Dev Environment Setup

### a.) GDAL Lib Setup:
[The Geospatial Data Abstraction Library](https://github.com/OSGeo/gdal), or GDAL, is an open source MIT licensed translator library for raster and vector geospatial data formats.

1. Get GDAL system libraries: `sudo apt update && sudo apt install gdal-bin libgdal-dev -y`.
2. Check GDAL installation path `gdal-config --libs`. This usually outputs something like: `-L/usr/lib -lgdal`.
3. Run find to get the install location of your.so file: `find /usr/lib -name "libgdal.so*"`.
4. Put `GDAL_LIBRARY_PATH = "/usr/lib/x86_64-linux-gnu/libgdal.so.34"` <-- use whatever .so.xx file path is outputted, in your `settings.py` file.
5. Run `poetry add "GDAL==X.X.X"`, where the X's represent the major, minor, and patch version numbers outputted by the find command from step 3. E.g., if the first line of output reads: `/usr/lib/x86_64-linux-gnu/libgdal.so.34.3.8.4`, you would run `poetry add "GDAL==3.8.4"`, ignoring the first number, 34.
6. You __may__ also need to install Python bindings for GDAL on your operating system: `sudo apt install python3-gdal`.

## Useful Commands:

1. Start a PostGIS container with dev credentials locally on your machine.
```
docker run --name rush_postgis_container \
  -e POSTGRES_USER=rush_admin \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=rush \
  -p 5432:5432 \
  -d postgis/postgis
```
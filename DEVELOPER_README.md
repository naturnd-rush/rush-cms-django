## Dev Environment Setup

### a.) Create a `.env` file:
1. Copy the `.env-template` file into file named `.env` in the project's root directory.

### b.) GDAL Lib Setup:
[The Geospatial Data Abstraction Library](https://github.com/OSGeo/gdal), or GDAL, is an open source MIT licensed translator library for raster and vector geospatial data formats. GDAL requires some special setup.

1. Get GDAL system libraries: `sudo apt update && sudo apt install gdal-bin libgdal-dev -y`.
2. Check GDAL installation path `gdal-config --libs`. This usually outputs something like: `-L/usr/lib -lgdal`.
3. Run find to get the install location of your.so file: `find /usr/lib -name "libgdal.so*"`.
4. Put `GDAL_LIBRARY_PATH = "/usr/lib/x86_64-linux-gnu/libgdal.so.34"` <-- use whatever .so.xx file path is outputted, in your `.env` file.
5. Run `poetry add "GDAL==X.X.X"`, where the X's represent the major, minor, and patch version numbers outputted by the find command from step 3. E.g., if the first line of output reads: `/usr/lib/x86_64-linux-gnu/libgdal.so.34.3.8.4`, you would run `poetry add "GDAL==3.8.4"`, ignoring the first number, 34.
6. You __may__ also need to install Python bindings for GDAL on your operating system: `sudo apt install python3-gdal`.

### c.) Create a local PostGIS server:
A quick way to do this is to download docker on your machine and run: 
```
docker run --name rush_postgis_container \
  -e POSTGRES_USER=rush_admin \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=rush \
  -p 5432:5432 \
  -d postgis/postgis
```
However, if you already have other Postgres servers running locally, you may want to configure the `POSTGRES_*` lines in your `.env` file to make sure Django knows which database to look at.


### d.) Setup Django Project:
1. Install the [Poetry](https://python-poetry.org/docs/#installation) package manager for Python.
2. Install the project dependencies: `poetry install`.
3. Make Django migrations: `poetry run python manage.py makemigrations`.
4. Migrate your database using Django's migration system: `poetry run python manage.py migrate`.
5. Start the development server: `poetry run python manage.py runserver`.
6. Create a superuser so you can login to the development RUSH Admin Site: `poetry run python manage.py createsuperuser`.
7. Visit the development server url with `/admin` appended after the base url and use your superuser credentials to login.
8. That's it! You should now have a working version of the RUSH Admin Site's development server :)


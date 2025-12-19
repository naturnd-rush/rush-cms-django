# Setting-up the RUSH Development Environment
The most popular way to set up the RUSH Initiative development environment, and in many cases the easiest, is to configure and run our Docker Compose project by following the instructions outlined in "Method A". Alternatively, you can manually configure the RUSH Initiative project on your machine by following the instructions in "Method B," below.

## Method A: Using Docker Compose

1. Make sure you have [Docker](https://docs.docker.com/desktop/setup/install/linux/) installed on your machine.

2. You should see a file called `.env-template` in the project's root directory. Copy this file into a new file named `.env`.

3. Run `docker compose build`. This may take a while.

4. Run `docker compose up -d` to start the containers.

5. Run `docker compose exec -it django bash` to shell into the Django container.

6. Once inside the Django container, run `poetry run python manage.py createsuperuser` and follow the instructions to create a development login for the RUSH admin site.

7. Visit `http://127.0.0.1:8000/` and try logging into the admin site with your superuser credentials.
11. That's it! You should now have a working version of the RUSH Admin Site's development server :)

## Method B: Manual Configuration

**WARNING:** The following instructions assume you are running a linux OS that supports `apt`. If you are not running linux, it is likely *possible* that you can configure the project manually. However, this is not recommended.

1. You should see a file called `.env-template` in the project's root directory. Copy this file into a new file named `.env`.

2. Next, you will need to install [The Geospatial Data Abstraction Library](https://github.com/OSGeo/gdal), or GDAL, which is an open source MIT licensed translator library for raster and vector geospatial data formats. This needs to be done manually, because the version installed varies depending on what OS you're running, and you need to install the corresponding Python library (which wraps around your system's GDAL binary) with the same version number. Follow these instructions to install and configure GDAL:

    1. Get GDAL system libraries and python bindings: `sudo apt update && sudo apt install gdal-bin libgdal-dev python3-gdal -y`.
    2. Check GDAL installation path `gdal-config --libs`. This usually outputs something like: `-L/usr/lib -lgdal`.
    3. Run find to get the install location of your.so file: `find /usr/lib -name "libgdal.so*"`.
    4. Put `GDAL_LIBRARY_PATH = "/usr/lib/x86_64-linux-gnu/libgdal.so.34"` <-- use whatever `.so.xx` file path is outputted, in your `.env` file.
    5.  Run `poetry add "GDAL==X.X.X"`, where the X's represent the major, minor, and patch version numbers outputted by the find command from the pervious step. For example, if the first line of output reads: `/usr/lib/x86_64-linux-gnu/libgdal.so.34.3.8.4`, you would run `poetry add "GDAL==3.8.4"`, and ignore the first number, 34.

3. Create a local [Postgres](https://www.postgresql.org/download/) database with the [PostGIS](https://www.postgis.net/workshops/postgis-intro/installation.html) plugin installed. An easy way to do this, if you have Docker on your machine, is to run the command below. However, if you choose to create your PostGIS database manually, you must make sure that the postgres database name, username, password, host, and port match those in the project's `.env` file.
    ```
    docker run --name rush_postgis_container \
      -e POSTGRES_USER=rush_admin \
      -e POSTGRES_PASSWORD=password \
      -e POSTGRES_DB=rush \
      -p 5432:5432 \
      -d postgis/postgis
    ```

4. Install the [Poetry](https://python-poetry.org/docs/#installation) package manager for Python.
5. Run `poety install` to install the project's Python dependencies.
6. Make Django migrations: `poetry run python manage.py makemigrations`.
7. Migrate your database using Django's migration system: `poetry run python manage.py migrate`.
8. Start the development server: `poetry run python manage.py runserver`.
9. Create a superuser so you can login to the development RUSH Admin Site: `poetry run python manage.py createsuperuser`.
10. Visit `http://127.0.0.1:8000/` and try logging into the admin site with your superuser credentials.
11. That's it! You should now have a working version of the RUSH Admin Site's development server :)

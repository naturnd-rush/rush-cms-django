# Sam's Backup Program
This is a generic backup program written by Samuel Morris using rclone and is so far only compatible with a postgres database.

## Prerequisites:
1. Install and configure `rclone` with a remote, see [their documentation](https://rclone.org/docs/).
2. Have a Postgres database to backup, and optionally some other local directories.
3. Install the linux pre-requisites using your package manager of choice: 
a.)`pg_dump`, `python3`, `yq`, and `zip`.
b.) NOTE: Make sure your pg_dump version matches your Postgres database. Postgres is picky about version mismatches.
c.) NOTE: There are multiple versions of `yq`. The one you want is here: https://github.com/mikefarah/yq.

## Configuration:
See `config.yaml` to configure this backup program.

## Usage:
Run the bash program from inside the top-level directory of your project using `./backups/run.sh`.

If you have an environment file like `.env` formatted without the export keyword, you can use this command `export $(grep -v '^#' .env | xargs)` to export your environment so that the variables propagate to each subprocess correctly.

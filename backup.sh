#!/bin/bash

function now(){
    date '+%Y-%m-%d %H:%M:%S %Z -'
}

echo "$(now) Running backup..."

# Check script preconditions
required_tools=(
    rclone
    pg_dump
    zip
)
for toolname in "${required_tools[@]}"; do
    if [ -z "$(which $toolname)" ]; then
        echo "$(now) Backup failed. Please install and configure $toolname..."
        exit 1
    fi
done
if [ ! -f ".env" ]; then
    echo "$(now) Backup failed. Please make sure a '.env' file exists in the current directory."
    exit 1
fi
source .env
required_vars=(
    DJANGO_STATIC_ROOT
    DJANGO_MEDIA_ROOT
    DEPLOY_LOGS_DIR
    POSTGRES_DATABASE_NAME
    POSTGRES_DATABASE_USERNAME
    POSTGRES_DATABASE_PASSWORD
    POSTGRES_DATABASE_HOST
    POSTGRES_DATABASE_PORT
)
for varname in "${required_vars[@]}"; do
    if [ -z "${!varname}" ]; then
        echo "$(now) Backup failed due to missing env var: '$varname'."
        exit 1
    fi
done
if ! pg_isready -h "$POSTGRES_DATABASE_HOST" -p "$POSTGRES_DATABASE_PORT" -U "$POSTGRES_DATABASE_USERNAME" >/dev/null 2>&1; then
    echo "$(now) Backup failed. Cannot connect to Postgres at $POSTGRES_DATABASE_HOST:$POSTGRES_DATABASE_PORT. Is the database running?"
    exit 1
fi

# Actually perform a backup...
workspace_dir=".tmp_backup_workspace"
mkdir $workspace_dir

echo "$(now) Dumping Postgres database..."
BACKUP_FILE="$workspace_dir/postgres_rush_db_backup_$(date +%Y-%m-%dT%H:%M:%S_%Z).sql"
export PGPASSWORD="$POSTGRES_DATABASE_PASSWORD" # Needed for pg_dump to avoid prompting for a password
pg_dump -h "$POSTGRES_DATABASE_HOST" -p "$POSTGRES_DATABASE_PORT" -U "$POSTGRES_DATABASE_USERNAME" "$POSTGRES_DATABASE_NAME" > "$BACKUP_FILE"

echo "$(now) Copying and compressing files..."
backup_directories=(
    DJANGO_STATIC_ROOT
    DJANGO_MEDIA_ROOT
    DEPLOY_LOGS_DIR
)
for dirname in "${backup_directories[@]}"; do
    path="${!dirname}"
    if [ -d "$path" ]; then
        mkdir -p "$workspace_dir/$path"
        cp -r "$path" "$workspace_dir/$path"
    else
        echo "WARNING: Missing directory: '$path'. Skipping during backup."
    fi
done

echo "$(now) Done!"

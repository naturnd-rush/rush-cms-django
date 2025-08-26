#!/bin/bash

function now(){
    date '+%Y-%m-%d %H:%M:%S %Z'
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
        echo "$(now) - Backup failed. Please install and configure $toolname..."
        exit 1
    fi
done
if [ ! -f ".env" ]; then
    echo "$(now) - Backup failed. Please make sure a '.env' file exists in the current directory."
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
    RCLONE_REMOTE_NAME
)
for varname in "${required_vars[@]}"; do
    if [ -z "${!varname}" ]; then
        echo "$(now) - Backup failed due to missing env var: '$varname'."
        exit 1
    fi
done
if ! pg_isready -h "$POSTGRES_DATABASE_HOST" -p "$POSTGRES_DATABASE_PORT" -U "$POSTGRES_DATABASE_USERNAME" >/dev/null 2>&1; then
    echo "$(now) - Backup failed. Cannot connect to Postgres at $POSTGRES_DATABASE_HOST:$POSTGRES_DATABASE_PORT. Is the database running?"
    exit 1
fi

# Actually perform a backup...
workspace_dir=".tmp_backup_workspace"
mkdir $workspace_dir

echo "$(now) - Dumping Postgres database..."
official_backup_timestamp="$(date +"%Y-%m-%d_%I-%M-%S_%p")"
DB_BACKUP_FILE="$workspace_dir/postgres_rush_db_backup_$official_backup_timestamp.sql"
export PGPASSWORD="$POSTGRES_DATABASE_PASSWORD" # Needed for pg_dump to avoid prompting for a password
pg_dump -h "$POSTGRES_DATABASE_HOST" -p "$POSTGRES_DATABASE_PORT" -U "$POSTGRES_DATABASE_USERNAME" "$POSTGRES_DATABASE_NAME" > "$DB_BACKUP_FILE"

echo "$(now) - Copying files..."
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
        echo "$(now) - WARNING: Missing directory: '$path'. Skipping during backup."
    fi
done

# echo "$(now) Compressing files..."
# COMPRESSED_BACKUP_FILE="rush_backup_$official_backup_timestamp.zip"
# zip -r "$COMPRESSED_BACKUP_FILE" "$workspace_dir/" >/dev/null
rm -r "$workspace_dir"

#echo "$(now) Uploading backup file..."
#rclone copy $COMPRESSED_BACKUP_FILE $RCLONE_REMOTE_NAME

# Back off saving older backup versions to save storage space. For now, I'm gonna keep daily backups 7 days back, 
# weekly backups 4 weeks back, monthly backups 12 months back, and yearly backups 5 years back. Any additional backups
# outside this schema will be deleted.
echo "$(now) - Purging old backup files..."
keep_daily=7
keep_weekly=4
keep_monthly=12
keep_yearly=5

files_with_age=()
files=( $(rclone lsf $RCLONE_REMOTE_NAME | sort -r) )  # sorts newest first
for filename in "${files[@]}"; do
    IFS='_' read -r _ _ filedate _ <<< "$filename"  # split name string by underscores
    date_seconds=$(date -d "$filedate" +%s)
    now_seconds=$(date -d "$now" +%s)
    diff_seconds=$(( now_seconds - date_seconds ))
    age=$(( diff_seconds / 86400 ))  # age in days
    files_with_age+=("$filename|$age")
done

files_to_keep=()
for filename in "${files_with_age[@]}"; do
    echo "$filename"
done

#rclone delete "$RCLONE_REMOTE_NAME$filename"


# indices=(
#     1
#     2
#     3
#     4
#     5
#     6
#     7
#     8
#     9
#     10
#     11
#     12
#     13
#     14
#     15
#     16
#     17
#     18
#     19
#     20
#     21
#     22
#     23
#     24
#     25
#     26
#     27
#     28
#     29
#     30
#     31
#     32
#     33
#     34
#     35
#     36
#     50
#     100
#     225
#     250
#     200
#     300
#     500
# )
# for i in "${indices[@]}"; do
#     now_seconds=$(date -d "$now" +%s)
#     fake_backup_seconds=$(( now_seconds - (i * 86400) ))
#     fake_backup_date=$(date -d "@$fake_backup_seconds" +"%Y-%m-%d_%H-%M-%S")
#     touch "rush_backup_$fake_backup_date.zip"
# done

echo "$(now) Done!"

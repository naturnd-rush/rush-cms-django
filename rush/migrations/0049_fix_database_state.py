# Manual migration to fix database state inconsistency
# The database was manually corrected to match what migration 0048 should have done

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rush", "0048_remove_layeronquestion_layer_group_and_more"),
    ]

    operations = [
        # The RenameModel in 0048 should have preserved the question field,
        # but Django's migration state doesn't know about it.
        # This tells Django the field exists without touching the database.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="layergrouponquestion",
                    name="question",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="rush.question",
                    ),
                ),
            ],
            database_operations=[
                # Database already has this field from the rename
            ],
        ),
    ]

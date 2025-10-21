from django.core.management import call_command
from django.db import migrations


def reorder_models(apps, schema_editor):
    """
    Reorder display_order fields for sortable models. This ensures sequential ordering starting
    from 0 and is required for django-admin-sortable2 to function as an initial migration.
    """
    models_to_reorder = [
        "rush.Question",
        "rush.QuestionTab",
        "rush.LayerOnLayerGroup",
        "rush.LayerGroupOnQuestion",
    ]

    for model in models_to_reorder:
        try:
            call_command("reorder", model)
        except Exception as e:
            print(f"ERROR: Could not reorder {model}: {e}")


def reverse_reorder(apps, schema_editor):
    """
    Reverse operation - does nothing as reordering is non-destructive.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rush", "0052_alter_layergrouponquestion_group_description"),
    ]

    operations = [
        migrations.RunPython(reorder_models, reverse_reorder),
    ]

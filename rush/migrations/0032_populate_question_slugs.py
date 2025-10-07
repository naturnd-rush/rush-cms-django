"""Populate Question.slug for existing records.

This migration will iterate over all Question objects and call save() to
trigger the model's slug generation logic when slug is empty.

It is safe to run multiple times; existing slugs are left intact.
"""
from django.db import migrations


def populate_slugs(apps, schema_editor):
    Question = apps.get_model("rush", "Question")
    for q in Question.objects.all():
        # If slug is falsy (None or empty string), assign and save
        if not q.slug:
            # Call the model's save which will populate slug
            q.save()


class Migration(migrations.Migration):

    dependencies = [
        ("rush", "0031_historicalquestion_slug_question_slug"),
    ]

    operations = [
        migrations.RunPython(populate_slugs, reverse_code=migrations.RunPython.noop),
    ]

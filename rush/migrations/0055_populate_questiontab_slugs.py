"""
Populate QuestionTab.slug for existing records.

This migration will iterate over all QuestionTab objects and generate slugs
based on their title, similar to how Question slugs are generated.

It is safe to run multiple times; existing slugs are left intact.
"""

from typing import TYPE_CHECKING
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import migrations
from django.db.models import QuerySet
from django.utils.text import slugify

if TYPE_CHECKING:
    from rush.models.question import QuestionTab


def populate_slugs(apps, schema_editor):
    QuestionTabModel: QuestionTab = apps.get_model("rush", "QuestionTab")
    question_tabs: QuerySet[QuestionTab] = QuestionTabModel.objects.all()
    for tab in question_tabs:
        if not tab.slug:
            tab.slug = slugify(tab.title)
            # Check if this slug already exists for this question
            existing = QuestionTabModel.objects.filter(
                slug=tab.slug, question=tab.question
            ).exclude(pk=tab.pk).exists()
            if existing:
                print(f"WARNING: Duplicate slug found on QuestionTab '{tab.id}', generating a random slug...")
                tab.slug = f"{tab.slug}-{uuid4().hex[:8]}"
            tab.save()


class Migration(migrations.Migration):

    dependencies = [
        ("rush", "0054_questiontab_slug"),
    ]

    operations = [
        migrations.RunPython(populate_slugs, reverse_code=migrations.RunPython.noop),
    ]

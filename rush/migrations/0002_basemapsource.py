from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rush", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BasemapSource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tile_url", models.CharField(max_length=512)),
                ("max_zoom", models.PositiveIntegerField()),
                ("attribution", models.TextField()),
            ],
        ),
    ]

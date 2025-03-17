# questions/models.py

import uuid

from django.db import models
from simple_history.models import HistoricalRecords


class Provider(models.TextChoices):
    GEOJSON = "geojson"
    OPEN_GREEN_MAP = "open_green_map"
    ESRI_FEATURE_SERVER = "esri_feature_server"  # TODO: Not sure how this gets implemented with the current MapData model
    GENERIC_REST = "generic_rest"  # TODO: Not sure how this gets implemented with the current MapData model


class MapData(models.Model):
    # TODO: Add on_create validation
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=255, choices=Provider.choices)
    geojson = models.JSONField(null=True, blank=True)

    # Open Green Map metadata
    ogm_map_id = models.CharField(max_length=1024, null=True, blank=True)
    feature_url_template = models.CharField(max_length=1024, null=True, blank=True)
    icon_url_template = models.CharField(max_length=1024, null=True, blank=True)
    image_url_template = models.CharField(max_length=1024, null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Layer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    description = models.TextField()

    map_data = models.ForeignKey(
        to=MapData,
        # Prevent MapData from being deleted if a Layer relies on it
        on_delete=models.PROTECT,
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.title


class SubQuestionDiplay(models.TextChoices):
    FULL_WINDOW = "full_window"
    CARD = "card"


class SubQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    content = models.TextField()

    button_text = models.CharField(max_length=255)
    display = models.CharField(max_length=255, choices=SubQuestionDiplay.choices)

    sub_question = models.ForeignKey(
        to="self",
        null=True,
        blank=True,
        # If a SubQuestion is deleted, nothing happens to this Question
        on_delete=models.DO_NOTHING,
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.title} - {self.subtitle}"


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    layer = models.ForeignKey(
        to=Layer,
        # Prevent a Layer from being deleted if a Question relies on it
        on_delete=models.PROTECT,
    )
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    image = models.ImageField(upload_to="question_images/", null=True, blank=True)
    content = models.TextField()

    sub_question = models.ForeignKey(
        to=SubQuestion,
        null=True,
        blank=True,
        # If a SubQuestion is deleted, nothing happens to this Question
        on_delete=models.DO_NOTHING,
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.title


class Initiative(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    # TODO: complete this model

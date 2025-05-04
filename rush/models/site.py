import uuid

from django.db import models

"""
Django models related to frontend UI / display.
"""

# TODO: make a page/link model! Probably one model with dual interpretation by the frontend.


import uuid

import django.db.models as models
from simple_history.models import HistoricalRecords


class Question(models.Model):
    """
    A question that ties together one or more map layers into a data-driven narrative.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="question_images/", null=True, blank=True)
    content = models.TextField()
    initiatives = models.ManyToManyField(to="Initiative")
    history = HistoricalRecords()
    layer = models.ForeignKey(
        to="Layer",
        # Prevent a Layer from being deleted if a Question relies on it
        on_delete=models.PROTECT,
    )
    sub_question = models.ForeignKey(
        to="QuestionTab",
        null=True,
        blank=True,
        # If a QuestionTab is deleted, nothing happens to this Question
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return self.title


class QuestionTab(models.Model):
    """ """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    content = models.TextField()

    button_text = models.CharField(max_length=255)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.title} - {self.subtitle}"


class Initiative(models.Model):
    """
    A project, group, or resource relevant to answering one or more questions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    image = models.ImageField(upload_to="initiative_images/", null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField(to="InitiativeTag", related_name="initiatives")

    def __str__(self):
        return self.title


class InitiativeTag(models.Model):
    """
    A descriptive word or phrase that represents a category of initiatives.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

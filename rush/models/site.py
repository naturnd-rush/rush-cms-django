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
    initiatives = models.ManyToManyField(to="Initiative", blank=True)
    questions = models.ManyToManyField(to="Layer", related_name="questions")
    history = HistoricalRecords()

    def __str__(self):
        return self.title


class QuestionTab(models.Model):
    """ """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    question = models.ForeignKey(
        null=True,
        # Delete all QuestionTabs when a Question is deleted.
        to="Question",
        on_delete=models.CASCADE,
        related_name="tabs",
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.title} for question: '{self.question.title}'"


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


class LayerGroup(models.Model):
    """
    The title of a group of layers in the legend.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    group_name = models.CharField(max_length=255)
    group_description = models.TextField(blank=True, help_text="Optional description.")

    def __str__(self):
        return self.group_name


class LayerOnQuestion(models.Model):
    """
    Connect each question card to multiple Layers.
    """

    layer = models.ForeignKey(to="Layer", on_delete=models.CASCADE)
    question = models.ForeignKey(to="Question", on_delete=models.CASCADE)

    active_by_default = models.BooleanField(
        default=False,
        help_text="Whether the layer is active by default when a new question is loaded.",
    )
    layer_group = models.ForeignKey(
        to=LayerGroup,
        on_delete=models.CASCADE,
        help_text="The title of the layer group.",
    )


class Page(models.Model):
    """
    A static webpage on the website.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255, help_text="The title of the webpage.")
    content = models.TextField(help_text="The content that will appear on the webpage.")

    def __str__(self):
        return f"{self.title} - Page"

from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin

from rush import models
from rush.admin import utils
from rush.admin.widgets import SummernoteWidget


class BasemapSourceForm(forms.ModelForm):
    """
    Override the default add/change page for the Initiative model admin.
    """

    class Meta:
        model = models.BasemapSource
        fields = [
            "name",
            "tile_url",
            "attribution",
            "max_zoom",
            "is_default",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attribution"].widget = SummernoteWidget()

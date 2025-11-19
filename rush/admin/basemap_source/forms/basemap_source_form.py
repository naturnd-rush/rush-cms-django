from django import forms
from django.db import models

from rush import models
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

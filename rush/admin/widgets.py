import json
import logging

from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_summernote.widgets import SummernoteWidgetBase

logger = logging.getLogger(__name__)


class SummernoteWidgetFactory:
    """
    Creates Summernote widgets with specified parameters.
    """

    def __init__(self, width="500px", height="300px", **kwargs):
        self.render_kwargs = kwargs | {'width': width, 'height': height}

    def _make_render_fn(self, render_kwargs):
        def render(self, name, value, attrs=None, **kwargs):
            if attrs is None:
                attrs = {}
            summernote_settings = self.summernote_settings()
            summernote_settings.update(**self.render_kwargs)

            html = super().render(name, value, attrs=attrs, **kwargs)
            context = {
                "id": attrs["id"],
                "id_safe": attrs["id"].replace("-", "_"),
                "flat_attrs": flatatt(self.final_attr(attrs)),
                "settings": json.dumps(summernote_settings),
                "src": reverse("django_summernote-editor", kwargs={"id": attrs["id"]}),
                # Width and height have to be pulled out to create an iframe with correct size
                "width": summernote_settings["width"],
                "height": summernote_settings["height"],
            }

            html += render_to_string("django_summernote/widget_iframe.html", context)
            return mark_safe(html)


class SummernoteWidget(SummernoteWidgetBase):
    

import logging
from typing import Any, Dict

from django import forms
from django.contrib import admin
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import Initiative, InitiativeTag, Layer, MapData, Question, SubQuestion

logger = logging.getLogger(__name__)


def image_html(image_url: str, image_width: int = 200) -> str:
    """
    Return HTML for rendering an image.
    """
    return mark_safe(f'<img src="{image_url}" width="{image_width}" height="auto" />')


def content_preview_fn(
    content_attr_name: str = "content",
    preview_chars: int = 500,
):
    """
    Return an admin model function that renders a preview of some
    content in the inline display.
    """

    def inner(admin_instance: admin.ModelAdmin, obj: models.Model) -> str:
        content = getattr(obj, content_attr_name, None)
        if not content:
            return "No content"
        return format_html(content[:preview_chars] + "...")

    return inner


class QuestionForm(forms.ModelForm):
    """
    Override the default add/change page for the Question model admin.
    TODO: Maybe delete this form and inject JS for preview using readonly_fields?
    """

    class Meta:
        model = Question
        fields = ["title", "subtitle", "image", "content", "initiatives"]

    def __init__(self, *args, **kwargs):
        """
        Inject image HTML in "image" field help text.
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.image:
            self.fields["image"].help_text = image_html(self.instance.image.url)

    def clean_image(self):
        """
        Can add custom image validation here if we want...
        """
        image = self.cleaned_data.get("image")
        return image


@admin.register(Question)
class QuestionAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    form = QuestionForm
    summernote_fields = ["content"]
    list_display = [
        "title",
        "subtitle",
        "content_preview",
        "image_preview",
        "get_initiatives",
    ]
    content_preview = content_preview_fn()
    filter_horizontal = ["initiatives"]  # better admin editing for many-to-many fields

    def image_preview(self, obj):
        """
        Image preview inline.
        """
        if obj.image:
            return image_html(obj.image.url)
        return "No image"

    def get_initiatives(self, obj):
        if obj.initiatives.count() > 0:
            return ", ".join([initiative.title for initiative in obj.initiatives.all()])
        return "No Initiatives"

    get_initiatives.short_description = "Initiatives"


@admin.register(SubQuestion)
class SubQuestionAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    list_display = ["title", "subtitle", "content_preview"]
    content_preview = content_preview_fn()


@admin.register(Layer)
class LayerAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]

    def render_change_form(self, request, context, *args, **kwargs):
        obj = context.get("original")
        geojson = obj.map_data.geojson if obj and obj.map_data.geojson else {}
        map_preview_html = get_map_preview_html(geojson, "id_map_data")

        try:
            context["adminform"].form.fields["map_data"].help_text = map_preview_html
        except (KeyError, AttributeError):
            logger.exception("Failed to inject map preview.")
        finally:
            return super().render_change_form(request, context, *args, **kwargs)


class MapDataAdminForm(forms.ModelForm):

    class Meta:
        model = MapData
        fields = "__all__"
        widgets = {
            "geojson": forms.Textarea(
                attrs={"rows": 20, "cols": 150, "id": "geojson-input"}
            ),
        }


@admin.register(MapData)
class MapDataAdmin(SimpleHistoryAdmin):
    form = MapDataAdminForm
    exclude = ["id"]
    list_display = ["name", "provider"]

    def render_change_form(self, request, context, *args, **kwargs):
        obj = context.get("original")
        geojson = obj.geojson if obj and obj.geojson else {}
        map_preview_html = get_map_preview_html(geojson, "geojson-input")

        try:
            context["adminform"].form.fields["geojson"].help_text = map_preview_html
        except (KeyError, AttributeError):
            logger.exception("Failed to inject map preview.")
        finally:
            return super().render_change_form(request, context, *args, **kwargs)


class InitiativeForm(forms.ModelForm):
    """
    Override the default add/change page for the Initiative model admin.
    """

    class Meta:
        model = Initiative
        fields = ["title", "image", "content", "tags"]

    def __init__(self, *args, **kwargs):
        """
        Inject image HTML in "image" field help text.
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.image:
            self.fields["image"].help_text = image_html(self.instance.image.url)

    def clean_image(self):
        """
        Can add custom image validation here if we want...
        """
        image = self.cleaned_data.get("image")
        return image


@admin.register(Initiative)
class InitiativeAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    form = InitiativeForm
    list_display = ["title", "content_preview", "image_preview", "get_tags"]
    content_preview = content_preview_fn()
    filter_horizontal = ["tags"]  # better admin editing for many-to-many fields

    def image_preview(self, obj):
        """
        Image preview inline.
        """
        if obj.image:
            return image_html(obj.image.url)
        return "No image"

    def get_tags(self, obj):
        if obj.tags.count() > 0:
            return ", ".join([tag.name for tag in obj.tags.all()])
        return "No Tags"

    get_tags.short_description = "Tags"


@admin.register(InitiativeTag)
class InitiativeTagAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    list_display = ["name", "get_initiatives"]

    # Reverse relation is readonly in the add/change view for now, we can
    # change this later, but the solution is a little complicated.
    readonly_fields = ["get_initiatives"]

    def get_initiatives(self, obj):
        if obj.initiatives.count() > 0:
            return ", ".join([initiative.title for initiative in obj.initiatives.all()])
        return "No Initiatives"

    get_initiatives.short_description = "Initiatives"

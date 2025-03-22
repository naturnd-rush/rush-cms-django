import logging

from django import forms
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from rush import models
from rush.admin import utils

logger = logging.getLogger(__name__)


@admin.register(models.Layer)
class LayerAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]

    def render_change_form(self, request, context, *args, **kwargs):
        obj = context.get("original")
        geojson = obj.map_data.geojson if obj and obj.map_data.geojson else {}
        map_preview_html = utils.get_map_preview_html(geojson, "id_map_data")

        try:
            context["adminform"].form.fields["map_data"].help_text = map_preview_html
        except (KeyError, AttributeError):
            logger.exception("Failed to inject map preview.")
        finally:
            return super().render_change_form(request, context, *args, **kwargs)


class MapDataAdminForm(forms.ModelForm):

    class Meta:
        model = models.MapData
        fields = "__all__"
        widgets = {
            "geojson": forms.Textarea(
                attrs={"rows": 20, "cols": 150, "id": "geojson-input"}
            ),
        }


@admin.register(models.MapData)
class MapDataAdmin(SimpleHistoryAdmin):
    form = MapDataAdminForm
    exclude = ["id"]
    list_display = ["name", "provider"]

    def render_change_form(self, request, context, *args, **kwargs):
        obj = context.get("original")
        geojson = obj.geojson if obj and obj.geojson else {}
        map_preview_html = utils.get_map_preview_html(geojson, "geojson-input")

        try:
            context["adminform"].form.fields["geojson"].help_text = map_preview_html
        except (KeyError, AttributeError):
            logger.exception("Failed to inject map preview.")
        finally:
            return super().render_change_form(request, context, *args, **kwargs)

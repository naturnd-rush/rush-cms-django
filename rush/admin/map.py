import logging

from django import forms
from django.contrib import admin
from django.db import models as django_db_models
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from rush import models
from rush.admin import utils

logger = logging.getLogger(__name__)


class StyleOnLayerInline(admin.TabularInline):
    template = "admin/rush/stylesonlayer/edit_inline/tabular.html"
    verbose_name_plural = "Styles applied to this Layer"
    model = models.StylesOnLayer
    extra = 0
    exclude = ["id"]
    fields = ["style", "feature_mapping"]
    autocomplete_fields = [
        # uses the searchable textbox in the admin form to add/remove Styles
        "style"
    ]
    formfield_overrides = {
        django_db_models.TextField: {
            # make the feature mapping textarea a smaller size (default is wayyy to large)
            "widget": forms.Textarea(attrs={"rows": 1, "cols": 40})
        },
    }


@admin.register(models.Layer)
class LayerAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    inlines = [StyleOnLayerInline]

    def render_change_form(self, request, context, *args, **kwargs):
        # obj = context.get("original")
        # geojson = obj.map_data.geojson if obj and obj.map_data.geojson else {}
        map_preview_html = mark_safe(
            '<div id="map-preview" style="height: 400px; margin-bottom: 1em;"></div>'
            '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />'
            '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
        )

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
    exclude = [
        # for now, exclude these because they are confusing to people who just wanna upload GeoJson
        *exclude,
        "ogm_map_id",
        "feature_url_template",
        "icon_url_template",
        "image_url_template",
    ]
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


class StyleForm(forms.ModelForm):

    class Meta:
        model = models.Style
        fields = [
            # Stroke data
            "draw_stroke",
            "stroke_color",
            "stroke_weight",
            "stroke_opacity",
            "stroke_line_cap",
            "stroke_line_join",
            "stroke_dash_array",
            "stroke_dash_offset",
            # Fill data
            "draw_fill",
            "fill_color",
            "fill_opacity",
            # Icon data
            "draw_marker",
            "marker_icon",
            "marker_icon_opacity",
            # "fill_rule", <-- gonna handle this later. Seems like an extreme edge-case for using the admin site.
            # I put the style name at end of submission because I feel like people will want to create
            # the style, and then name it after they have a solid idea of what it will look like, but that's just me.
            "name",
        ]
        widgets = {
            "stroke_weight": utils.SliderAndTextboxNumberInput(max=30, step=0.05),
            "stroke_opacity": utils.SliderAndTextboxNumberInput(),
            "stroke_dash_offset": utils.SliderAndTextboxNumberInput(max=100, step=1),
            "fill_opacity": utils.SliderAndTextboxNumberInput(),
            "marker_icon_opacity": utils.SliderAndTextboxNumberInput(),
            "marker_icon": utils.LiveImagePreviewInput(),
        }

    class Media:
        js = [
            "style_preview.js",
            "slider_textbox_input_sync.js",
            "live_image_preview_refresh.js",
        ]


@admin.register(models.Style)
class StyleAdmin(SimpleHistoryAdmin):
    form = StyleForm
    readonly_fields = ["style_preview"]
    exclude = ["id"]
    search_fields = ["name"]

    @admin.display(description="Style Preview")
    def style_preview(self, obj):
        """
        Readonly field that previews the style while it's being changed or created.
        The `style_preview.js` file hooks into the HTML element generated by this function.
        """
        return mark_safe('<div id="style_preview"></div>')

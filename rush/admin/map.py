import json
import logging
from typing import Any, List

from django import forms
from django.contrib import admin
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin
from django_summernote.widgets import SummernoteWidgetBase
from simple_history.admin import SimpleHistoryAdmin

from rush import models
from rush.admin import utils

logger = logging.getLogger(__name__)


class SummernoteWidget(SummernoteWidgetBase):
    def render(self, name, value, attrs=None, **kwargs):
        if attrs is None:
            attrs = {}
        summernote_settings = self.summernote_settings()
        summernote_settings.update(
            {
                "height": "300px",
                "width": "500px",
                "toolbar": [
                    ["style", ["bold", "italic", "underline"]],
                    ["para", ["ul", "ol"]],
                    ["insert", ["link", "picture"]],
                ],
                "disableDragAndDrop": True,
            }
        )

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


class StylesOnLayerInlineForm(forms.ModelForm):
    class Meta:
        model = models.StylesOnLayer
        fields = ["style", "feature_mapping", "popup"]
        widgets = {
            "popup": SummernoteWidget(),
            "feature_mapping": forms.Textarea(attrs={"rows": 1, "cols": 50}),
        }


class StyleOnLayerInline(admin.TabularInline):
    form = StylesOnLayerInlineForm
    verbose_name_plural = "Styles applied to this Layer"
    model = models.StylesOnLayer
    extra = 0
    exclude = ["id"]
    autocomplete_fields = [
        # uses the searchable textbox in the admin form to add/remove Styles
        "style"
    ]


class LayerForm(forms.ModelForm):
    serialized_leaflet_json = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = models.Layer
        exclude = ["id"]


@admin.register(models.Layer)
class LayerAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    form = LayerForm
    inlines = [StyleOnLayerInline]
    autocomplete_fields = ["map_data"]
    search_fields = ["name"]

    def render_change_form(self, request, context, *args, **kwargs):
        map_preview_html = mark_safe(
            '<div id="map-preview" style="height: 600px; margin-bottom: 1em;"></div>'
            '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />'
            '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
        )
        try:
            context["adminform"].form.fields["map_data"].help_text = map_preview_html
        except (KeyError, AttributeError):
            logger.exception("Failed to inject map preview.")
        finally:
            return super().render_change_form(request, context, *args, **kwargs)

    def _inject_serialized_leaflet_json(self, obj, form) -> None:
        """
        Takes the serialized leaflet json data from a hidden field on the form and injects it into
        the model at model save time.
        """
        fieldname = "serialized_leaflet_json"
        data = form.cleaned_data.get(fieldname)
        if not data:
            raise forms.ValidationError(f"Error saving {fieldname} data!")

        # Avoid double-serialization
        parsed = json.loads(data)

        setattr(obj, fieldname, parsed)

    def save_model(self, request, obj, form, change):
        self._inject_serialized_leaflet_json(obj, form)
        super().save_model(request, obj, form, change)


class MapDataAdminForm(forms.ModelForm):

    PROVIDER_FIELDS_MAP = {
        # Define what fields are shown by the frontend depending on which map_data.provider is selected
        models.Provider.GEOJSON: ["geojson"],
        models.Provider.OPEN_GREEN_MAP: ["ogm_map_link", "ogm_campaign_link"],
    }

    @classmethod
    def _get_unused_provider_fields(cls, selected_provider: models.Provider) -> List[str]:
        """
        The fields that are not used for the given provider.
        """
        unused = []
        for provider, fields in cls.PROVIDER_FIELDS_MAP.items():
            if provider != selected_provider:
                unused = [*unused, *fields]
        return unused

    # Geojson provider fields
    geojson = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "cols": 50, "id": "geojson-input"}),
        initial="",
        required=False,
    )

    # Open green map provider fields
    ogm_map_link = forms.CharField(max_length=2000, required=False)
    ogm_campaign_link = forms.CharField(max_length=2000, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inject field information on provider so the frontend can know which
        # fields to show depending on what value is selected in the dropdown.
        self.fields["provider"].widget.attrs["show-fields-map"] = json.dumps(self.PROVIDER_FIELDS_MAP)

        if self.instance and self.instance.pk:
            if self.instance.ogm_provider:
                # Load OpenGreenMapProvider field values when the form is loaded initially
                self.fields["ogm_map_link"].initial = self.instance.ogm_provider.map_link
                self.fields["ogm_campaign_link"].initial = self.instance.ogm_provider.campaign_link

    class Meta:
        model = models.MapData
        fields = ["id", "name", "provider", "geojson", "ogm_map_link", "ogm_campaign_link"]
        widgets = {
            "geojson": forms.Textarea(attrs={"rows": 20, "cols": 150, "id": "geojson-input"}),
        }

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        provider = models.Provider(cleaned_data["provider"])
        for unused_field in self._get_unused_provider_fields(provider):
            # set unused fields (relative to the currently selected map data provider) to None
            cleaned_data[unused_field] = None

        if provider == models.Provider.GEOJSON:
            # TODO: Maybe validate GeoJson data?
            return cleaned_data

        elif provider == models.Provider.OPEN_GREEN_MAP:
            try:

                # update or create an open green maps provider
                if self.instance.ogm_provider:
                    ogm = self.instance.ogm_provider
                    ogm.map_link = self.cleaned_data["ogm_map_link"]
                    ogm.campaign_link = self.cleaned_data["ogm_campaign_link"]
                else:
                    ogm = models.OpenGreenMapProvider.objects.create(
                        map_link=self.cleaned_data["ogm_map_link"],
                        campaign_link=self.cleaned_data["ogm_campaign_link"],
                    )
                ogm.full_clean()
                cleaned_data["ogm_provider"] = ogm

                for fieldname in self.PROVIDER_FIELDS_MAP[provider]:
                    # pop subfields that are now a part of the ogm_provider model
                    cleaned_data.pop(fieldname)

            except forms.ValidationError as e:
                # Propagate field-specific errors
                for field, messages in e.message_dict.items():
                    self.add_error(f"ogm_{field}", ", ".join(messages))

        return cleaned_data

    def save(self, commit=True) -> Any:
        if self.instance and self.instance.provider:
            if self.instance.provider == models.Provider.OPEN_GREEN_MAP:
                # Save OGM provider model onto this MapData instance
                self.instance.ogm_provider = self.cleaned_data["ogm_provider"]
        return super().save(commit)


def get_map_preview_html(
    geojson: dict[str, Any],
    change_element_id: str,
    height: str = "400px",
) -> str:
    """
    Return an HTML + JS snippet that renders a basic map preview.
    """
    leaflet_html = render_to_string(
        template_name="admin/geojson_map_preview.html",
        context={
            "geojson_data": mark_safe(json.dumps(geojson)),
            "height": height,
            "change_element_id": change_element_id,
        },
    )
    return mark_safe(leaflet_html)


@admin.register(models.MapData)
class MapDataAdmin(SimpleHistoryAdmin):
    form = MapDataAdminForm
    exclude = ["id"]
    list_display = ["name", "provider"]
    search_fields = ["name"]

    def render_change_form(self, request, context, *args, **kwargs):
        obj: models.MapData = context.get("original")
        geojson = obj.geojson if obj and obj.geojson else {}
        map_preview_html = get_map_preview_html(geojson, "geojson-input")

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
            "marker_background_color",
            "marker_icon",
            "marker_icon_opacity",
            # "fill_rule", <-- gonna handle this later. Seems like an extreme edge-case for using the admin site.
            # I put the style name at end of submission because I feel like people will want to create
            # the style, and then name it after they have a solid idea of what it will look like, but that's just me.
            "name",
        ]
        widgets = {
            "stroke_weight": utils.SliderAndTextboxNumberInput(max=30, step=0.05, attrs={"class": "inline-field"}),
            "stroke_opacity": utils.SliderAndTextboxNumberInput(),
            "stroke_dash_offset": utils.SliderAndTextboxNumberInput(max=100, step=1),
            "fill_opacity": utils.SliderAndTextboxNumberInput(),
            "marker_icon_opacity": utils.SliderAndTextboxNumberInput(),
            "marker_icon": forms.FileInput(),
        }

    class Media:
        js = [
            # "style_preview.js",
            # "slider_textbox_input_sync.js",
            # "live_image_preview_refresh.js",
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
        return mark_safe('<div id="style_preview" style="position: relative;"></div>')

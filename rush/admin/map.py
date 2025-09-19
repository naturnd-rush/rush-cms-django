import json
import logging
from dataclasses import asdict, dataclass
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
                    ["style", ["bold", "italic", "underline", "h1"]],
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


class MapDataChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj) -> str:
        if obj and isinstance(obj, models.MapData):
            # Customize the MapData dropdown label without touching __str__
            return f"{obj.name} ({obj.provider_state.upper()})"
        return "Unknown Map Data"


class LayerForm(forms.ModelForm):
    serialized_leaflet_json = forms.CharField(widget=forms.HiddenInput())
    map_data = MapDataChoiceField(queryset=models.MapData.objects.all())

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


@dataclass
class MapDataAdminFormConfig:
    """
    This form is a little more complicated and requires some configuration to determine
    it's business logic. An instance of this class stores all the necessary configuration
    data for this form.
    """

    @dataclass
    class Field:
        fieldname: str
        required: bool  # is the field required on form save?

    @dataclass
    class Provider:
        state: models.MapData.ProviderState
        fields: List["MapDataAdminFormConfig.Field"]
        map_preview: bool  # Whether to render the map preview for this provider

    providers: List["MapDataAdminFormConfig.Provider"]

    def get_fields(self) -> List[Field]:
        fields = []
        for provider in self.providers:
            for field in provider.fields:
                fields.append(field)
        return fields

    def get_provider(self, provider_state: models.MapData.ProviderState | str) -> Provider | None:
        """
        Get an admin form config `Provider` from a `ProviderState`, or return None if none could be found.
        """
        if not isinstance(provider_state, models.MapData.ProviderState):
            provider_state = models.MapData.ProviderState(provider_state)
        for provider in self.providers:
            if provider.state == provider_state:
                return provider
        return None


mdaf_config = MapDataAdminFormConfig(
    providers=[
        MapDataAdminFormConfig.Provider(
            state=models.MapData.ProviderState.GEOJSON,
            fields=[MapDataAdminFormConfig.Field("_geojson", required=True)],
            map_preview=True,
        ),
        MapDataAdminFormConfig.Provider(
            state=models.MapData.ProviderState.OPEN_GREEN_MAP,
            fields=[
                MapDataAdminFormConfig.Field("map_link", required=True),
                MapDataAdminFormConfig.Field("campaign_link", required=False),
            ],
            map_preview=False,
        ),
    ]
)


class MapDataAdminForm(forms.ModelForm):
    """
    For submitting `MapData` info.
    """

    class Meta:
        model = models.MapData
        fields = ["id", "name", "provider_state", *[field.fieldname for field in mdaf_config.get_fields()]]

    def get_initial_for_field(self, field, field_name):
        if field_name == "_geojson":
            if self.instance and isinstance(self.instance, models.MapData):
                if self.instance._geojson is None:
                    # Replace "null" in geojson form field with "{}"
                    return {}
        return super().get_initial_for_field(field, field_name)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inject field information on provider so the frontend can know which
        # provider fields to show depending on what value is selected in the dropdown.
        # TODO: Should probably move this to the admin "render changeform" method and use context[VAR_NAME]
        #       to inject this data, instead of hackily putting JSON data into HTML elements like this...
        # self.fields["provider_state"].widget.attrs["show-fields-map"] = json.dumps(
        #     models.MapData.get_formfield_map()
        # )
        # all_fields = []
        # for fieldlist in models.MapData.get_formfield_map().values():
        #     for field in fieldlist:
        #         all_fields.append(field["name"])
        # self.fields["provider_state"].widget.attrs["all-fields"] = json.dumps({"fieldnames": all_fields})

        # Remove "UNSET" option from dropdown menu
        self.fields["provider_state"].choices = [
            (value, label)
            for value, label in models.MapData.ProviderState.choices
            if value != models.MapData.ProviderState.UNSET
        ]

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        provider = mdaf_config.get_provider(cleaned_data["provider_state"])

        if not (
            self.instance
            and provider
            and isinstance(self.instance, models.MapData)
            and "provider_state" in cleaned_data
            and cleaned_data["provider_state"] in models.MapData.ProviderState
        ):
            # Exit early
            return cleaned_data

        required_fieldnames = [field.fieldname for field in provider.fields if field.required]
        for fieldname in required_fieldnames:
            if fieldname not in self.errors:
                if fieldname not in cleaned_data or not cleaned_data[fieldname]:
                    # Enforce required fields dynamically (depending on selected provider state)
                    self.add_error(fieldname, "This field is required.")

        non_provider_fieldnames = [
            field.fieldname for field in mdaf_config.get_fields() if field not in provider.fields
        ]
        for fieldname in non_provider_fieldnames:
            # Ignore fields dynamically (belonging to other provider states)
            if fieldname in self.errors:
                self.errors.pop(fieldname)
            cleaned_data[fieldname] = None

        return cleaned_data


@admin.register(models.MapData)
class MapDataAdmin(SimpleHistoryAdmin):
    form = MapDataAdminForm
    exclude = ["id"]
    list_display = ["name", "provider_state"]
    search_fields = ["name"]

    @staticmethod
    def _get_geojson_str(context) -> str:
        if map_data := context.get("original"):
            if isinstance(map_data, models.MapData):
                try:
                    return map_data.get_raw_geojson_data()
                except models.MapData.NoGeoJsonData:
                    pass
        return "{}"

    def render_change_form(self, request, context, *args, **kwargs):
        """
        Inject initial GeoJSON data into page so we can render an initial
        `MapData` preview in the change form.
        """
        geojson = self._get_geojson_str(context)
        context["map_data_admin_form_config"] = mark_safe(json.dumps(asdict(mdaf_config)))
        context["initial_geojson_data"] = mark_safe(geojson)
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

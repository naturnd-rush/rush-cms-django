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
    """
    For submitting `MapData` info. This form handles creating / destroying
    `MapDataProvider objects depending on the new data being saved. It adds additional
    fields for each `Provider` type and cleans the data depending on which `Provider` is selected.
    """

    class Meta:
        model = models.MapData
        fields = ["id", "name", "provider_state", "_geojson", "map_link", "campaign_link"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inject field information on provider so the frontend can know which
        # provider fields to show depending on what value is selected in the dropdown.
        self.fields["provider_state"].widget.attrs["show-fields-map"] = json.dumps(
            models.MapData.get_formfield_map()
        )

        # Remove "UNSET" option from dropdown menu
        self.fields["provider_state"].choices = [
            (value, label)
            for value, label in models.MapData.ProviderState.choices
            if value != models.MapData.ProviderState.UNSET
        ]

        # try:
        #     map_data = self._validate_map_data()
        #     provider = self._validate_provider()
        #     provider_instance = provider.get_instance(map_data)
        # except ValueError:
        #     return

        # # If the map data already has a provider, we want to inject the already submitted field
        # # values into the form so they can be edited by the user.
        # provider_formfields = [rf for rf in RELATED_FORMFIELDS if rf.provider == provider]
        # for provider_formfield in provider_formfields:
        #     try:
        #         field_value = getattr(provider_instance, provider_formfield.provider_fieldname)
        #         self.fields[provider_formfield.form_fieldname].initial = field_value
        #     except (KeyError, AttributeError):
        #         msg = "Unable to inject initial value on MapData change form for {}."
        #         logger.warning(msg.format(provider_formfield))

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        if not (
            self.instance
            and isinstance(self.instance, models.MapData)
            and "provider_state" in cleaned_data
            and cleaned_data["provider_state"] in models.MapData.ProviderState
        ):
            return cleaned_data

        provider_state = models.MapData.ProviderState(cleaned_data["provider_state"])
        provider_fields = self.instance.get_formfield_map()[provider_state]
        required_fieldnames = [field["name"] for field in provider_fields if field["required"]]
        print(f"Required fieldnames: {required_fieldnames}.")
        print(f"Cleaned data: {cleaned_data}.")
        for fieldname in required_fieldnames:
            if fieldname not in cleaned_data or not cleaned_data[fieldname]:
                self.add_error(fieldname, "This field is required.")

        return cleaned_data

    #     try:
    #         map_data = self._validate_map_data()
    #         provider = self._validate_provider()
    #         provider_instance = provider.get_instance(map_data)

    #         form_provider_type = models.ProviderType(cleaned_data['provider'])
    #         if provider != form_provider_type:
    #             # Switch to a new provider type if the form's type is different from the current instance type.
    #             provider.switch(map_data, form_provider_type)

    #     except models.NoMapDataProvider:
    #         # Create a new MapData Provider instance.
    #         provider_instance =

    #     try:
    #         provider_instance = self._validate_provider_instance()
    #     except ValueError:
    #         # There is no provider instance. We don't need to do any more cleaning.
    #         return cleaned_data

    #     form_provider = models.ProviderType(cleaned_data["provider"])
    #     for unused_field in self._get_unused_provider_fields(provider):
    #         # set unused fields (relative to the currently selected map data provider) to None
    #         cleaned_data[unused_field] = None

    #     if provider == models.ProviderType.GEOJSON:
    #         # TODO: Maybe validate GeoJson data?
    #         return cleaned_data

    #     elif provider == models.ProviderType.OPEN_GREEN_MAP:
    #         try:

    #             # update or create an open green maps provider
    #             if self.instance.ogm_provider:
    #                 ogm = self.instance.ogm_provider
    #                 ogm.map_link = self.cleaned_data["ogm_map_link"]
    #                 ogm.campaign_link = self.cleaned_data["ogm_campaign_link"]
    #             else:
    #                 ogm = models.OpenGreenMapProvider.objects.create(
    #                     map_link=self.cleaned_data["ogm_map_link"],
    #                     campaign_link=self.cleaned_data["ogm_campaign_link"],
    #                 )
    #             ogm.full_clean()
    #             cleaned_data["ogm_provider"] = ogm

    #             for fieldname in self.PROVIDER_FIELDS_MAP[provider]:
    #                 # pop subfields that are now a part of the ogm_provider model
    #                 cleaned_data.pop(fieldname)

    #         except forms.ValidationError as e:
    #             # Propagate field-specific errors
    #             for field, messages in e.message_dict.items():
    #                 self.add_error(f"ogm_{field}", ", ".join(messages))

    #     return cleaned_data

    # def save(self, commit=True) -> Any:
    #     if self.instance and self.instance.provider:
    #         if self.instance.provider == models.ProviderType.OPEN_GREEN_MAP:
    #             # Save OGM provider model onto this MapData instance
    #             self.instance.ogm_provider = self.cleaned_data["ogm_provider"]
    #     return super().save(commit)


@admin.register(models.MapData)
class MapDataAdmin(SimpleHistoryAdmin):
    form = MapDataAdminForm
    exclude = ["id"]
    list_display = ["name", "provider_state"]
    search_fields = ["name"]

    @staticmethod
    def _get_geojson(context) -> str:
        if map_data := context.get("original"):
            if isinstance(map_data, models.MapData):
                try:
                    return map_data.get_raw_geojson_data()
                except models.MapData.NoGeoJsonData:
                    pass
        return "{}"

    def render_change_form(self, request, context, *args, **kwargs):
        """
        Inject a map-preview and load the geojson data. If no geojson data could be provided,
        or we are creating a new map data object, this function injects an empty map-preview.
        """
        GEOJSON_FIELDNAME = "_geojson"
        geojson = self._get_geojson(context)
        try:
            map_preview_html = mark_safe(
                render_to_string(
                    template_name="admin/geojson_map_preview.html",
                    context={
                        GEOJSON_FIELDNAME: mark_safe(json.dumps(geojson)),
                        "height": "400px",
                        "change_element_id": "geojson-input",
                    },
                )
            )
            context["adminform"].form.fields[GEOJSON_FIELDNAME].help_text = map_preview_html
        except (KeyError, AttributeError):
            logger.exception(f"Failed to inject map preview.")
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

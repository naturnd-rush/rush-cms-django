import json
import logging
from dataclasses import asdict, dataclass
from typing import Any, List

import adminsortable2.admin as sortable_admin
from django import forms
from django.contrib import admin
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin
from silk.profiling.dynamic import silk_profile

from rush import models
from rush.admin import utils
from rush.admin.utils import truncate_admin_text_from
from rush.admin.widgets import SummernoteWidget

logger = logging.getLogger(__name__)


class StylesOnLayerInlineForm(forms.ModelForm):
    class Meta:
        model = models.StylesOnLayer
        fields = [
            "style",
            "feature_mapping",
            "legend_description",
            "popup",
        ]
        widgets = {
            "popup": SummernoteWidget(),
            "feature_mapping": forms.Textarea(attrs={"rows": 1, "cols": 50}),
        }


class StyleOnLayerInline(sortable_admin.SortableTabularInline, admin.TabularInline):
    form = StylesOnLayerInlineForm
    verbose_name_plural = "Styles applied to this Layer"
    model = models.StylesOnLayer
    extra = 0
    exclude = ["id"]
    sortable_field_name = "display_order"
    autocomplete_fields = [
        # uses the searchable textbox in the admin form to add/remove Styles
        "style"
    ]

    def get_formset(self, request, obj=None, **kwargs):
        """Profile inline formset creation"""
        return super().get_formset(request, obj, **kwargs)


class MapDataChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj) -> str:
        if obj and isinstance(obj, models.MapData):
            # Customize the MapData dropdown label without touching __str__
            return f"{obj.name} ({obj.provider_state.upper()})"
        return "Unknown Map Data"


class LayerForm(forms.ModelForm):

    class Meta:
        model = models.Layer
        exclude = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].widget = SummernoteWidget(height="300px")

    class LeafletSerializationFail(Exception):
        """
        Something went wrong while trying to serialize the leaflet
        JSON before saving it to the Layer model.
        """

        ...

    serialized_leaflet_json = forms.CharField(widget=forms.HiddenInput(), required=False)
    map_data = MapDataChoiceField(
        # Defer loading the large _geojson field to improve form rendering performance
        # Only load id, name, and provider_state which are needed for the dropdown
        queryset=models.MapData.objects.only(
            "id",
            "name",
            "provider_state",
        ).order_by("name")
    )

    @silk_profile(name="LayerForm clean_serialized_leaflet_json")
    def clean_serialized_leaflet_json(self):
        """
        Prevent double-serialization of submitted GeoJSON data.
        """
        try:
            map_data: models.MapData = self.cleaned_data["map_data"]
            if map_data.provider_state == models.MapData.ProviderState.GEOJSON:
                data = self.cleaned_data["serialized_leaflet_json"]
                # The json.loads here avoids double-serialization. We need it because
                # the data is serialized pre-transit to the server, and then again (mistakenly)
                # by Django's JSONField.
                return json.loads(data)
        except Exception as e:
            raise self.LeafletSerializationFail from e


@admin.register(models.Layer)
class LayerAdmin(sortable_admin.SortableAdminBase, SummernoteModelAdmin):  # type: ignore
    form = LayerForm
    inlines = [StyleOnLayerInline]
    autocomplete_fields = ["map_data"]
    search_fields = ["name"]
    list_display = ["name", "description_preview"]
    description_preview = truncate_admin_text_from("description")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # avoid fetching map_data when listing Layers
        return qs.defer("map_data", "serialized_leaflet_json")

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Handles both GET (load form) and POST (save form) requests"""
        # Dynamic profile name based on request method
        profile_name = f"LayerAdmin changeform_view ({request.method})"
        with silk_profile(name=profile_name):
            return super().changeform_view(request, object_id, form_url, extra_context)

    @silk_profile(name="LayerAdmin save_model")
    def save_model(self, request: HttpRequest, obj: Any, form: forms.ModelForm, change: bool) -> None:
        return super().save_model(request, obj, form, change)

    @silk_profile(name="LayerAdmin get_form")
    def get_form(self, request, obj=None, change=False, **kwargs):
        """Profile form instantiation"""
        return super().get_form(request, obj, change, **kwargs)

    @silk_profile(name="LayerAdmin render_change_form")
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

    @silk_profile(name="LayerAdmin save_formset")
    def save_formset(self, request, form, formset, change):
        """Profile saving inline formsets (StylesOnLayer)"""
        return super().save_formset(request, form, formset, change)

    @silk_profile(name="LayerAdmin get_inline_instances")
    def get_inline_instances(self, request, obj=None):
        """Profile loading inline forms"""
        return super().get_inline_instances(request, obj)


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
        MapDataAdminFormConfig.Provider(
            state=models.MapData.ProviderState.GEOTIFF,
            fields=[MapDataAdminFormConfig.Field("geotiff", required=True)],
            map_preview=False,
        ),
    ]
)


class MapDataAdminForm(forms.ModelForm):
    """
    For submitting `MapData` info.
    """

    # provider_state = forms.ChoiceField(choices=models.MapData.ProviderState.choices, label="Data Type")

    class Meta:
        model = models.MapData
        fields = ["id", "name", "provider_state", *[field.fieldname for field in mdaf_config.get_fields()]]
        labels = {
            "provider_state": "Data Type",
        }

    @silk_profile(name="MapDataForm get_initial_for_field")
    def get_initial_for_field(self, field, field_name):
        if field_name == "_geojson":
            if self.instance and isinstance(self.instance, models.MapData):
                if self.instance._geojson is None:
                    # Replace "null" in geojson form field with "{}"
                    return {}
        return super().get_initial_for_field(field, field_name)

    @silk_profile(name="MapDataForm __init__")
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

    @silk_profile(name="MapDataForm clean")
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
class MapDataAdmin(admin.ModelAdmin):
    form = MapDataAdminForm
    exclude = ["id"]
    list_display = ["name", "provider_state"]
    search_fields = ["name"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # avoid fetching map_data and geotiff data when listing all MapDatas
        return qs.defer("_geojson", "geotiff")

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Handles both GET (load form) and POST (save form) requests"""
        # Dynamic profile name based on request method
        profile_name = f"MapDataAdmin changeform_view ({request.method})"
        with silk_profile(name=profile_name):
            return super().changeform_view(request, object_id, form_url, extra_context)

    @silk_profile(name="MapDataAdmin save")
    def save_model(self, request: HttpRequest, obj: Any, form: forms.ModelForm, change: bool) -> None:
        return super().save_model(request, obj, form, change)

    @silk_profile(name="MapDataAdmin get_form")
    def get_form(self, request, obj=None, change=False, **kwargs):
        return super().get_form(request, obj, change, **kwargs)

    @silk_profile(name="MapDataAdmin log_change")
    def log_change(self, request, object, message):
        """
        Skip expensive change message for large JSON fields.
        """
        # Don't construct detailed change message, just log the action
        from django.contrib.admin.models import CHANGE, LogEntry
        from django.contrib.contenttypes.models import ContentType

        return LogEntry.objects.log_action(
            user_id=request.user.pk,  # type: ignore
            content_type_id=ContentType.objects.get_for_model(object).pk,
            object_id=object.pk,
            object_repr=str(object)[:200],
            action_flag=CHANGE,
            change_message="Modified",  # Simple message instead of detailed diff
        )

    @silk_profile(name="MapDataAdmin render_change_form")
    def render_change_form(self, request, context, *args, **kwargs):
        """
        Inject initial GeoJSON data into page so we can render an initial
        `MapData` preview in the change form.
        """
        geojson = None
        if map_data := context.get("original"):
            if isinstance(map_data, models.MapData):
                if raw_geojson := map_data.geojson:
                    geojson = raw_geojson
        geojson = "{}" if geojson is None else geojson
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
class StyleAdmin(admin.ModelAdmin):
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

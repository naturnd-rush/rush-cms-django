import json
import uuid
from decimal import Decimal, InvalidOperation
from typing import NamedTuple
from urllib.parse import parse_qs, urlparse

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.forms import ModelForm

from rush.admin.widgets import SummernoteWidget, TiledForeignKeyWidget
from rush.models import Icon, Layer, QuestionTab


class ShareLinkValues(NamedTuple):
    lat: Decimal
    lng: Decimal
    zoom: int | None
    layers: list[Layer] | None


class QuestionTabInlineForm(ModelForm):

    share_link = forms.CharField(
        required=False,
        help_text="Paste a share link from the website to fill out the zoom, latitude, longitude and layers.",
    )

    # Declared explicitly because the admin hides many-to-many fields with a custom through model.
    layers = forms.ModelMultipleChoiceField(
        queryset=Layer.objects.all(),
        required=False,
        widget=AutocompleteSelectMultiple(
            QuestionTab._meta.get_field("layers"), admin.site
        ),
        help_text=QuestionTab._meta.get_field("layers").help_text,
    )

    class Meta:
        model = QuestionTab
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        """
        Tiled foreign key widget needs to access the form, to get the request, so it can
        render thumbnails using the correct base-media-url.
        """
        super().__init__(*args, **kwargs)
        self.fields["icon"].widget = TiledForeignKeyWidget(
            display_choices=[
                TiledForeignKeyWidget.Choice(
                    id=str(icon.id),
                    thumbnail_url=icon.file.url,
                    instance=self.instance,
                    fk_name="icon",
                    request=getattr(self, "request"),
                )
                for icon in Icon.objects.order_by("-created_at")[:10]
            ],
        )
        self.fields["content"].widget = SummernoteWidget()

    def clean(self):
        """
        Fill out the map center, zoom and layers from the share link, if one was given.
        """
        cleaned_data = super().clean()
        share_link = cleaned_data.get("share_link")
        if share_link:
            values = self._parse_share_link(share_link)
            cleaned_data["center_lat"] = values.lat
            cleaned_data["center_long"] = values.lng
            if values.zoom is not None:
                cleaned_data["zoom"] = values.zoom
            if values.layers is not None:
                cleaned_data["layers"] = values.layers
        return cleaned_data

    def _parse_share_link(self, share_link: str) -> ShareLinkValues:
        """
        Parse the lat, lng, (optional) zoom, and (optional) active layers out of a share link, e.g.,
        https://whatstherush.earth/app/travel-light/notice?zoom=13&lat=48.408193&lng=-123.216991&activeLayers=%5B%22<uuid>%22%5D
        """
        params = parse_qs(urlparse(share_link.strip()).query)

        def first(key: str) -> str | None:
            return params.get(key, [None])[0]

        try:
            lat = Decimal(first("lat") or "").quantize(Decimal("0.000001"))
            lng = Decimal(first("lng") or "").quantize(Decimal("0.000001"))
        except InvalidOperation:
            raise forms.ValidationError(
                {"share_link": "Couldn't find a valid 'lat' and 'lng' in this link."}
            )
        if not (
            lat.is_finite()
            and lng.is_finite()
            and -90 <= lat <= 90
            and -180 <= lng <= 180
        ):
            raise forms.ValidationError(
                {"share_link": "The 'lat' or 'lng' in this link is out of range."}
            )

        zoom = None
        raw_zoom = first("zoom")
        if raw_zoom is not None:
            try:
                zoom = round(float(raw_zoom))
            except ValueError:
                raise forms.ValidationError(
                    {"share_link": "The 'zoom' in this link isn't a number."}
                )
            if not 0 <= zoom <= 23:
                raise forms.ValidationError(
                    {"share_link": "The 'zoom' in this link must be between 0 and 23."}
                )

        layers = None
        raw_layers = first("activeLayers")
        if raw_layers is not None:
            try:
                layer_ids = [uuid.UUID(x) for x in json.loads(raw_layers)]
            except (ValueError, TypeError, AttributeError):
                raise forms.ValidationError(
                    {
                        "share_link": "The 'activeLayers' in this link isn't a list of layer ids."
                    }
                )
            layers = list(Layer.objects.filter(id__in=layer_ids))
            missing = set(layer_ids) - {layer.id for layer in layers}
            if missing:
                raise forms.ValidationError(
                    {
                        "share_link": "These layers in the link don't exist: "
                        + ", ".join(sorted(str(x) for x in missing))
                    }
                )

        return ShareLinkValues(lat=lat, lng=lng, zoom=zoom, layers=layers)

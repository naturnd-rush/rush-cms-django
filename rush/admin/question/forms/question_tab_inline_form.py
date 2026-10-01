from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs, urlparse

from django import forms
from django.forms import ModelForm

from rush.admin.widgets import SummernoteWidget, TiledForeignKeyWidget
from rush.models import Icon, QuestionTab


class QuestionTabInlineForm(ModelForm):

    share_link = forms.CharField(
        required=False,
        help_text="Paste a share link from the website to fill out the zoom, latitude and longitude.",
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
        Fill out the map center and zoom from the share link, if one was given.
        """
        cleaned_data = super().clean()
        share_link = cleaned_data.get("share_link")
        if share_link:
            lat, lng, zoom = self._parse_share_link(share_link)
            cleaned_data["center_lat"] = lat
            cleaned_data["center_long"] = lng
            if zoom is not None:
                cleaned_data["zoom"] = zoom
        return cleaned_data

    def _parse_share_link(self, share_link: str) -> tuple[Decimal, Decimal, int | None]:
        """
        Parse the lat, lng, and (optional) zoom out of a share link, e.g.,
        https://whatstherush.earth/app/travel-light/notice?zoom=13&lat=48.408193&lng=-123.216991
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

        return lat, lng, zoom

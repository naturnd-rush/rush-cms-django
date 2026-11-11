import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from rush.models.utils import SummernoteTextCleaner


class StylesOnLayer(models.Model):
    """
    Through table for adding multiple Styles on a single Layer with the ability to
    reuse styles on other Layers.
    """

    MIN_ZOOM = 0
    MAX_ZOOM = 23

    class Meta:
        ordering = ["display_order"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)

    style = models.ForeignKey("Style", on_delete=models.CASCADE)
    layer = models.ForeignKey("Layer", on_delete=models.CASCADE)

    legend_description = models.CharField(
        max_length=255,
        default="E.g., 'Grassland', '0-25%', or '>3 Tree Protection Score'.",
        help_text="A short description of what this style represents on the map.",
    )
    legend_description_strict_clean = models.BooleanField(default=True)
    popup_strict_clean = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(
        default=0, blank=False, null=False, db_index=True, editable=True
    )

    # Some expression that will be matched against a GeoJSON feature's properties
    # to decide whether this style will be applied to any given feature on the map.
    # The default is True, which means this style will be applied to all Features by default!
    feature_mapping = models.TextField(default="true")

    # Optional HTML text field for describing what the popup template will be used
    popup = models.TextField(null=True, blank=True)
    popup_permanent = models.BooleanField(
        default=True,
        help_text="Keep this on if you want the popup to stay open while people click around outside of the popup.",
    )

    # The zoom range (inclusive) that this style is rendered at on the map.
    min_zoom = models.IntegerField(
        default=MIN_ZOOM,
        validators=[MinValueValidator(MIN_ZOOM), MaxValueValidator(MAX_ZOOM)],
        help_text="The lowest zoom level this style is drawn at. Defaults to 0 (fully zoomed out).",
    )
    max_zoom = models.IntegerField(
        default=MAX_ZOOM,
        validators=[MinValueValidator(MIN_ZOOM), MaxValueValidator(MAX_ZOOM)],
        help_text="The highest zoom level this style is drawn at. Defaults to 23 (fully zoomed in).",
    )

    def clean(self) -> None:
        if (
            self.min_zoom is not None
            and self.max_zoom is not None
            and self.min_zoom > self.max_zoom
        ):
            raise ValidationError(
                {"max_zoom": "Max zoom must be greater than or equal to min zoom."}
            )
        if self.popup:
            self.popup = SummernoteTextCleaner.clean(
                self.popup, strict_clean=self.popup_strict_clean
            )

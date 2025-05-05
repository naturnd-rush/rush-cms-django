import re
import uuid

import django.db.models as models
from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords

"""
Django models related to geographical data and styling.
"""


def validate_only_integers_and_whitespace(value):
    """
    Validates that the value contains only integers and whitespace.
    Examples of valid values: "1", "123", "12 34 56", " 7  8 9 "
    """
    if not re.fullmatch(r"[0-9\s]*", value):
        raise ValidationError("This field must contain only digits and whitespace.")


class LineCap(models.TextChoices):
    """
    The shape to be used at the end of the line.
    """

    BUTT = "butt"
    ROUND = "round"
    SQUARE = "square"


class LineJoin(models.TextChoices):
    """
    The shape to be used at the corners where lines meet.
    """

    ARCS = "arcs"
    BEVEL = "bevel"
    MITER = "miter"
    MITER_CLIP = "miter-clip"
    ROUND = "round"


class FillRule(models.TextChoices):
    """
    TODO: I'm not really sure what this does.
    https://developer.mozilla.org/en-US/docs/Web/CSS/fill-rule
    """

    NONZERO = "nonzero"
    EVENODD = "evenodd"


class Style(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255)
    draw_stroke = models.BooleanField(
        help_text="Check this box when you want to draw the line. Unchecking this box, for example, "
        + "will remove the borders from a polygon."
    )
    stroke_color = ColorField(default="#FFFFFF", verbose_name="Color")
    stroke_weight = models.DecimalField(
        max_digits=10, decimal_places=2, default=1, verbose_name="Thickness"
    )
    stroke_opacity = models.DecimalField(
        max_digits=5, decimal_places=3, default=1.00, verbose_name="Transparency"
    )
    stroke_line_cap = models.CharField(
        # See Mozilla docs: https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-linecap#usage_notes.
        max_length=32,
        choices=LineCap.choices,
        default=LineCap.ROUND,
        help_text="The shape of the end of a stroke. Options: butt, round, or square.",
    )
    stroke_line_join = models.CharField(
        # See Mozilla docs: https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-linejoin#usage_context.
        max_length=32,
        choices=LineJoin.choices,
        default=LineJoin.ROUND,
        help_text="The shape used to join two lines. Options: miter, round, or bevel.",
    )
    stroke_dash_array = models.CharField(
        # See Mozilla docs: https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-dasharray#example.
        max_length=32,
        validators=[validate_only_integers_and_whitespace],
        null=True,
        blank=True,
        help_text="The pattern of dashes and gaps for the outline, e.g., '5 5' for 5 pixel long lines "
        + "separated by 5 pixels of whiespace. Only digits and whitespace are allowed (e.g., '12 34 56')",
    )
    stroke_dash_offset = models.CharField(
        # See Mozilla docs: https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-dashoffset#example.
        max_length=32,
        null=True,
        blank=True,
        help_text="Offset where the dash pattern starts along the outline path.",
    )
    draw_fill = models.BooleanField(
        help_text="Check this box if you want to fill the polygon.",
        default=True,
    )
    fill_color = ColorField(
        default="#FFFFFF",
        null=True,
        blank=True,
    )
    fill_opacity = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=1.00,
        null=True,
        blank=True,
    )
    fill_rule = models.CharField(
        # Unused for now.
        max_length=32,
        choices=FillRule.choices,
        null=True,
        blank=True,
    )

    # marker_icon =
    # marker_icon_opacity =

    # TODO: Add _hover style and _active style recursive foreign keys.

    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Provider(models.TextChoices):
    GEOJSON = "geojson"
    OPEN_GREEN_MAP = "open_green_map"
    ESRI_FEATURE_SERVER = "esri_feature_server"  # TODO: Not sure how this gets implemented with the current MapData model
    GENERIC_REST = "generic_rest"  # TODO: Not sure how this gets implemented with the current MapData model


class MapData(models.Model):
    # TODO: Add on_create validation
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=255, choices=Provider.choices)
    geojson = models.JSONField(null=True, blank=True)

    # Open Green Map metadata
    ogm_map_id = models.CharField(max_length=1024, null=True, blank=True)
    feature_url_template = models.CharField(max_length=1024, null=True, blank=True)
    icon_url_template = models.CharField(max_length=1024, null=True, blank=True)
    image_url_template = models.CharField(max_length=1024, null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        # better plural name in the admin table list
        verbose_name_plural = "Map Data"


class Layer(models.Model):
    """
    MapData + Styling + Legend information combo.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    map_data = models.ForeignKey(
        to=MapData,
        # MapData deletion should fail if a Layer references it.
        on_delete=models.PROTECT,
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.name

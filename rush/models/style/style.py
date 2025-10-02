import uuid
from decimal import Decimal

import django.db.models as models
from colorfield.fields import ColorField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords

from rush.models import utils
from rush.models.base import BaseModel
from rush.models.validators import (
    validate_image_or_svg,
    validate_only_integers_and_whitespace,
)


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
    TODO: I'm not really sure what this does. It's currently omitted from the style form.
    https://developer.mozilla.org/en-US/docs/Web/CSS/fill-rule
    """

    NONZERO = "nonzero"
    EVENODD = "evenodd"


class Style(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    name = models.CharField(max_length=255)
    draw_stroke = models.BooleanField(
        help_text="Check this box when you want to draw the line. Unchecking this box, for example, "
        + "will remove the borders from a polygon."
    )
    stroke_color = ColorField(default="#FFFFFF", verbose_name="Color")
    stroke_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(1),
        verbose_name="Thickness",
    )
    stroke_opacity = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=Decimal(1),
        verbose_name="Transparency",
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
        help_text="The shape used to join two lines. Options: arcs, bevel, miter, miter clip, or round.",
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
        default=Decimal(1),
        null=True,
        blank=True,
    )
    fill_rule = models.CharField(
        # Unused in the admin form for now.
        max_length=32,
        choices=FillRule.choices,
        null=True,
        blank=True,
    )
    draw_marker = models.BooleanField(
        help_text="Check this box if you want to draw the marker icon on each point this style is applied to.",
        default=True,
    )
    marker_icon = models.FileField(
        upload_to="marker_icons/",
        null=True,
        blank=True,
        validators=[validate_image_or_svg],
        help_text="The image that will appear at each point this style is applied to. Accepts PNG, JPEG, and SVG files.",
    )
    marker_icon_opacity = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=Decimal(1),
        null=True,
        blank=True,
    )
    marker_background_color = ColorField(
        default="#F2F2F2",
        null=True,
        blank=True,
        verbose_name="Background Color",
    )

    # TODO: Add _hover style and _active style recursive foreign keys.

    history = HistoricalRecords()

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Style)
def compress_marker_icon(sender, instance: Style, **kwargs):
    if image := instance.marker_icon:
        try:
            compressed = utils.compress_image(image)
            # save = False avoids double-saving for efficiency and just
            # assigns the compressed image value to the marker_icon field
            image.save(compressed.name, compressed, save=False)
        except utils.CompressionFailed:
            pass

from io import BytesIO
from logging import getLogger

import bleach
import bleach.css_sanitizer
from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile
from PIL import Image

from rush.models.validators import FiletypeValidator

logger = getLogger(__name__)


class CompressionFailed(Exception):
    """
    Compressing the image failed.
    """

    ...


def compress_image(image: FieldFile, pixel_width=128) -> ContentFile:
    """
    Compress and resize the given image and return it as a ContentFile.
    The returned ContentFile can be manually assigned to a model's FieldFile.
    """

    try:

        FiletypeValidator(
            valid_names=[
                "WEBP",
                "JPEG",
                "PNG",
                # NOTE: SVGs/TIFFs should not be compressed
            ]
        )(image)

        # Resize image
        img = Image.open(image)
        original_width, original_height = img.size
        pixel_width = min(original_width, pixel_width)
        w_ratio = pixel_width / original_width
        new_height = int(original_height * w_ratio)
        img = img.resize((pixel_width, new_height), Image.Resampling.LANCZOS)

        # Save to in-memory buffer
        img_io = BytesIO()
        img.save(
            img_io,
            format="WEBP",
            lossless=False,
            quality=90,  # 85-95 is visually lossless for most images
            method=6,  # 0-6, where 6 is the most compressed but takes longer
        )

        original_name = image.name
        compressed_name = f"compressed_{original_name.split('/')[-1].rsplit('.', 1)[0]}.webp"

        # Return a ContentFile with name
        return ContentFile(img_io.getvalue(), name=compressed_name)

    except Exception as e:
        logger.error(f"Failed to compress file: {image.name}.")
        raise CompressionFailed from e


class SummernoteTextCleaner:
    """
    Responsible for sanitizing summernote TextField data before it
    gets saved to the database.
    """

    ALLOWED_TAGS = [
        "p",
        "ul",
        "ol",
        "li",
        "strong",
        "em",
        "div",
        "span",
        "a",
        "blockquote",
        "pre",
        "figure",
        "figcaption",
        "br",
        "code",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "picture",
        "source",
        "img",
        "del",
        "b",
        "i",
        "button",
        "input",
        "font",
    ]

    ALLOWED_ATTRIBUTES = [
        "alt",
        "class",
        "src",
        "srcset",
        "href",
        "media",
        "style",
        "align",
    ]

    # Which CSS properties are allowed in 'style' attributes (assuming style is
    # an allowed attribute)
    BLEACH_ALLOWED_STYLES = [
        "width",
        "height",
        "max-width",
        "max-height",
        "min-width",
        "min-height",
        "font-family",
        "font-weight",
        "font-size",
        "background-color",
        "color",
    ]

    @classmethod
    def clean(cls, text: str) -> str:
        unescaped = text.replace("&quot;", "'")
        cleaned = bleach.clean(
            text=unescaped,
            attributes=cls.ALLOWED_ATTRIBUTES,
            tags=cls.ALLOWED_TAGS,
            css_sanitizer=bleach.css_sanitizer.CSSSanitizer(
                allowed_css_properties=cls.BLEACH_ALLOWED_STYLES,
            ),
        )
        return cleaned

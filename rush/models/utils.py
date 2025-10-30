from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile
from PIL import Image

from rush.models.validators import BaseInvalidFileType, validate_image_webp


class CompressionFailed(Exception):
    """
    Compressing the image failed.
    """

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def compress_image(image: FieldFile, pixel_width=128) -> ContentFile:
    """
    Compress and resize the given image and return it as a ContentFile.
    The returned ContentFile can be manually assigned to a model's FieldFile.
    """

    try:
        validate_image_webp(image)
    except BaseInvalidFileType as e:
        raise CompressionFailed(reason=e.message_str) from e

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

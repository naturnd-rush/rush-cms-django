import mimetypes

from django.core.exceptions import ValidationError


def validate_image_or_svg(file):
    """
    Raise a validation-error if then file isn't a PNG, JPEG, or SVG.
    """
    mime_type, _ = mimetypes.guess_type(file.name)
    if mime_type not in ["image/png", "image/jpeg", "image/svg+xml"]:
        raise ValidationError(
            f"Unsupported file type '{mime_type}'. Please upload PNG, JPEG, or SVG."
        )


def validate_image(file):
    """
    Raise a validation-error if then file isn't a PNG or JPEG.
    """
    mime_type, _ = mimetypes.guess_type(file.name)
    if mime_type not in ["image/png", "image/jpeg"]:
        raise ValidationError(
            f"Unsupported file type '{mime_type}'. Please upload PNG or JPEG."
        )

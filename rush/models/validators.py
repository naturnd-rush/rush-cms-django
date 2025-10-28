import re

from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile

from rush.models import MimeType


class UnsupportedFileType(ValidationError):
    """
    The file type is not supported.
    """

    def __init__(
        self,
        filename: str,
        offending_type: MimeType,
        *supported_types: MimeType,
        **kwargs,
    ):
        msg = 'Unsupported file type "{}" from "{}". Please upload one of: {}.'.format(
            offending_type.human_name,
            filename,
            ", ".join([x.human_name for x in supported_types]),
        )
        self.message_str = msg
        super().__init__(message=msg, **kwargs)


def _validate_mimetypes(file: FieldFile, *allowed_mimetypes: MimeType) -> None:
    """
    Raise a validation-error if the file's extension isn't in the provided list of mimetypes.
    """
    mimetype = MimeType.guess_type(file.name)
    if mimetype == MimeType.UNKNOWN() or mimetype not in allowed_mimetypes:
        raise UnsupportedFileType(file.name, mimetype, *allowed_mimetypes)


def validate_image_or_svg(file: FieldFile):
    """
    Raise a validation-error if then file isn't a PNG, JPEG, or SVG.
    """
    _validate_mimetypes(
        file,
        MimeType.PNG(),
        MimeType.JPEG(),
        MimeType.SVG(),
    )


def validate_image(file: FieldFile):
    """
    Raise a validation-error if then file isn't a PNG or JPEG.
    """
    _validate_mimetypes(
        file,
        MimeType.PNG(),
        MimeType.JPEG(),
    )


def validate_svg(file: FieldFile):
    """
    Raise a validation-error if then file isn't an SVG file.
    """
    return _validate_mimetypes(
        file,
        MimeType.SVG(),
    )


def validate_tiff(file: FieldFile):
    """
    Raise a validation-error if then file isn't a TIFF file (https://en.wikipedia.org/wiki/TIFF).
    """
    return _validate_mimetypes(
        file,
        MimeType.TIFF(),
    )


def validate_only_integers_and_whitespace(value):
    """
    Validates that the value contains only integers and whitespace.
    Examples of valid values: "1", "123", "12 34 56", " 7  8 9 "
    """
    if not re.fullmatch(r"[0-9\s]*", value):
        raise ValidationError("This field must contain only digits and whitespace.")

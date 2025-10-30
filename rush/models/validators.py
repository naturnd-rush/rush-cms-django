import mimetypes
import re

from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile


class BaseInvalidFileType(ValidationError):
    """
    The file type is invalid and cannot be used.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    @property
    def message_str(self) -> str:
        # to fix typing issue while subclassing ValidationError
        return str(self.message)


class UnsupportedFileType(BaseInvalidFileType):
    """
    The file type is known, but not supported.
    """

    def __init__(
        self,
        offending_type: str,
        supported_types: list[str],
        *args,
        **kwargs,
    ):
        self.offending_type = offending_type
        self.supported_types = supported_types
        # Build a user-friendly message listing supported mime types.
        supported_list = ", ".join(f'"{x}"' for x in supported_types)
        msg = 'Unsupported file type "{}". Please upload one of: {}.'.format(offending_type, supported_list)
        super().__init__(message=msg, *args, **kwargs)


class UnknownFileType(BaseInvalidFileType):
    """
    The file type is unknown, and therefore invalid.
    """

    def __init__(self, file_name: str, *args, **kwargs):
        self.file_name = file_name
        msg = f'Unknown file type: ".{file_name.split(".")[-1]}".'
        super().__init__(message=msg, *args, **kwargs)


def validate_image_svg_webp(file: FieldFile):
    """
    Raise a validation-error if then file isn't a PNG, JPEG, SVG, or WEBP.
    """
    allowed = ["image/png", "image/jpeg", "image/svg+xml", "image/webp"]
    mime_type, _ = mimetypes.guess_type(file.name)
    if not mime_type:
        raise UnknownFileType(file.name)
    if mime_type not in allowed:
        raise UnsupportedFileType(mime_type, allowed)


def validate_image_webp(file: FieldFile):
    """
    Raise a validation-error if then file isn't a PNG, JPEG, or WEBP.
    """
    allowed = ["image/png", "image/jpeg", "image/webp"]
    mime_type, _ = mimetypes.guess_type(file.name)
    if not mime_type:
        raise UnknownFileType(file.name)
    if mime_type not in allowed:
        raise UnsupportedFileType(mime_type, allowed)


def validate_tiff(file: FieldFile):
    """
    Raise a validation-error if then file isn't a TIFF file (https://en.wikipedia.org/wiki/TIFF).
    """
    allowed = ["image/tiff", "image/tiff-fx"]
    mime_type, _ = mimetypes.guess_type(file.name)
    if not mime_type:
        raise UnknownFileType(file.name)
    if mime_type not in allowed:
        raise UnsupportedFileType(mime_type, allowed)


def validate_only_integers_and_whitespace(value):
    """
    Validates that the value contains only integers and whitespace.
    Examples of valid values: "1", "123", "12 34 56", " 7  8 9 "
    """
    if not re.fullmatch(r"[0-9\s]*", value):
        raise ValidationError("This field must contain only digits and whitespace.")

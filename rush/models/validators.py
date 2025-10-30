import re
from typing import List

from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile

from rush.models import MimeType


def validate_filetype(
    valid: List[MimeType] | None = None,
    invalid: List[MimeType] | None = None,
):
    """
    Return a django-validator for a file-field that raises a validation-error if the
    file's guessed mimetype is not a member of `valid`, or is a member of `invalid`.
    """

    def _validate(file: FieldFile):
        MimeType.guess(file.name).validate(valid, invalid)

    return _validate


def validate_only_integers_and_whitespace(value):
    """
    Validates that the value contains only integers and whitespace.
    Examples of valid values: "1", "123", "12 34 56", " 7  8 9 "
    """
    if not re.fullmatch(r"[0-9\s]*", value):
        raise ValidationError("This field must contain only digits and whitespace.")

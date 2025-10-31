import re
from typing import List

from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile

from rush.models import MimeType


class FiletypeValidator:
    """
    Args:
        valid_names: List of human-readable mimetype names that are allowed.
        invalid_names: List of human-readable mimetype names that are not allowed.
    """

    def __init__(
        self,
        valid_names: List[str] | None = None,
        invalid_names: List[str] | None = None,
    ):
        self.valid_names = valid_names
        self.invalid_names = invalid_names

    def __call__(self, file: FieldFile):
        # Resolve names to MimeType instances at runtime
        valid_types = None
        invalid_types = None

        if self.valid_names:
            valid_types = [MimeType.by_name(name) for name in self.valid_names]

        if self.invalid_names:
            invalid_types = [MimeType.by_name(name) for name in self.invalid_names]

        # Use existing validation logic
        MimeType.guess(file.name).validate(valid_types, invalid_types)

    def __eq__(self, other):
        return (
            isinstance(other, FiletypeValidator)
            and self.valid_names == other.valid_names
            and self.invalid_names == other.invalid_names
        )

    def deconstruct(self):
        """Required for migration serialization."""
        return (
            "rush.models.validators.FiletypeValidator",
            [],
            {"valid_names": self.valid_names, "invalid_names": self.invalid_names},
        )


def validate_only_integers_and_whitespace(value):
    """
    Validates that the value contains only integers and whitespace.
    Examples of valid values: "1", "123", "12 34 56", " 7  8 9 "
    """
    if not re.fullmatch(r"[0-9\s]*", value):
        raise ValidationError("This field must contain only digits and whitespace.")

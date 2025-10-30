from typing import Callable
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError

from rush.models import GuessedMimeType, MimeType
from rush.models.validators import *
from rush.tests.models.helpers import FakeFile


def valid_file(
    name: str,
    valid=None,
    invalid=None,
) -> tuple[Mock, bool, str, List[MimeType] | None, List[MimeType] | None]:
    valid = [] if valid is None else valid
    invalid = [] if invalid is None else invalid
    return (FakeFile(name), False, "", valid, invalid)


def invalid_file(
    name: str,
    err_msg: str,
    valid=None,
    invalid=None,
) -> tuple[Mock, bool, str, List[MimeType] | None, List[MimeType] | None]:
    valid = [] if valid is None else valid
    invalid = [] if invalid is None else invalid
    return (FakeFile(name), True, err_msg, valid, invalid)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file, raises, err_msg, valid, invalid",
    [
        valid_file("test.svg", valid=[MimeType.SVG]),
        valid_file("test.SVG", valid=[MimeType.SVG]),
        valid_file("test.svg", valid=[MimeType.SVG, MimeType.TIFF]),
        invalid_file(
            "test.html5",
            "The mimetype of file 'test.html5' could not be parsed",
        ),
        invalid_file(
            "test.html",
            "The mimetype of file 'test.html' is currently not supported",
        ),
        invalid_file(
            "test.svg",
            "The mimetype SVG is invalid",
            valid=[MimeType.TIFF],
        ),
        invalid_file(
            "test.svg",
            "The mimetype SVG is invalid",
            valid=[],
        ),
        invalid_file(
            "test.svg",
            "The mimetype SVG is invalid",
            valid=[MimeType.SVG],
            invalid=[MimeType.SVG],
        ),
    ],
)
def test_validate_filetype(
    file: Mock,
    raises: bool,
    err_msg: str,
    valid: List[Callable[[], MimeType]],
    invalid: List[Callable[[], MimeType]],
):
    """
    PNG, JPEG, and SVG all allowed.
    """
    fn = validate_filetype([x() for x in valid], [x() for x in invalid])
    if raises:
        with pytest.raises(GuessedMimeType.BaseValidationError, match=err_msg):
            fn(file)
    else:
        # Shouldn't raise
        fn(file)


@pytest.mark.parametrize(
    "value, raises",
    [
        ("123", False),
        ("  123", False),
        ("123  ", False),
        (" 1 2   3 ", False),
        ("123\n", False),  # newline is whitespace
        ("123\r", False),  # carriage return is whitespace
        ("123298312931   273234234234234", False),
        ("123.", True),
        ("a123", True),
        ("0a8ue98qy3r", True),
    ],
)
def test_validate_only_integers_and_whitespace(value: str, raises: bool):
    """
    Only digits and whitespace allowed.
    """
    if raises:
        msg = "This field must contain only digits and whitespace."
        with pytest.raises(ValidationError, match=msg):
            validate_only_integers_and_whitespace(value)
    else:
        validate_only_integers_and_whitespace(value)

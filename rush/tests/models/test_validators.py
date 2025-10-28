from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError

from rush.models.validators import *
from rush.tests.models.helpers import FakeFile


def valid_file(name: str) -> tuple[Mock, bool, str]:
    return (FakeFile(name), False, "")


def invalid_file(name: str, err_msg: str) -> tuple[Mock, bool, str]:
    return (FakeFile(name), True, err_msg)


def image_test_params():
    return [
        # Test lower-case file types
        valid_file("test.png"),
        valid_file("test.jpg"),
        valid_file("test.jpeg"),
        # Test upper-case file types
        valid_file("test.PNG"),
        valid_file("test.JPG"),
        valid_file("test.JPEG"),
        # Test bogus file types, and mime types we haven't added yet.
        invalid_file(
            "test.html",
            'Unsupported file type "UNKNOWN" from "test.html". Please upload one of: PNG, JPEG.',
        ),
        invalid_file(
            "test.css",
            'Unsupported file type "UNKNOWN" from "test.css". Please upload one of: PNG, JPEG.',
        ),
        invalid_file(
            "test.html5",
            'Unsupported file type "UNKNOWN" from "test.html5". Please upload one of: PNG, JPEG.',
        ),
    ]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file, raises, err_msg",
    [*image_test_params(), valid_file("test.svg"), valid_file("test.SVG")],
)
def test_validate_image_or_svg(file: Mock, raises: bool, err_msg: str):
    """
    PNG, JPEG, and SVG all allowed.
    """
    if raises:
        with pytest.raises(UnsupportedFileType, match=err_msg):
            validate_image_or_svg(file)
    else:
        validate_image_or_svg(file)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file, raises, err_msg",
    [
        *image_test_params(),
        invalid_file("test.svg", 'Unsupported file type "SVG" from "test.svg". Please upload one of: PNG, JPEG.'),
        invalid_file("test.SVG", 'Unsupported file type "SVG" from "test.SVG". Please upload one of: PNG, JPEG.'),
    ],
)
def test_validate_image(file: Mock, raises: bool, err_msg: str):
    """
    Should raise validation error when mimetype is not PNG, JPEG.
    """
    if raises:
        with pytest.raises(UnsupportedFileType, match=err_msg):
            validate_image(file)
    else:
        validate_image(file)


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

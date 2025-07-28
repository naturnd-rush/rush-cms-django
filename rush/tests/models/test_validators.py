import pytest
from django.core.exceptions import ValidationError

import rush.models.validators as validators


class FakeFile:
    """
    A fake file for testing purposes.
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'<FakeFile: "{self.name}">'


@pytest.mark.parametrize(
    "file, raises, err_msg",
    [
        (FakeFile("test.png"), False, ""),
        (FakeFile("test.jpg"), False, ""),
        (FakeFile("test.jpeg"), False, ""),
        (FakeFile("test.PNG"), False, ""),
        (FakeFile("test.JPG"), False, ""),
        (FakeFile("test.JPEG"), False, ""),
        (FakeFile("test.html"), True, "Unsupported file type 'text/html'"),
        (FakeFile("test.css"), True, "Unsupported file type 'text/css'"),
        # SVGs allowed
        (FakeFile("test.svg"), False, ""),
        (FakeFile("test.SVG"), False, ""),
    ],
)
def test_validate_image_or_svg(file: FakeFile, raises: bool, err_msg: str):
    """
    Should raise validation error when mimetype is not PNG, JPEG, or SVG.
    """
    if raises:
        with pytest.raises(ValidationError, match=err_msg):
            validators.validate_image_or_svg(file)
    else:
        validators.validate_image_or_svg(file)


@pytest.mark.parametrize(
    "file, raises, err_msg",
    [
        (FakeFile("test.png"), False, ""),
        (FakeFile("test.jpg"), False, ""),
        (FakeFile("test.jpeg"), False, ""),
        (FakeFile("test.PNG"), False, ""),
        (FakeFile("test.JPG"), False, ""),
        (FakeFile("test.JPEG"), False, ""),
        (FakeFile("test.html"), True, "Unsupported file type 'text/html'"),
        (FakeFile("test.css"), True, "Unsupported file type 'text/css'"),
        # SVGs not allowed
        (FakeFile("test.svg"), True, "Unsupported file type 'image/svg"),
        (FakeFile("test.SVG"), True, "Unsupported file type 'image/svg"),
    ],
)
def test_validate_image(file: FakeFile, raises: bool, err_msg: str):
    """
    Should raise validation error when mimetype is not PNG, JPEG.
    """
    if raises:
        with pytest.raises(ValidationError, match=err_msg):
            validators.validate_image(file)
    else:
        validators.validate_image(file)

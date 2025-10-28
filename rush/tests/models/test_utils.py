from unittest.mock import MagicMock, patch

import pytest

from rush.models.utils import *
from rush.tests.models.helpers import FakeFile


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file, raises, err_msg",
    [
        (
            FakeFile("not_an_image.zyx"),
            True,
            'Unsupported file type "UNKNOWN" from "not_an_image.zyx". Please upload one of: PNG, JPEG.',
        ),
        (
            FakeFile("not_an_image.svg"),
            True,
            'Unsupported file type "SVG" from "not_an_image.svg". Please upload one of: PNG, JPEG.',
        ),
        (FakeFile("image.png"), False, ""),
        (FakeFile("image.jpg"), False, ""),
        (FakeFile("image.jpeg"), False, ""),
    ],
)
def test_compress_image(file, raises, err_msg):

    with patch("rush.models.utils.Image.open") as mock_open:

        # Mock a PIL Image instance
        mock_image = MagicMock()
        mock_image.size = (1024, 768)
        mock_open.return_value = mock_image

        if raises:
            with pytest.raises(CompressionFailed, match=err_msg):
                compress_image(file)
        else:
            output = compress_image(file)
            assert isinstance(output, ContentFile)
            assert output.name.startswith("compressed_")
            assert output.name.endswith(".png")  # always gets compressed as PNG

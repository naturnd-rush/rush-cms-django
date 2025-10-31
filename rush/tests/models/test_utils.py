from unittest.mock import MagicMock, patch

import pytest

from rush.models.utils import *
from rush.tests.models.helpers import FakeFile


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file, raises",
    [
        (FakeFile("image.png"), False),
        (FakeFile("image.jpg"), False),
        (FakeFile("image.jpeg"), False),
        (FakeFile("image.webp"), False),
        (FakeFile("not_an_image.zyx"), True),
        (FakeFile("not_an_image.svg"), True),
        (FakeFile("not_an_image.tiff"), True),
    ],
)
def test_compress_image(file, raises):

    with patch("rush.models.utils.Image.open") as mock_open:

        # Mock a PIL Image instance
        mock_image = MagicMock()
        mock_image.size = (1024, 768)
        mock_open.return_value = mock_image

        if raises:
            with pytest.raises(CompressionFailed):
                compress_image(file)
        else:
            output = compress_image(file)
            assert isinstance(output, ContentFile)
            assert output.name.startswith("compressed_")
            assert output.name.endswith(".webp")  # always gets compressed as WEBP

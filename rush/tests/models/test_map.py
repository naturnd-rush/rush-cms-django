import io
import os
from typing import Any

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from rush.models.map import *
from rush.tests.models.helpers import use_tmp_media_dir


def get_test_image(name: str, size=(100, 100), color=(255, 0, 0)) -> SimpleUploadedFile:
    ext = name.split(".")[-1].lower()
    if ext.lower() == "jpg":
        ext = "jpeg"
    image_bytes = io.BytesIO()
    image = Image.new("RGB", size, color)
    image.save(image_bytes, format=ext)
    image_bytes.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=image_bytes.read(),
        content_type=f"image/{ext}",
    )


def get_test_svg(name: str) -> SimpleUploadedFile:
    svg_content = b"""<?xml version="1.0"?>
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
      <rect width="100" height="100" style="fill:rgb(0,0,255);" />
    </svg>"""
    return SimpleUploadedFile(name, svg_content, content_type="image/svg+xml")


def create_style_kwargs() -> dict[str, Any]:
    return {
        "draw_stroke": True,
        "draw_fill": True,
        "draw_marker": True,
    }


@use_tmp_media_dir
@pytest.mark.django_db
@pytest.mark.parametrize(
    "image, save_name",
    [
        (get_test_image("test_image.png"), "compressed_test_image.png"),
        (get_test_image("test_image.jpg"), "compressed_test_image.png"),
        (get_test_image("test_image.jpeg"), "compressed_test_image.png"),
    ],
)
def test_create_style_compresses_marker_icon_images(image, save_name: str):
    kwargs = create_style_kwargs() | {"marker_icon": image}
    style = Style.objects.create(**kwargs)

    assert os.path.exists(style.marker_icon.path)
    assert style.marker_icon.name.endswith(save_name)
    assert style.marker_icon.size < image.size


@use_tmp_media_dir
@pytest.mark.django_db
def test_create_style_does_not_compress_marker_icon_svgs():

    svg = get_test_svg("test_image.svg")
    kwargs = create_style_kwargs() | {"marker_icon": svg}
    style = Style.objects.create(**kwargs)

    assert os.path.exists(style.marker_icon.path)
    assert style.marker_icon.name.endswith("test_image.svg")
    assert style.marker_icon.size == svg.size  # no compression

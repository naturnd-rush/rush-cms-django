from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile
from PIL import Image

from rush.models.validators import InvalidFileType, validate_image


class CompressionFailed(Exception):
    """
    Compressing the image failed.
    """

    ...


def compress_image(image: FieldFile) -> FieldFile:

    try:
        validate_image(image)
    except UnsupportedFileType as e:
        raise CompressionFailed from e

    # open image and resize
    BASE_WIDTH = int(256)  # pixels
    img = Image.open(self.marker_icon)
    print(f"Image: {img.__dict__}")
    original_width, original_height = img.size
    w_ratio = BASE_WIDTH / original_width
    img = img.resize(
        (BASE_WIDTH, int(original_height * w_ratio)),
        Image.Resampling.LANCZOS,
    )

    # save compressed version image using buffer
    img_io = BytesIO()
    img.save(img_io, format="PNG", optimize=True, compress_level=9)
    # TODO: Fix this code, it doesnt nest the folders anymore but it saves the high resversion alongside
    # the optimized version which is unecessary...

    # Replace the image file with the compressed version
    img_content = ContentFile(img_io.getvalue(), name=self.marker_icon.name)
    name_without_path = self.marker_icon.name.split(self.MARKER_ICON_UPLOAD_TO)[1]
    self.marker_icon.save(name_without_path, img_content, save=False)

    # Save the model again to store the compressed image
    # super().save()

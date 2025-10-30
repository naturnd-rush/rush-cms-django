import uuid

from django.db import models

from rush.models import MimeType
from rush.models.validators import FiletypeValidator


class Icon(models.Model):
    """
    An SVG, PNG, WEBP, or JPEG icon.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    mime_type = models.ForeignKey(to=MimeType, on_delete=models.DO_NOTHING)
    file = models.FileField(
        upload_to="icons/",
        validators=[FiletypeValidator(valid_names=["PNG", "JPEG", "SVG", "WEBP"])],
    )

    def clean_file(self):
        if not self.mime_type:
            # Inject mime-type of the icon before saving
            self.mime_type = MimeType.guess(self.file.name).guessed

    def __str__(self):
        return "{}-{}".format(
            self.mime_type.human_name,
            self.file.name,
        )

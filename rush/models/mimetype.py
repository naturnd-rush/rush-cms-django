import mimetypes
from typing import List

from django.db import models


class MimeType(models.Model):
    """
    The media type of a file, see: https://en.wikipedia.org/wiki/Media_type.
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["_values"],
                condition=models.Q(is_valid=True),
                name="unique_mimetype_value_when_valid",
            ),
        ]

    human_name = models.CharField(max_length=255)
    _values = models.CharField(max_length=255)
    is_valid = models.BooleanField(default=True)

    @property
    def values(self) -> List[str]:
        vals = self._values.split(",")
        return [x.strip() for x in vals]

    @classmethod
    def SVG(cls) -> "MimeType":
        return cls.objects.get(human_name="SVG")

    @classmethod
    def PNG(cls) -> "MimeType":
        return cls.objects.get(human_name="PNG")

    @classmethod
    def JPEG(cls) -> "MimeType":
        return cls.objects.get(human_name="JPEG")

    @classmethod
    def TIFF(cls) -> "MimeType":
        return cls.objects.get(human_name="TIFF")

    @classmethod
    def UNKNOWN(cls) -> "MimeType":
        return cls.objects.get(human_name="UNKNOWN")

    @classmethod
    def UNSUPPORTED(cls) -> "MimeType":
        return cls.objects.get(human_name="UNSUPPORTED")

    @classmethod
    def guess_type(cls, filename: str) -> "MimeType":
        """
        Guess the mime-type based on a file name.
        """
        mime_type_value, encoding = mimetypes.guess_type(filename)
        if not mime_type_value:
            return cls.UNKNOWN()
        try:
            return cls.objects.get(_values__contains=mime_type_value)
        except MimeType.DoesNotExist:
            return cls.UNKNOWN()

    def __str__(self):
        return "{}-{}".format(
            self.human_name,
            self.values,
        )

import uuid

from django.core.validators import URLValidator
from django.db.models import (
    CASCADE,
    CharField,
    FileField,
    ForeignKey,
    Model,
    TextChoices,
    UUIDField,
)
from django.db.models.signals import post_save
from django.dispatch import receiver

from rush.models.validators import FiletypeValidator


class UploadState(TextChoices):
    """
    Whether the file is pending upload, in the process of being uploaded, or has finished uploading.
    """

    PENDING = "pending_upload"
    UPLOADING = "uploading"
    DONE = "finished_uploading"


class S3File(Model):
    """
    A file that exists in some S3-compatible cloud storage bucket. All uploads happen locally
    at first, and then asynchronously to the cloud, after which the local file is deleted.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4, null=False)

    s3_client = ForeignKey(to="S3Client", on_delete=CASCADE)
    bucket_name = CharField(max_length=255)
    upload_url = CharField(max_length=2048, null=True, blank=True, validators=[URLValidator()])

    local_file = FileField(null=True, blank=True, validators=[FiletypeValidator(valid_names=["TIFF"])])
    state = CharField(max_length=255, choices=UploadState.choices, default=UploadState.PENDING)


# @receiver(post_save, sender=S3File)
# def trigger_async_upload(sender, instance: S3File, **kwargs):
#     # Upload file
#     s3_client.upload_file(
#         "/home/dodo/Documents/github/rush-cms-django-prototype/.django_dev/media/marker_icons/Bananas-218094b-scaled-2492773212_EAlgIXu.jpg",
#         settings.BACKBLAZE_RASTER_BUCKET_NAME,
#         "Bananas-218094b-scaled-2492773212_EAlgIXu.jpg",
#     )(max_length=255, choices=UploadState.choices, default=UploadState.PENDING)


# url = f"https://{bucket_name}.s3.{region}.backblazeb2.com/{key}"

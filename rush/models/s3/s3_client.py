import uuid

import boto3
from botocore.config import Config
from django.conf import settings
from django.core.validators import URLValidator
from django.db.models import CharField, FileField, Model, TextChoices, UUIDField
from django.utils.functional import cached_property

from rush.models.s3.s3_file import S3File, UploadState
from rush.models.validators import FiletypeValidator


class UploadFileResult(TextChoices):
    FILE_NOT_PENDING_UPLOAD = "expected_s3_file_to_be_in_pending_state"
    SUCCESS = "SUCCESS"


class S3Client(Model):
    """
    A S3 storage bucket.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    human_name = CharField(max_length=255)
    endpoint_url = CharField(max_length=2048)
    key_id = CharField(max_length=255)
    key_secret = CharField(max_length=255)

    @cached_property
    def _connection(self):
        # TODO: Create a test connection here that redirects to just saving files in a folder locally
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.key_secret,
            config=Config(signature_version="s3v4"),
        )

    def upload_file(self, file: S3File) -> UploadFileResult:
        """
        Upload a file to storage.
        """
        if UploadState(file.state) != UploadState.PENDING:
            return UploadFileResult.FILE_NOT_PENDING_UPLOAD
        if not file.local_file.path:
            raise ValueError(f"File {file.id} not found for upload.")
        self._connection.upload_file(file.local_file.path, file.bucket_name, file.local_file.name)
        return UploadFileResult.SUCCESS

        # return boto3.client(
        #     "s3",
        #     endpoint_url=settings.BACKBLAZE_ENDPOINT_URL,
        #     aws_access_key_id=settings.BACKBLAZE_APP_KEY_ID,
        #     aws_secret_access_key=settings.BACKBLAZE_APP_KEY,
        #     config=Config(signature_version="s3v4"),
        # )

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.core.config import get_settings


PLACEHOLDER_VALUES = {
    "",
    "your_storage_account_name_here",
    "your_storage_account_key_here",
}


@dataclass
class BlobUploadResult:
    blob_name: str
    blob_url: str


class AzureBlobService:
    def __init__(self):
        settings = get_settings()
        connection_string = settings.AZURE_STORAGE_CONNECTION_STRING

        self.container_name = (
            settings.AZURE_STORAGE_CONTAINER_NAME
            or settings.AZURE_BLOB_CONTAINER_NAME
        )

        if connection_string is not None:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                connection_string.get_secret_value()
            )
        else:
            account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
            account_key = settings.AZURE_STORAGE_ACCOUNT_KEY

            if not account_name or account_name in PLACEHOLDER_VALUES:
                raise RuntimeError(
                    "Azure Storage is not configured. Set AZURE_STORAGE_CONNECTION_STRING "
                    "or AZURE_STORAGE_ACCOUNT_NAME."
                )

            if account_key is None or account_key.get_secret_value() in PLACEHOLDER_VALUES:
                raise RuntimeError(
                    "Azure Storage is not configured. Set AZURE_STORAGE_CONNECTION_STRING "
                    "or AZURE_STORAGE_ACCOUNT_KEY."
                )

            account_url = (
                f"https://{account_name}.blob.core.windows.net"
            )

            credential = AzureNamedKeyCredential(
                name=account_name,
                key=account_key.get_secret_value(),
            )

            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=credential,
            )

        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

    def ensure_container_exists(self) -> None:
        try:
            self.container_client.create_container()
        except ResourceExistsError:
            pass

    def upload_bytes(
        self,
        file_bytes: bytes,
        original_filename: str,
        content_type: str | None = None,
        folder: str = "item-files",
    ) -> BlobUploadResult:
        blob_name = self._generate_blob_name(
            original_filename=original_filename,
            folder=folder,
        )

        blob_client = self.container_client.get_blob_client(blob_name)

        blob_client.upload_blob(
            data=file_bytes,
            overwrite=False,
            content_settings=ContentSettings(
                content_type=content_type or "application/octet-stream"
            ),
        )

        return BlobUploadResult(
            blob_name=blob_name,
            blob_url=blob_client.url,
        )

    def upload_file(
        self,
        file: BinaryIO,
        original_filename: str,
        content_type: str | None = None,
        folder: str = "item-files",
    ) -> BlobUploadResult:
        blob_name = self._generate_blob_name(
            original_filename=original_filename,
            folder=folder,
        )

        blob_client = self.container_client.get_blob_client(blob_name)
        
        file.seek(0)

        blob_client.upload_blob(
            data=file,
            overwrite=False,
            content_settings=ContentSettings(
                content_type=content_type or "application/octet-stream"
            ),
        )

        return BlobUploadResult(
            blob_name=blob_name,
            blob_url=blob_client.url,
        )

    def _generate_blob_name(self, original_filename: str, folder: str) -> str:
        safe_filename = Path(original_filename).name.replace(" ", "_")
        unique_id = uuid4().hex

        return f"{folder}/{unique_id}_{safe_filename}"
    
    def delete_blob(self, blob_name: str) -> None:
        blob_client = self.container_client.get_blob_client(blob_name)
        try:
          blob_client.delete_blob()
        except ResourceNotFoundError:
          pass

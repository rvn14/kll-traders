from typing import Annotated

from azure.core.exceptions import AzureError
from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependencies.services import get_blob_service
from app.core.exceptions import (
    AzureBlobUploadError,
    BlobConfigurationError,
    InvalidFileTypeError,
)
from app.schemas.blob_schema import BlobUploadRead
from app.services.blob_service import AzureBlobService


router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


@router.post(
    "",
    response_model=BlobUploadRead,
    status_code=status.HTTP_201_CREATED,
)
def upload_file(
    file: Annotated[UploadFile, File(...)],
    blob_service: Annotated[AzureBlobService, Depends(get_blob_service)],
):
    if not file.filename:
        raise InvalidFileTypeError("Uploaded file must have a filename.")

    try:
        blob_service.ensure_container_exists()

        result = blob_service.upload_file(
            file=file.file,
            original_filename=file.filename,
            content_type=file.content_type,
            folder="uploads",
        )

        return BlobUploadRead(
            blob_name=result.blob_name,
            blob_url=result.blob_url,
        )

    except AzureError:
        raise AzureBlobUploadError("Failed to upload file to Azure Blob Storage.")

    except RuntimeError as error:
        raise BlobConfigurationError(str(error))
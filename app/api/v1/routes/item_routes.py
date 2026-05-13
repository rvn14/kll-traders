from typing import Annotated

from azure.core.exceptions import AzureError
from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.api.dependencies import get_blob_service, get_item_service
from app.core.exceptions import (
    AzureBlobUploadError,
    BlobConfigurationError,
    InvalidFileTypeError,
    ItemNotFoundError,
)
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services.blob_service import AzureBlobService
from app.services.item_service import ItemService


router = APIRouter(
    prefix="/items",
    tags=["Items"],
)


@router.post(
    "",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_item(
    item_data: ItemCreate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
):
    return item_service.create_item(item_data)


@router.get(
    "",
    response_model=list[ItemRead],
)
def get_items(
    item_service: Annotated[ItemService, Depends(get_item_service)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return item_service.get_items(skip=skip, limit=limit)


@router.get(
    "/{item_id}",
    response_model=ItemRead,
)
def get_item_by_id(
    item_id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
):
    return item_service.get_item_by_id(item_id)


@router.patch(
    "/{item_id}",
    response_model=ItemRead,
)
def update_item(
    item_id: int,
    item_data: ItemUpdate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
):
    return item_service.update_item(item_id, item_data)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_item(
    item_id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
):
    item_service.delete_item(item_id)
    return None


@router.post(
    "/{item_id}/image",
    response_model=ItemRead,
    status_code=status.HTTP_200_OK,
)
def upload_item_image(
    item_id: int,
    file: Annotated[UploadFile, File(...)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
    blob_service: Annotated[AzureBlobService, Depends(get_blob_service)],
):
    if not file.filename:
        raise InvalidFileTypeError("Uploaded file must have a filename.")

    if file.content_type is None or not file.content_type.startswith("image/"):
        raise InvalidFileTypeError("Only image files are allowed for item image upload.")

    existing_item = item_service.get_item_by_id(item_id)
    old_blob_name = existing_item.image_blob_name

    try:
        blob_service.ensure_container_exists()

        upload_result = blob_service.upload_file(
            file=file.file,
            original_filename=file.filename,
            content_type=file.content_type,
            folder="item-images",
        )

        try:
            updated_item = item_service.attach_item_blob(
                item_id=item_id,
                blob_name=upload_result.blob_name,
                blob_url=upload_result.blob_url,
            )

        except ItemNotFoundError:
            blob_service.delete_blob(upload_result.blob_name)
            raise

        if old_blob_name and old_blob_name != upload_result.blob_name:
            blob_service.delete_blob(old_blob_name)

        return updated_item

    except AzureError:
        raise AzureBlobUploadError("Failed to upload item image to Azure Blob Storage.")

    except RuntimeError as error:
        raise BlobConfigurationError(str(error))
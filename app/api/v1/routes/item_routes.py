from typing import Annotated

from azure.core.exceptions import AzureError
from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.api.dependencies.services import get_blob_service, get_item_service
from app.core.exceptions import (
    AzureBlobUploadError,
    BlobConfigurationError,
    InvalidFileTypeError,
    ItemNotFoundError,
)
from app.models.user import User
from app.services.blob_service import AzureBlobService
from app.services.item_service import ItemService

from fastapi import APIRouter, Depends, Query
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from app.api.dependencies.auth import get_current_user_optional
from app.db.session import get_db
from app.schemas.item_schema import ItemQueryParams,ItemCreateRequest, PaginatedItemsResponse ,ItemResponse,ItemAdminResponse , ItemUpdateRequest
from app.services.item_service import ItemService
from app.api.dependencies.auth import require_admin 

router = APIRouter(prefix="/items", tags=["Items"])

@router.post(
            "",
            response_model=ItemAdminResponse,
            status_code=status.HTTP_201_CREATED
)
def create_item(
    payload:ItemCreateRequest,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    currect_user : User = Depends(require_admin),
):
    return item_service.create_item(payload)

@router.get("",response_model=PaginatedItemsResponse)
def getItems(
    item_service: Annotated[ItemService, Depends(get_item_service)],
    params: ItemQueryParams = Depends(),
):
    return item_service.get_items(params)
    
@router.get(
    "/{item_id}",
    response_model=ItemAdminResponse | ItemResponse,
    summary="Get item by ID",
)
def get_item_by_id(
    item_id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: User | None = Depends(get_current_user_optional),
):
    return item_service.get_item_by_id(item_id, current_user)


@router.patch(
    "/{item_id}",
    response_model=ItemAdminResponse,
)
def update_item(
    item_id: int,
    payload: ItemUpdateRequest,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: User = Depends(require_admin), 
):
    return item_service.update_item(item_id, payload)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_200_OK,
)
def delete_item(
    item_id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: User = Depends(require_admin),
):
    return item_service.delete_item(item_id)


@router.patch(
    "/{item_id}/restore",
    response_model=ItemAdminResponse,
)
def restore_item(
    item_id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
    current_user: User = Depends(require_admin),    
):
    return item_service.restore_item(item_id)


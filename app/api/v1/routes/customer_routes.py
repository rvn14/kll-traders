from typing import Annotated

from fastapi import APIRouter
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from app.api.dependencies import get_customer_service
from app.schemas.customer import CustomerRead
from app.services import customer_service
from app.services.customer_service import CustomerService


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post(
    "",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer_data: CustomerRead,
    item_Service: Annotated[CustomerService, Depends(get_customer_service)],
):
    return customer_service.create_item(customer_data)

@router.get(
    "",
    response_model=list[CustomerRead],
)
def list_customers(
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return customer_service.list_items(skip=skip, limit=limit)


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,   
)
def get_item_by_id(
    customer_id: int,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
):
    return customer_service.get_item_by_id(customer_id)

@router.put(
    "/{customer_id}",
    response_model=CustomerRead,
)
def update_customer(
    customer_id: int,
    customer_data: CustomerRead,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
):
    return customer_service.update_item(customer_id, customer_data)
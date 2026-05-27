from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_customer_profile_service
from app.models.user import User
from app.schemas.cutomer_profile_schema import AddressCreate, AddressRead, AddressUpdate, CustomerProfileRead, ProfileUpdate
from app.services.customer_profile_service import CustomerProfileService


router = APIRouter(
    prefix="/customer-profile",
    tags=["Customer Profile"],
)

# get profile
@router.get(
    "",
    response_model=CustomerProfileRead
)
def get_customer_profile(
    profile_service: Annotated[CustomerProfileService, Depends(get_customer_profile_service)],
    current_user: User = Depends(get_current_user)
):
    return profile_service.get_customer_profile(current_user)


# update profile
@router.put(
    "",
    response_model=CustomerProfileRead
)
def update_customer_profile(
    payload: ProfileUpdate,
    profile_service: Annotated[CustomerProfileService, Depends(get_customer_profile_service)],
    current_user: User = Depends(get_current_user)
):
    return profile_service.update_customer_profile(current_user, payload)


# get addresses
@router.get(
    "/addresses",
    response_model=list[AddressRead]
)
def get_addresses(
    profile_service: Annotated[CustomerProfileService, Depends(get_customer_profile_service)],
    current_user: User = Depends(get_current_user)
):
    return profile_service.get_addresses(current_user)


# get address by id
@router.get(
    "/addresses/{address_id}",
    response_model=AddressRead
)
def get_address_by_id(
    address_id: int,
    profile_service: Annotated[CustomerProfileService, Depends(get_customer_profile_service)],
    current_user: User = Depends(get_current_user)
):
    return profile_service.get_address_by_id(current_user, address_id)


# create address
@router.post(
    "/addresses",
    response_model=AddressRead,
    status_code=status.HTTP_201_CREATED
)
def create_address(
    payload: AddressCreate,
    profile_service: Annotated[CustomerProfileService, Depends(get_customer_profile_service)],
    current_user: User = Depends(get_current_user)
):
    return profile_service.create_address(current_user, payload)


# update address
@router.put(
    "/addresses/{address_id}",
    response_model=AddressRead
)
def update_address(
    address_id: int,
    payload: AddressUpdate,
    profile_service: Annotated[CustomerProfileService, Depends(get_customer_profile_service)],
    current_user: User = Depends(get_current_user)
):
    return profile_service.update_address(current_user, address_id, payload)


# delete address
@router.delete(
    "/addresses/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_address(
    address_id: int,
    profile_service: Annotated[CustomerProfileService, Depends(get_customer_profile_service)],
    current_user: User = Depends(get_current_user)
):
    profile_service.delete_address(current_user, address_id)
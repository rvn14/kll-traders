from typing import Annotated

from fastapi import APIRouter
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from app.api.dependencies.admin import require_admin
from app.api.dependencies.services import get_admin_user_service
from app.models.user import User
from app.schemas.user_schema import UserRead, UserCreate, UserUpdate
from app.services import admin_user_service
from app.services.admin_user_service import AdminUserService


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin Users"],
)


# create user
@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreate,
    admin_user_service: Annotated[AdminUserService, Depends(get_admin_user_service)],
    _: User = Depends(require_admin)
):
    return admin_user_service.create_user(payload)


# get all
@router.get(
    "",
    response_model=list[UserRead],
)
def list_users(
    admin_user_service: Annotated[AdminUserService, Depends(get_admin_user_service)],
    _: User = Depends(require_admin),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
):
    return admin_user_service.get_users(skip=skip, limit=limit)


# get by email
@router.get(
    "/by-email",
    response_model=UserRead,   
)
def get_user_by_email(
    admin_user_service: Annotated[AdminUserService, Depends(get_admin_user_service)],
    _: User = Depends(require_admin),
    email: str = Query(..., min_length=1),
):
    return admin_user_service.get_user_by_email(email.strip())


# get by id
@router.get(
    "/{user_id}",
    response_model=UserRead,   
)
def get_user_by_id(
    user_id: int,
    admin_user_service: Annotated[AdminUserService, Depends(get_admin_user_service)],
    _: User = Depends(require_admin)
):
    return admin_user_service.get_user_by_id(user_id)


# update user
@router.put(
    "/{user_id}",
    response_model=UserRead,
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    admin_user_service: Annotated[AdminUserService, Depends(get_admin_user_service)],
    _: User = Depends(require_admin)
):
    return admin_user_service.update_user(user_id, payload)


# deactivate user
@router.post(
    "/{user_id}/deactivate",
    response_model=UserRead,
)
def deactivate_user(
    user_id: int,
    admin_user_service: Annotated[AdminUserService, Depends(get_admin_user_service)],
    _: User = Depends(require_admin)
):
    return admin_user_service.deactivate_user(user_id)


# activate user
@router.post(
    "/{user_id}/activate",
    response_model=UserRead,
)
def activate_user(
    user_id: int,
    admin_user_service: Annotated[AdminUserService, Depends(get_admin_user_service)],
    _: User = Depends(require_admin)
):
    return admin_user_service.activate_user(user_id)


# delete user
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    admin_user_service: Annotated[AdminUserService, Depends(get_admin_user_service)],
    _: User = Depends(require_admin)
):
    admin_user_service.delete_user(user_id)
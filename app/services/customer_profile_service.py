from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password
from app.models.address import Address
from app.models.user import CustomerProfile, User
from app.repositories.customer_profile_repository import CustomerProfileRepository
from app.schemas.cutomer_profile_schema import AddressCreate, AddressUpdate, ProfileUpdate, UpdateEmailRequest, UpdatePasswordRequest


class CustomerProfileService:
    def __init__(self, customer_repository: CustomerProfileRepository):
        self.customer_repository = customer_repository

    def get_customer_profile(self, user: User) -> User:
        profile = self.customer_repository.get_customer_profile(user.id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found"
            )

        return user

    def update_customer_profile(self, user: User, payload: ProfileUpdate) -> User:
        update_data = payload.model_dump(exclude_unset=True)

        if not update_data:
            return user
        
        try: 
            return self.customer_repository.update_customer_profile(user, update_data)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Failed to update customer profile"
            )
        
    def create_address(self, user: User, payload: AddressCreate) -> Address:
            profile = self.customer_repository.get_customer_profile(user.id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer profile not found"
                )
            address_data = payload.model_dump()
            address_data["customer_profile_id"] = profile.id
            return self.customer_repository.create_address(address_data)

    def get_addresses(self, user: User) -> list[Address]:
        profile = self.customer_repository.get_customer_profile(user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found"
            )
        return self.customer_repository.get_addresses(profile.id)
    
    def get_address_by_id(self, user: User, address_id: int) -> Address:
        profile = self.customer_repository.get_customer_profile(user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found"
            )
        return self.customer_repository.get_address_by_id(address_id, profile.id)
    
    def update_address(self, user: User, address_id: int, payload: AddressUpdate) -> Address:
        profile = self.customer_repository.get_customer_profile(user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found"
            )
        address = self.customer_repository.get_address_by_id(address_id, profile.id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return address
        try:
            return self.customer_repository.update_address(address, update_data)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Failed to update address"
            )
        
    def delete_address(self, user: User, address_id: int) -> None:
        profile = self.customer_repository.get_customer_profile(user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer profile not found"
            )
        address = self.customer_repository.get_address_by_id(address_id, profile.id)
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        self.customer_repository.delete_address(address)

    def update_email(self, current_user: User, payload: UpdateEmailRequest) -> User:
        if not verify_password(payload.password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        existing_user = self.customer_repository.get_user_by_email(payload.new_email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already in use by another account"
            )
        
        return self.customer_repository.update_user_email(current_user, payload.new_email)
    
    def update_password(self, current_user: User, payload: UpdatePasswordRequest) -> User:
        if not verify_password(payload.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect current password"
            )
        
        if payload.current_password == payload.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password cannot be the same as the current password"
            )
            
        new_hashed_password = hash_password(payload.new_password)
        return self.customer_repository.update_user_password(current_user, new_hashed_password)
        
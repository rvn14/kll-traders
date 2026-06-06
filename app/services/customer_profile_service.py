from fastapi import HTTPException, status

from app.models.address import Address
from app.models.user import CustomerProfile, User
from app.repositories.customer_profile_repository import CustomerProfileRepository
from app.schemas.cutomer_profile_schema import AddressCreate, AddressUpdate, ProfileUpdate


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
        
from sqlalchemy import select
from sqlalchemy.orm import Session
from psycopg import IntegrityError

from app.models.user import CustomerProfile, User
from app.models.address import Address


class CustomerProfileRepository:
    def __init__(self, db):
        self.db = db

    def get_customer_profile(self, user_id: int) -> CustomerProfile | None:
        statement = select(CustomerProfile).where(CustomerProfile.user_id == user_id)
        return self.db.execute(statement).scalars().first()
    
    def update_customer_profile(self, user: User, update_data: dict) -> User:
        for field, value in update_data.items():
            setattr(user, field, value)
        try:
          self.db.commit()
          self.db.refresh(user)
          return user
        except IntegrityError:
            self.db.rollback()
            raise
    
    def create_address(self, address_data: dict) -> Address:
        address = Address(**address_data)
        try:
            self.db.add(address)
            self.db.commit()
            self.db.refresh(address)
            return address
        except IntegrityError:
            self.db.rollback()
            raise

    def get_addresses(self, profile_id: int) -> list[Address]:
        statement = select(Address).where(Address.customer_profile_id == profile_id)
        return list(self.db.scalars(statement).all())
    
    def get_address_by_id(self, address_id: int, profile_id: int) -> Address | None:
        statement = select(Address).where(
            Address.id == address_id, 
            Address.customer_profile_id == profile_id
        )
        return self.db.execute(statement).scalars().first()
    
    def update_address(self, address: Address, update_data: dict) -> Address:
        for field, value in update_data.items():
            setattr(address, field, value)
        try:
            self.db.commit()
            self.db.refresh(address)
            return address
        except IntegrityError:
            self.db.rollback()
            raise
    
    def delete_address(self, address: Address) -> None:
        self.db.delete(address)
        try:
            self.db.commit()
        except:
            self.db.rollback()
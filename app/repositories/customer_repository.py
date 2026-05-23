from decimal import Decimal

from psycopg import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session


from app.models.customer import Customer

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db
    
    
    def create(self, customer_data: dict) -> Customer:
        customer = Customer(**customer_data)

        try:
          self.db.add(customer)
          self.db.commit()
          self.db.refresh(customer)
          return customer
        except:
          self.db.rollback()
          raise
      
      
    def get_all(self, skip: int = 0, limit: int = 100) -> list[Customer]:
        statement = (
            select(Customer)
            .order_by(Customer.id)
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())
    
    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)
    
    def get_by_email(self, email: str) -> Customer | None:
        statement = select(Customer).where(Customer.email == email)
        return self.db.scalars(statement).first()
    
    def update(self, customer: Customer, update_data: dict) -> Customer:
        for field, value in update_data.items():
            setattr(customer, field, value)

        try:
          self.db.commit()
          self.db.refresh(customer)
          return customer
        except IntegrityError:
          self.db.rollback()
          raise
      
      
    def delete(self, customer: Customer) -> None:
        self.db.delete(customer)
        try:
          self.db.commit()
        except:
          self.db.rollback()
          raise
        
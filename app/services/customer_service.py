from sqlalchemy.exc import IntegrityError
from app.core.exceptions import CustomerAlreadyExistsError, CustomerNotFoundError
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate


class CustomerService:
    MAX_LIMIT = 100
    
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository
        
        
    def create_customer(self, customer_data: CustomerCreate) -> Customer:
        existing_item = self.customer_repository.get_by_email(customer_data.email)
        
        if existing_item is not None:
            raise CustomerAlreadyExistsError
        
        
        data = customer_data.model_dump()
        
        try:
          return self.customer_repository.create(data)
        except IntegrityError:
            raise CustomerAlreadyExistsError(customer_data.email)
          
          
    def get_customers(self, skip: int = 0, limit: int = 100) -> list[Customer]:
        safe_limit = min(limit, self.MAX_LIMIT)
        return self.customer_repository.list(skip=skip, limit=safe_limit)
    
    def get_customer_by_id(self, customer_id: int) -> Customer:
        customer = self.customer_repository.get_by_id(customer_id)
        
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        
        return customer
    
    def get_customer_by_email(self, email: str) -> Customer:
        customer = self.customer_repository.get_by_email(email)
        
        if customer is None:
            raise CustomerNotFoundError(email)
        
        return customer
    
    def delete_customer(self, customer_id: int) -> None:
        customer = self.customer_repository.get_by_id(customer_id)
        
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        
        self.customer_repository.delete(customer)
        
    def update_customer(self, customer_id: int, customer_data: CustomerCreate) -> Customer:
        existing_customer = self.customer_repository.get_by_id(customer_id)
        
        if existing_customer is None:
            raise CustomerNotFoundError(customer_id)
        
        update_data = customer_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return existing_customer
        
        new_email = update_data.get("email")
        
        if new_email is not None:
            customer_with_same_email = self.customer_repository.get_by_email(new_email)
            
            if customer_with_same_email is not None and customer_with_same_email.id != customer_id:
                raise CustomerAlreadyExistsError(new_email)
        
        try:
            return self.customer_repository.update(existing_customer, update_data)
        except IntegrityError:
            raise CustomerAlreadyExistsError(update_data.get("email", "unknown email"))
        
        
        
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import CustomerAlreadyExistsError, CustomerNotFoundError, UserAlreadyExistsError, UserNotFoundError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.admin_user_repository import AdminUserRepository
from app.schemas.user_schema import UserCreate, UserUpdate


class AdminUserService:
    MAX_LIMIT = 100
    
    def __init__(self, admin_user_repository: AdminUserRepository):
        self.admin_user_repository = admin_user_repository
        
        
    def create_user(self, user_data: UserCreate) -> User:
        existing_item = self.admin_user_repository.get_by_email(user_data.email)
        
        if existing_item is not None:
            raise UserAlreadyExistsError

        data = user_data.model_dump()
        password = data.pop("password", None)
        data["hashed_password"] = hash_password(password) if password else None

        try:
            return self.admin_user_repository.create(data)
        except IntegrityError:
            raise UserAlreadyExistsError(user_data.email)
          
          
    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        safe_limit = min(limit, self.MAX_LIMIT)
        return self.admin_user_repository.get_all(skip=skip, limit=safe_limit)
    
    def get_user_by_id(self, user_id: int) -> User:
        user = self.admin_user_repository.get_by_id(user_id)
        
        if user is None:
            raise UserNotFoundError(user_id)
        
        return user
    
    def get_user_by_email(self, email: str) -> User:
        user = self.admin_user_repository.get_by_email(email)
        
        if user is None:
            raise UserNotFoundError(email)
        
        return user
    
    def delete_user(self, user_id: int) -> None:
        user = self.admin_user_repository.get_by_id(user_id)
        
        if user is None:
            raise UserNotFoundError(user_id)
        
        self.admin_user_repository.delete(user)

    def deactivate_user(self, user_id: int) -> User:
        user = self.admin_user_repository.get_by_id(user_id)
        
        if user is None:
            raise UserNotFoundError(user_id)
        
        update_data = {"is_active": False}
        
        try:
            return self.admin_user_repository.update(user, update_data)
        except IntegrityError:
            raise
        
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        existing_user = self.admin_user_repository.get_by_id(user_id)
        
        if existing_user is None:
            raise UserNotFoundError(user_id)
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return existing_user
        
        try:
            return self.admin_user_repository.update(existing_user, update_data)
        except IntegrityError:
            raise
        
        
from decimal import Decimal

from psycopg import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session


from app.models.user import User

class AdminUserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    
    def create(self, user_data: dict) -> User:
        user = User(**user_data)

        try:
          self.db.add(user)
          self.db.commit()
          self.db.refresh(user)
          return user
        except:
          self.db.rollback()
          raise
      
      
    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        statement = (
            select(User)
            .order_by(User.id)
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())
    
    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)
    
    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.scalars(statement).first()
    
    def update(self, user: User, update_data: dict) -> User:
        for field, value in update_data.items():
            setattr(user, field, value)

        try:
          self.db.commit()
          self.db.refresh(user)
          return user
        except IntegrityError:
          self.db.rollback()
          raise
      
      
    def delete(self, user: User) -> None:
        self.db.delete(user)
        try:
          self.db.commit()
        except:
          self.db.rollback()
          raise
        
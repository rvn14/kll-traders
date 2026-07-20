from sqlalchemy.orm import Session
from app.models.brand import Brand

class BrandRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_brands(self, query: str) -> list[Brand]:
        if not query.strip():
            return []
        return self.db.query(Brand).filter(
            Brand.name.ilike(f"%{query}%")
        ).filter(Brand.is_active == True).limit(20).all()

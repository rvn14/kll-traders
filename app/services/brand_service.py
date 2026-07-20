from app.repositories.brand_repository import BrandRepository
from app.models.brand import Brand

class BrandService:
    def __init__(self, brand_repo: BrandRepository):
        self.brand_repo = brand_repo

    def search_brands(self, query: str) -> list[Brand]:
        return self.brand_repo.search_brands(query)

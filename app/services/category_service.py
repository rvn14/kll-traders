from app.repositories.category_repository import CategoryRepository
from app.models.category import Category

class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def get_categories(self) -> list[Category]:
        return self.category_repo.get_all()

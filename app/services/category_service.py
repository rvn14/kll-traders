from app.repositories.category_repository import CategoryRepository
from app.models.category import Category

class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def get_categories(self) -> list[Category]:
        categories = self.category_repo.get_all()
        
        # Ensure "Others" category exists in the returned list
        has_others = any(
            c.name.lower() == "others" for c in categories
        )
        
        if not has_others:
            # Create a virtual "Others" category (not persisted)
            others = Category(
                id=-1,
                name="Others",
                is_active=True,
                parent_id=None,
            )
            categories.append(others)
        
        return categories

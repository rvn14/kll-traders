import app.models.item
from app.db.session import Base, engine


def create_db_tables():
    Base.metadata.create_all(bind=engine)
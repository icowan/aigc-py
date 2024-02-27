from functools import lru_cache

from sqlalchemy.orm import Session

from app.models.base import get_db
from app.repository.datasets import DatasetsRepository


class Repository:
    def __init__(self, db: Session):
        """Construct a new repository."""
        self.dataset = DatasetsRepository(db)

    def datasets(self):
        """Return the dataset repository."""
        return self.dataset


def get_repository(db: Session):
    return Repository(db)

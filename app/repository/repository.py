from functools import lru_cache

from sqlalchemy.orm import Session

from app.models.base import get_db
from app.repository.dataset_segments import DatasetSegmentsRepository
from app.repository.datasets import DatasetsRepository


class Repository:
    def __init__(self, db: Session):
        """Construct a new repository."""
        self._datasets = DatasetsRepository(db)
        self._dataset_segments = DatasetSegmentsRepository(db)

    def datasets(self) -> DatasetsRepository:
        """Return the datasets repository."""
        return self._datasets

    def dataset_segments(self) -> DatasetSegmentsRepository:
        """Return the dataset segments repository."""
        return self._dataset_segments


def get_repository(db: Session) -> Repository:
    return Repository(db)

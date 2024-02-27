from sqlalchemy.orm import Session

from app.models.datasets import Datasets


class DatasetsRepository:
    """The repository for datasets. It contains methods for accessing datasets."""

    def __init__(self, db: Session):
        """Construct a new repository for datasets."""
        self.db = db

    def get(self, dataset_id):
        """Get a dataset by its ID."""
        return self.db.get(dataset_id)

    def create(self, dataset: Datasets):
        """Create a new dataset."""
        db = self.db
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

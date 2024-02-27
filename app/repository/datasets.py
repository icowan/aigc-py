from sqlalchemy.orm import Session

from app.models.datasets import Datasets, DatasetSegments


class DatasetsRepository:
    """The repository for datasets. It contains methods for accessing datasets."""

    def __init__(self, db: Session):
        """Construct a new repository for datasets."""
        self.db = db

    def create(self, dataset: Datasets):
        """Create a new dataset."""
        db = self.db
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    def find_by_name(self, name: str):
        """Find a dataset by name."""
        return self.db.query(Datasets).filter(Datasets.name == name).first()

    def list(self, tenant_id: int, name: str = '', page: int = 1, page_size: int = 10):
        """List datasets."""
        query = self.db.query(Datasets).filter(Datasets.tenant_id == tenant_id)
        if name:
            query = query.filter(Datasets.name.like(f"%{name}%"))
        total = query.count()
        datasets = query.offset((page - 1) * page_size).limit(page_size).all()
        return datasets, total

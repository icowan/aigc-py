from datetime import datetime
from typing import List

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.datasets import Datasets, DatasetSegments


class DatasetsRepository:
    """The repository for datasets. It contains methods for accessing datasets."""

    def __init__(self, db: Session):
        """Construct a new repository for datasets."""
        self.db = db

    async def create(self, dataset: Datasets) -> Datasets:
        """Create a new dataset."""
        db = self.db
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    async def find_by_name(self, name: str) -> Datasets:
        """Find a dataset by name."""
        return self.db.query(Datasets).filter(Datasets.name == name, Datasets.deleted_at == None).first()

    async def list(self, tenant_id: int, name: str = '', page: int = 1, page_size: int = 10) -> (List[Datasets], int):
        """List datasets."""
        query = self.db.query(Datasets).filter(Datasets.tenant_id == tenant_id, Datasets.deleted_at == None)
        if name:
            query = query.filter(Datasets.name.like(f"%{name}%"))
        total = query.count()
        datasets = query.order_by(desc(Datasets.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        return datasets, total

    async def find_by_uuid(self, tenant_id: int, uuid: str) -> Datasets:
        """Find a dataset by UUID."""
        return self.db.query(Datasets).filter(Datasets.tenant_id == tenant_id, Datasets.uuid == uuid,
                                              Datasets.deleted_at == None).first()

    async def delete_by_uuid(self, tenant_id: int, uuid: str) -> bool:
        """Delete a dataset by UUID."""
        dataset = self.find_by_uuid(tenant_id, uuid)
        self.db.delete(dataset)
        self.db.commit()
        return True

    async def delete(self, dataset: Datasets, unscoped: bool = False) -> bool:
        """Delete a dataset."""
        if unscoped:
            """需要去除关联关系"""
            self.db.delete(dataset)
        else:
            dataset.deleted_at = datetime.now()
        self.db.commit()
        return True

    async def update(self, id: int, dataset: Datasets) -> Datasets:
        """Update a dataset."""
        update_data = {
            "name": dataset.name,
            "remark": dataset.remark,
            "format_type": dataset.format_type,
            "split_type": dataset.split_type,
            "updated_at": datetime.now(),
            "segment_count": dataset.segment_count
        }
        self.db.query(Datasets).filter(Datasets.id == id).update(update_data)
        self.db.commit()
        return await self.get(id)

    async def get(self, id: int) -> Datasets:
        """Get a dataset by ID."""
        return self.db.query(Datasets).filter(Datasets.id == id).first()

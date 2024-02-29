from typing import List

from app.models.datasets import DatasetSegments


class DatasetSegmentsRepository:
    """The repository for dataset segments. It contains methods for accessing dataset segments."""

    def __init__(self, db):
        """Construct a new repository for dataset segments."""
        self.db = db

    async def add_segments(self, segments: list[DatasetSegments]):
        """Add segments to a dataset."""
        db = self.db
        db.add_all(segments)
        db.commit()

    async def get_by_dataset_id_and_sn(self, dataset_id: int, start: int = 0, end: int = 0) -> List[DatasetSegments]:
        """Get segments by dataset ID and serial number."""
        return self.db.query(DatasetSegments).filter(DatasetSegments.dataset_id == dataset_id,
                                                     DatasetSegments.serial_number >= start,
                                                     DatasetSegments.serial_number < end).all()

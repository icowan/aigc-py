from app.models.datasets import DatasetSegments


class DatasetSegmentsRepository:
    """The repository for dataset segments. It contains methods for accessing dataset segments."""

    def __init__(self, db):
        """Construct a new repository for dataset segments."""
        self.db = db

    def add_segments(self, segments: list[DatasetSegments]):
        """Add segments to a dataset."""
        db = self.db
        db.add_all(segments)
        db.commit()

from datetime import datetime
from typing import Type, List

from sqlalchemy import desc, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload

from app.models.data_annotation import DataAnnotation, DataAnnotationSegments, DataAnnotationStatus
from app.models.datasets import DatasetSegments


class DataAnnotationRepository:
    """数据标注仓库"""

    def __init__(self, db: Session):
        self.db = db

    async def create(self, data_annotation: DataAnnotation) -> DataAnnotation:
        """Create a new data annotation."""
        self.db.add(data_annotation)
        self.db.commit()
        self.db.refresh(data_annotation)
        return data_annotation

    async def get(self, id: int) -> DataAnnotation:
        """Get a data annotation by ID."""
        return self.db.query(DataAnnotation).filter(DataAnnotation.id == id).first()

    async def update(self, id: int, data_annotation: DataAnnotation) -> DataAnnotation:
        """"Update a data annotation."""
        self.db.query(DataAnnotation).filter(DataAnnotation.id == id).update(data_annotation)
        self.db.commit()
        return await self.get(id)

    async def delete(self, id: int, unscoped: bool = False):
        """Delete a data annotation."""
        data_annotation = await self.get(id)
        if unscoped:
            self.db.delete(data_annotation)
        else:
            update_data = {
                "deleted_at": datetime.now()
            }
            self.db.query(DataAnnotation).filter(DataAnnotation.id == id).update(update_data)
        return

    async def get_by_uuid(self, tenant_id: int, uid: str, datasets: bool = False,
                          segments: bool = False) -> DataAnnotation:
        """Find a data annotation by UUID."""
        query = self.db.query(DataAnnotation).filter(DataAnnotation.tenant_id == tenant_id, DataAnnotation.uuid == uid,
                                                     DataAnnotation.deleted_at == None)
        if datasets:
            query = query.options(joinedload(DataAnnotation.Datasets))
        if segments:
            query = query.options(joinedload(DataAnnotation.Segments))
        return query.first()

    async def get_segment_by_sn(self, dataset_id: int, serial_number: int) -> Type[DatasetSegments] | None:
        """根据sn号获取标注记录"""
        return self.db.query(DatasetSegments).filter(DatasetSegments.dataset_id == dataset_id,
                                                     DatasetSegments.serial_number == serial_number).first()

    async def get_annotation_tasks(self, tenant_id: int, status: str = None, datasets: bool = False, page: int = 1,
                                   page_size: int = 10) -> (
            List[Type[DataAnnotation]], int):
        """获取标注任务列表"""
        query = self.db.query(DataAnnotation).filter(DataAnnotation.tenant_id == tenant_id,
                                                     DataAnnotation.deleted_at == None)
        if status:
            query = query.filter(DataAnnotation.status == status)
        if datasets:
            query = query.options(joinedload(DataAnnotation.Datasets))
        total = query.count()
        annotations = query.order_by(desc(DataAnnotation.created_at)).offset((page - 1) * page_size).limit(
            page_size).all()
        return annotations, total

    async def add_annotation_segments(self, segments: List[DataAnnotationSegments]) -> List[DataAnnotationSegments]:
        """Add segments to a data annotation."""
        self.db.add_all(segments)
        self.db.commit()
        return segments

    async def get_annotation_one_segment(self, annotation_id: int, index: int = -1,
                                         status: DataAnnotationStatus = None) -> DataAnnotationSegments:
        """Get one segment by annotation ID and index."""
        query = self.db.query(DataAnnotationSegments).filter(DataAnnotationSegments.data_annotation_id == annotation_id)
        if status:
            query = query.filter(DataAnnotationSegments.status == status)
        if index == -1:
            return query.order_by(DataAnnotationSegments.id).first()
        return query.order_by(DataAnnotationSegments.id).offset(index * 1).limit(1).first()

    async def get_annotation_segment_by_uuid(self, annotation_id: int, uid: str) -> DataAnnotationSegments:
        """Find a segment by UUID."""
        return self.db.query(DataAnnotationSegments).filter(DataAnnotationSegments.data_annotation_id == annotation_id,
                                                            DataAnnotationSegments.uuid == uid).first()

    async def update_annotation_segment(self, data_annotation: DataAnnotation,
                                        data_annotation_segment: DataAnnotationSegments) -> DataAnnotationSegments:
        """Update a data annotation segment."""
        if (data_annotation.completed + data_annotation.abandoned) == data_annotation.total:
            data_annotation.status = DataAnnotationStatus.COMPLETED
            data_annotation.completed_at = datetime.now()
        if data_annotation.status == DataAnnotationStatus.PENDING:
            data_annotation.status = DataAnnotationStatus.PROCESSING

        update_data = {
            "segment_content": data_annotation_segment.segment_content,
            "status": data_annotation_segment.status,
            "updated_at": datetime.now(),
            "document": data_annotation_segment.document,
            "instruction": data_annotation_segment.instruction,
            "input": data_annotation_segment.input,
            "question": data_annotation_segment.question,
            "intent": data_annotation_segment.intent,
            "output": data_annotation_segment.output,
            "creator_email": data_annotation_segment.creator_email
        }
        self.db.query(DataAnnotationSegments).filter(DataAnnotationSegments.id == data_annotation_segment.id).update(
            update_data)
        self.db.commit()
        await self.update_data_annotation(data_annotation.id, data_annotation)
        return await self.get_annotation_segment_by_uuid(data_annotation_segment.data_annotation_id,
                                                         data_annotation_segment.uuid)

    async def update_data_annotation(self, data_annotation_id: int, data_annotation: DataAnnotation) -> DataAnnotation:
        """Update a data annotation."""
        update_data = {
            "name": data_annotation.name,
            "principal": data_annotation.principal,
            "annotation_type": data_annotation.annotation_type,
            "status": data_annotation.status,
            "completed_at": data_annotation.completed_at,
            "data_sequence": data_annotation.data_sequence,
            "total": data_annotation.total,
            "completed": data_annotation.completed,
            "abandoned": data_annotation.abandoned,
            "remark": data_annotation.remark,
            "updated_at": datetime.now(),
        }
        self.db.query(DataAnnotation).filter(DataAnnotation.id == data_annotation_id).update(update_data)
        self.db.commit()
        return await self.get(data_annotation_id)

    async def get_annotation_segments(self, annotation_id: int, status: DataAnnotationStatus = None) -> (
            List[DataAnnotationSegments], int):
        """Get segments by annotation ID."""
        query = self.db.query(DataAnnotationSegments).filter(DataAnnotationSegments.data_annotation_id == annotation_id,
                                                             DataAnnotationSegments.deleted_at == None,
                                                             DataAnnotationSegments.status == DataAnnotationStatus.COMPLETED)
        if status:
            query = query.filter(DataAnnotationSegments.status == status)
        segments = query.order_by(DataAnnotationSegments.id).all()
        return segments, len(segments)

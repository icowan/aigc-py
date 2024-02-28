from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base


class DataAnnotation(Base):
    """
    标注任务表
    """
    __tablename__ = "data_annotations"

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), comment="数据集ID")
    job_id = Column(String, unique=True, index=True, comment="标注任务ID")
    job_name = Column(String, index=True, comment="任务名称")
    tenant_id = Column(Integer, index=True, comment="租户ID")
    principal = Column(String, index=True, comment="负责人")
    annotation_type = Column(String, index=True, comment="标注类型")
    status = Column(String, index=True, comment="标注状态")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    data_sequence = Column(String, comment="数据序列")
    total = Column(Integer, default=0, comment="需要标的数据总量")
    completed = Column(Integer, default=0, comment="完成标注量")
    abandoned = Column(Integer, default=0, comment="废弃标注量")
    remark = Column(String, nullable=True, comment="备注")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    # Samples = relationship("DataAnnotationSample", back_populates="owner")
    Dataset = relationship("Datasets", back_populates="Annotations")


class DataAnnotationSegments(Base):
    """
    标注任务样本表
    """
    __tablename__ = "data_annotation_segments"

    id = Column(Integer, primary_key=True)
    data_annotation_id = Column(Integer, ForeignKey("data_annotations.id"), comment="标注任务ID")
    segment_id = Column(Integer, ForeignKey("dataset_segments.id"), comment="样本ID")
    remark = Column(String, nullable=True, comment="备注")
    creator_email = Column(String, nullable=False, index=True, comment="创建人邮箱")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")
    # owner = relationship("DataAnnotation", back_populates="Samples")
    # sample = relationship("DatasetSample", back_populates="Annotations")

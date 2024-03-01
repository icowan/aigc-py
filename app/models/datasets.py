import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, text, Text
from sqlalchemy.orm import relationship, Session
from app.models.base import Base


class Datasets(Base):
    """
    数据集表
    """
    __tablename__ = "datasets_v0"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), index=True, unique=True, comment="UUID")
    name = Column(String(64), unique=True, index=True, comment="名称")
    remark = Column(String(500), nullable=True, comment="描述")
    segment_count = Column(Integer, default=0, comment="样本数量")
    creator_email = Column(String(64), nullable=False, index=True, comment="创建人邮箱")
    tenant_id = Column(Integer, nullable=False, index=True, comment="租户ID")
    # type = Column(String(12), nullable=False, index=True, comment="数据集类型")
    format_type = Column(String(12), name="format", nullable=True, default="alpaca", comment="数据集类型")
    split_type = Column(String(12), nullable=True, default="\n\n", comment="切割方式")
    split_max = Column(Integer, nullable=True, default=1000, comment="切割的最大数据块")
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    Segments = relationship("DatasetSegments", back_populates="Datasets")
    Annotations = relationship("DataAnnotation", back_populates="Datasets")


class DatasetSegments(Base):
    """
    数据集切片表
    """
    __tablename__ = "dataset_segments"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), index=True, unique=True, comment="UUID")
    dataset_id = Column(Integer, ForeignKey("datasets_v0.id"), nullable=False, index=True, comment="数据集ID")
    serial_number = Column(Integer, nullable=False, index=True, comment="序号")
    content = Column(Text, nullable=False, comment="内容")
    word_count = Column(Integer, nullable=True, default=0, comment="字数")
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    Datasets = relationship("Datasets", back_populates="Segments")
    DataAnnotationSegments = relationship("DataAnnotationSegments", back_populates="Segments")

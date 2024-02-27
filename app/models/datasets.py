import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, text, Text
from sqlalchemy.orm import relationship, Session
from app.models.base import Base


class Datasets(Base):
    """
    数据集表
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, index=True, unique=True, comment="UUID")
    name = Column(String, unique=True, index=True, comment="名称")
    remark = Column(String, nullable=True, comment="描述")
    segment_count = Column(Integer, default=0, comment="样本数量")
    creator_email = Column(String, nullable=False, index=True, comment="创建人邮箱")
    tenant_id = Column(Integer, nullable=False, index=True, comment="租户ID")
    type = Column(String, nullable=False, index=True, comment="数据集类型")
    format_type = Column(String, name="format", nullable=True, default="alpaca", comment="数据集类型")
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    Segments = relationship("DatasetSegments", back_populates="owner")
    # Annotations = relationship("DataAnnotation", back_populates="dataset")


class DatasetSegments(Base):
    """
    数据集切片表
    """
    __tablename__ = "dataset_segments"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), index=True, unique=True, comment="UUID")
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False, index=True, comment="数据集ID")
    content = Column(Text, nullable=False, comment="内容")
    word_count = Column(Integer, nullable=False, comment="字数")
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    Owner = relationship("Datasets", back_populates="Segments")

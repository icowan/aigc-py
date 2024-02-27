from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Session
from app.models.base import Base


class DatasetSample(Base):
    """
    数据集样本表
    """
    __tablename__ = "dataset_samples"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, index=True, unique=True, comment="UUID")
    title = Column(String, index=True, comment="样本标题")
    dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True, comment="数据集ID")
    system = Column(String, nullable=True, comment="系统内容")
    instruction = Column(String, nullable=True, comment="意图")
    input = Column(String, nullable=True, comment="输入")
    output = Column(String, nullable=True, comment="输出")
    conversations = Column(String, nullable=True, comment="内容")
    label = Column(String, nullable=True, comment="标签")
    remark = Column(String, nullable=True, comment="备注")
    creator_email = Column(String, nullable=False, index=True, comment="创建人邮箱")
    turns = Column(Integer, default=0, comment="对话轮次")
    type = Column(String, nullable=True, default="alpaca", comment="数据样本类型")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    Annotations = relationship("DataAnnotationSample", back_populates="sample")
    owner = relationship("Datasets", back_populates="Samples")

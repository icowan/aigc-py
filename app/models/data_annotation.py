import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, text, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class DataAnnotationType(str, enum.Enum):
    RAG = "rag"
    FAQ = "faq"
    GENERAL = "general"


class DataAnnotationStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    CLEANED = "cleaned"


class DataAnnotationSegmentType(str, enum.Enum):
    TRAIN = "train"
    TEST = "test"


class DataAnnotation(Base):
    """
    标注任务表
    """
    __tablename__ = "data_annotations"

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets_v0.id"), comment="数据集ID")
    uuid = Column(String(64), unique=True, index=True, comment="标注任务ID")
    name = Column(String(64), index=True, comment="任务名称")
    tenant_id = Column(Integer, index=True, comment="租户ID")
    principal = Column(String(32), index=True, comment="负责人")
    annotation_type = Column(String(12), index=True, comment="标注类型")
    status = Column(String(12), index=True, default=DataAnnotationStatus.PENDING, comment="标注状态")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    data_sequence = Column(String(12), comment="数据序列")
    total = Column(Integer, nullable=True, default=0, comment="需要标的数据总量")
    completed = Column(Integer, nullable=True, default=0, comment="完成标注量")
    abandoned = Column(Integer, nullable=True, default=0, comment="废弃标注量")
    train_total = Column(Integer, nullable=True, default=0, comment="训练数据总量")
    test_total = Column(Integer, nullable=True, default=0, comment="测试数据总量")
    remark = Column(String(1000), nullable=True, comment="备注")
    test_repo = Column(Text, nullable=True, comment="测试数据仓库")
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    Datasets = relationship("Datasets", back_populates="Annotations")
    Segments = relationship("DataAnnotationSegments", back_populates="DataAnnotation")


class DataAnnotationSegments(Base):
    """
    标注任务样本表
    """
    __tablename__ = "data_annotation_segments"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), unique=True, index=True, comment="样本ID")
    data_annotation_id = Column(Integer, ForeignKey("data_annotations.id"), comment="标注任务ID")
    segment_id = Column(Integer, ForeignKey("dataset_segments.id"), comment="样本ID")
    annotation_type = Column(String(12), index=True, comment="标注类型")
    segment_content = Column(Text, nullable=True, comment="样本内容")
    document = Column(String(2000), nullable=True, comment="标注文本")
    instruction = Column(String(2000), nullable=True, comment="标注说明")
    input = Column(String(2000), nullable=True, comment="标注输入")
    question = Column(String(2000), nullable=True, comment="标注问题")
    intent = Column(String(32), nullable=True, comment="标注意图")
    output = Column(String(2000), nullable=True, comment="输出结果")
    status = Column(String(12), nullable=True, index=True, default=DataAnnotationStatus.PENDING, comment="标注状态")
    segment_type = Column(String(12), nullable=True, index=True, default=DataAnnotationSegmentType.TRAIN,
                          comment="样本类型")
    creator_email = Column(String(32), nullable=True, comment="创建人邮箱")
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    DataAnnotation = relationship("DataAnnotation", back_populates="Segments")
    Segments = relationship("DatasetSegments", back_populates="DataAnnotationSegments")

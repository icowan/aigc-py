from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship, joinedload

from app.models.base import Base

AssistantToolAssociations = Table('assistant_tool_associations', Base.metadata,
                                  Column('assistant_id', Integer, ForeignKey('assistants.id'), primary_key=True),
                                  Column('tool_id', Integer, ForeignKey('tools.id'), primary_key=True))


class Assistants(Base):
    """
    助手表
    """
    __tablename__ = "assistants"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), index=True, unique=True, comment="UUID")
    tenant_id = Column(Integer, index=True, comment="租户ID")
    name = Column(String(64), index=True, unique=True, comment="名称")
    avatar = Column(String(64), nullable=True, comment="头像")
    remark = Column(String(500), nullable=True, comment="描述")
    model_name = Column(String(32), index=True, comment="模型名称")
    description = Column(String(1000), nullable=True, comment="助手描述")
    instructions = Column(String(1000), nullable=True, comment="助手使用说明")
    metadata_origin = Column(String(10000), name="metadata", nullable=True, comment="助手元数据")
    operator = Column(String(64), nullable=False, comment="操作人")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    tools = relationship("Tools", secondary=AssistantToolAssociations, back_populates="assistants")


class Tools(Base):
    """
    工具表
    """
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), index=True, unique=True, comment="UUID")
    tenant_id = Column(Integer, index=True, comment="租户ID")
    name = Column(String(64), index=True, unique=True, comment="名称")
    description = Column(String(1000), nullable=True, comment="描述")
    type = Column(String(12), index=True, comment="工具类型")
    metadata_origin = Column(String(2000), name="metadata", nullable=False, comment="工具元数据")
    operator = Column(String(24), nullable=False, comment="操作人")
    remark = Column(String(500), nullable=True, comment="备注")
    created_at = Column(DateTime, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, comment="更新时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    assistants = relationship("Assistants", secondary=AssistantToolAssociations, back_populates="tools")


def get_assistant_by_uuid(db, uuid: str, tools: bool = False):
    """
    获取助手信息
    :param db: 数据库连接
    :param uuid: 助手UUID
    :param tools: 是否获取工具列表
    :return: 助手信息 Assistants
    """
    if tools:
        return db.query(Assistants).options(joinedload(Assistants.tools)).filter(Assistants.uuid == uuid).first()
    return db.query(Assistants).filter(Assistants.uuid == uuid).first()

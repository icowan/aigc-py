from typing import List

from fastapi import UploadFile, File
from pydantic import BaseModel


class DatasetCreateRequest(BaseModel):
    """Create dataset request model."""
    name: str
    """数据集名称"""
    remark: str
    """数据集备注"""
    formatType: str = 'txt'
    """数据集类型"""
    file: UploadFile = File(...)
    """数据集文件"""
    splitType: str = '\n\n'
    """切割方式"""
    splitMax: int = 1000
    """切割的最大数据块"""


class DatasetResponse(BaseModel):
    """Create dataset response model."""
    uuid: str
    """数据集ID"""
    name: str
    """数据集名称"""
    remark: str = ""
    """数据集备注"""
    segmentCount: int = 0
    """块数量"""
    creatorEmail: str = ""
    """创建人邮箱"""
    formatType: str = 'txt'
    """数据集类型"""
    splitType: str = '\n\n'
    """切割方式"""
    splitMax: int = 1000
    """切割的最大数据块"""


class DatasetsRequest:
    """Datasets request model."""
    page: int = 1
    """页码"""
    pageSize: int = 10
    """每页数量"""
    datasetType: str = "all"
    """数据集类型"""
    formatType: str = "all"
    """数据集格式"""
    name: str = ""
    """数据集名称"""


class DatasetsResponse(BaseModel):
    """Datasets response model."""
    list: List[DatasetResponse]
    """数据集列表"""
    total: int = 0
    """总数"""
    page: int = 1
    """页码"""
    pageSize: int = 10
    """每页数量"""

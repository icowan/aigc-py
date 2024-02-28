from typing import List

from fastapi import UploadFile, File
from pydantic import BaseModel


class DatasetCreateRequest(BaseModel):
    """Create dataset request model."""
    name: str
    """数据集名称"""
    remark: str
    """数据集备注"""
    format_type: str = 'txt'
    """数据集类型"""
    file: UploadFile = File(...)
    """数据集文件"""
    split_type: str = '\n\n'
    """切割方式"""
    split_max: int = 1000
    """切割的最大数据块"""


class DatasetResponse(BaseModel):
    """Create dataset response model."""
    uuid: str
    """数据集ID"""
    name: str
    """数据集名称"""
    remark: str = ""
    """数据集备注"""
    segment_count: int = 0
    """块数量"""
    creator_email: str = ""
    """创建人邮箱"""
    format_type: str = 'txt'
    """数据集类型"""
    split_type: str = '\n\n'
    """切割方式"""
    split_max: int = 1000
    """切割的最大数据块"""


class DatasetsRequest:
    """Datasets request model."""
    page: int = 1
    """页码"""
    page_size: int = 10
    """每页数量"""
    dataset_type: str = "all"
    """数据集类型"""
    format_type: str = "all"
    """数据集格式"""
    name: str = ""
    """数据集名称"""


class DatasetsResponse(BaseModel):
    """Datasets response model."""
    datasets: List[DatasetResponse]
    """数据集列表"""
    total: int
    """总数"""
    page: int
    """页码"""
    page_size: int
    """每页数量"""

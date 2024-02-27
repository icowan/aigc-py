from typing import List

from fastapi import UploadFile, File
from pydantic import BaseModel


class DatasetCreateRequest(BaseModel):
    """Create dataset request model."""
    name: str
    remark: str
    format_type: str = 'txt'
    file: UploadFile = File(...)
    """切割方式"""
    split_type: str = '\n\n'
    """切割的最大数据块"""
    split_max: int = 1000


class DatasetResponse(BaseModel):
    """Create dataset response model."""
    uuid: str
    """数据集名称"""
    name: str
    """数据集备注"""
    remark: str = ""
    """块数量"""
    segment_count: int = 0
    """创建人邮箱"""
    creator_email: str = ""
    """数据集类型"""
    format_type: str = 'txt'
    """切割方式"""
    split_type: str = '\n\n'
    """切割的最大数据块"""
    split_max: int = 1000


class DatasetsRequest:
    page: int = 1
    page_size: int = 10
    dataset_type: str = "all"
    format_type: str = "all"
    name: str = ""


class DatasetsResponse(BaseModel):
    datasets: List[DatasetResponse]
    total: int
    page: int
    page_size: int

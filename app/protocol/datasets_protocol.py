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


class DatasetsRequest:
    page: int = 1
    page_size: int = 10
    dataset_type: str = "all"
    format_type: str = "all"
    name: str = ""


class DatasetsSample(BaseModel):
    id: str
    dataset_id: str
    title: str
    system: str
    instruction: str
    input: str
    output: str
    created_at: str
    updated_at: str


class Dataset(BaseModel):
    id: str
    name: str
    remark: str
    sample_count: int
    dataset_type: str
    format: str
    created_at: str
    updated_at: str
    dataset_sample: List[DatasetsSample]


class DatasetsResponse(BaseModel):
    datasets: List[Dataset]
    total: int
    page: int
    page_size: int

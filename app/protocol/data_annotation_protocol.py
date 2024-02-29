from typing import List

from fastapi import UploadFile, File
from pydantic import BaseModel


class AnnotationCreateRequest(BaseModel):
    """The request model for creating an annotation."""
    name: str
    """The name of the annotation."""
    remark: str = ""
    """The remark of the annotation."""
    datasetId: str
    """The dataset ID."""
    principal: str
    """The principal of the annotation."""
    dataSequence: List[int]
    """The data sequence of the annotation."""
    annotationType: str
    """The type of the annotation."""


class DataAnnotationResponse(BaseModel):
    """The response model for a data annotation."""
    uuid: str
    """The ID of the annotation."""
    name: str
    """The name of the annotation."""
    datasetName: str = ""
    """The name of the dataset."""
    remark: str = None
    """The remark of the annotation."""
    annotationType: str
    """The type of the annotation."""
    principal: str
    """The principal of the annotation."""
    status: str
    """The status of the annotation."""
    dataSequence: list[int] = [0, 0]
    """The data sequence of the annotation."""
    total: int = 0
    """The total of the annotation."""
    createdAt: str
    """The created time of the annotation."""
    completedAt: str = ""
    """The completed time of the annotation."""
    completed: int = 0
    """The completed of the annotation."""
    abandoned: int = 0


class DataAnnotationsResponse(BaseModel):
    """The response model for a list of data annotations."""
    list: List[DataAnnotationResponse]
    """The list of data annotations."""
    total: int
    """The total of the data annotations."""
    page: int
    """The page of the data annotations."""
    pageSize: int
    """The page size of the data annotations."""


class DataAnnotationSegmentResponse(BaseModel):
    """The response model for a segment."""
    uuid: str
    """The status of the segment."""
    createdAt: str
    """The created time of the segment."""
    updatedAt: str = ''
    """The updated time of the segment."""
    status: str = 'pending'
    """The status of the segment."""
    annotationType: str = 'gengeral'
    """The type of the annotation."""
    segmentContent: str
    """The content of the segment."""
    document: str = ""
    """The document of the segment."""
    instruction: str = ""
    """The instruction of the segment."""
    input: str = ""
    """The input of the segment."""
    question: str = ""
    """The question of the segment."""
    intent: str = ""
    """The intent of the segment."""
    output: str = ""
    """The output of the segment."""
    creatorEmail: str = ''
    """The creator email of the segment."""


class DataAnnotationSegmentMarkRequest(BaseModel):
    """The status of the segment."""
    document: str = None
    """The document of the segment."""
    instruction: str = None
    """The instruction of the segment."""
    input: str = None
    """The input of the segment."""
    question: str = None
    """The question of the segment."""
    intent: str = None
    """The intent of the segment."""
    output: str = None

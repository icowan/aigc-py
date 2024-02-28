from typing import List

from fastapi import UploadFile, File
from pydantic import BaseModel


class AnnotationCreateRequest(BaseModel):
    """The request model for creating an annotation."""
    name: str
    """The name of the annotation."""
    remark: str
    """The remark of the annotation."""
    dataset_id: str
    """The dataset ID."""
    principal: str
    """The principal of the annotation."""
    data_sequence: List[int]
    """The data sequence of the annotation."""
    annotation_type: str
    """The type of the annotation."""

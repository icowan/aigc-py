import os
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Request
from requests import Session

from app.models.base import get_db
from app.models.datasets import Datasets, DatasetSegments
from app.protocol.api_protocol import ErrorResponse, SuccessResponse
from app.protocol.datasets_protocol import DatasetsResponse, DatasetCreateRequest, DatasetResponse
from app.repository.repository import Repository, get_repository

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/create", tags=["datasets"])
async def create_dataset(request: Request, name: str = Form(...), format_type: str = "txt", split_type: str = '\n\n',
                         split_max: int = 1000, remark: Optional[str] = Form(None), file: UploadFile = File(...),
                         db: Session = Depends(get_db)):
    store: Repository = get_repository(db)
    # store: Repository = request.state.store

    dataset = store.datasets().find_by_name(name)
    if dataset:
        raise HTTPException(status_code=400, detail="Dataset name already exists.")

    # 获取文件大小，单位为字节
    file_size = file.file.seek(0, 2)  # 移动到文件的末尾，返回文件大小
    file.file.seek(0)  # 重置文件指针到开始位置，以便后续读取

    # 设置文件大小限制为 100MB
    max_file_size = 100 * 1024 * 1024  # 100MB 转换为字节

    # 判断文件大小
    if file_size > max_file_size:
        # 如果文件大于 100MB，返回错误
        raise HTTPException(status_code=413, detail="File size exceeds limit (100MB).")

    content = await file.read()
    content_str = content.decode("utf-8")
    # 如果format_type == 'txt'，则按照split_type和split_max进行切割
    content_list = []
    if format_type == 'txt':
        content_list = content_str.split(split_type)

    # 创建数据集
    tenant_id = request.state.tenant_id
    creator_email = request.state.email

    uid = f"dataset-{uuid.uuid4()}"
    dataset = store.datasets().create(
        Datasets(name=name, segment_count=len(content_list), uuid=uid, remark=remark, format_type=format_type,
                 creator_email=creator_email,
                 tenant_id=tenant_id,
                 ))
    segment_list = []
    for i, content in enumerate(content_list):
        segment_list.append(
            DatasetSegments(uuid=f"segment-{uuid.uuid4()}", dataset_id=dataset.id, content=content,
                            word_count=len(content.split())))

    store.dataset_segments().add_segments(segment_list)

    return DatasetResponse(uuid=uid, name=name)


@router.put("/{datasetId}", tags=["datasets"])
async def update_dataset():
    return


@router.delete("/{datasetId}", tags=["datasets"])
async def delete_dataset(request: Request, datasetId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)

    dataset = store.datasets().find_by_uuid(tenant_id, datasetId)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    if store.datasets().delete(dataset) is False:
        raise HTTPException(status_code=500, detail="Failed to delete dataset.")

    return


@router.get("/list", tags=["datasets"])
async def datasets_list(request: Request, page: int = 1, page_size: int = 10,
                        name: str = "", db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    # 获取数据集列表
    datasets, total = store.datasets().list(tenant_id, name, page, page_size)
    dataset_result: List[DatasetResponse] = []
    for dataset in datasets:
        dataset_result.append(DatasetResponse(uuid=dataset.uuid, name=dataset.name, remark=dataset.remark,
                                              segment_count=dataset.segment_count, creator_email=dataset.creator_email,
                                              format_type=dataset.format_type, split_type=dataset.split_type,
                                              split_max=dataset.split_max))

    return DatasetsResponse(datasets=dataset_result, total=total, page=page, page_size=page_size)

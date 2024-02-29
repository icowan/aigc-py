import os
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Request
from requests import Session

from app.models.base import get_db
from app.models.datasets import Datasets, DatasetSegments
from app.protocol.api_protocol import ErrorResponse, SuccessResponse, ErrorException
from app.protocol.datasets_protocol import DatasetsResponse, DatasetCreateRequest, DatasetResponse
from app.repository.repository import Repository, get_repository

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/create", tags=["datasets"], description="Create a new dataset.")
async def create_dataset(request: Request, name: str = Form(...), formatType: str = "txt", splitType: str = '\n\n',
                         splitMax: int = 1000, remark: Optional[str] = Form(None), file: UploadFile = File(...),
                         db: Session = Depends(get_db)):
    store: Repository = get_repository(db)
    # store: Repository = request.state.store

    dataset = await store.datasets().find_by_name(name)
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
    if formatType == 'txt':
        content_list = content_str.split(splitType)

    # 创建数据集
    tenant_id = request.state.tenant_id
    creator_email = request.state.email

    try:
        uid = f"dataset-{uuid.uuid4()}"
        dataset = await store.datasets().create(
            Datasets(name=name, segment_count=len(content_list), uuid=uid, remark=remark, format_type=formatType,
                     creator_email=creator_email,
                     tenant_id=tenant_id,
                     ))
    except Exception as e:
        raise ErrorException(code=500, message=str(e))

    segment_list: List[DatasetSegments] = []
    sn = 0
    for i, content in enumerate(content_list):
        if len(content.strip()) == 0:
            continue
        segment_list.append(
            DatasetSegments(uuid=f"segment-{uuid.uuid4()}", dataset_id=dataset.id, content=content,
                            word_count=len(content.split()), serial_number=sn))
        sn += 1
    try:
        await store.dataset_segments().add_segments(segment_list)
    except Exception as e:
        await store.datasets().delete(dataset, unscoped=True)
        raise ErrorException(code=500, message=str(e))

    dataset.segment_count = len(segment_list)
    await store.datasets().update(dataset.id, dataset)

    return SuccessResponse(data=DatasetResponse(uuid=uid, name=name))


@router.delete("/{datasetId}", tags=["datasets"], description="Delete a dataset.")
async def delete_dataset(request: Request, datasetId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)

    dataset = await store.datasets().find_by_uuid(tenant_id, datasetId)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    if store.datasets().delete(dataset) is False:
        raise HTTPException(status_code=500, detail="Failed to delete dataset.")

    return SuccessResponse()


@router.get("/list", tags=["datasets"], description="List datasets.")
async def datasets_list(request: Request, page: int = 1, page_size: int = 10,
                        name: str = "", db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    # 获取数据集列表
    datasets, total = await store.datasets().list(tenant_id, name, page, page_size)
    dataset_result: List[DatasetResponse] = []
    for dataset in datasets:
        dataset_result.append(DatasetResponse(uuid=dataset.uuid, name=dataset.name, remark=str(dataset.remark),
                                              segmentCount=dataset.segment_count, creatorEmail=dataset.creator_email,
                                              formatType=dataset.format_type, splitType=dataset.split_type,
                                              splitMax=dataset.split_max))

    return SuccessResponse(data=DatasetsResponse(list=dataset_result, total=total, page=page, pageSize=page_size))

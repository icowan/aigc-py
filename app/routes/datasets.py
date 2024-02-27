import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Request
from requests import Session

from app.models.base import get_db
from app.models.datasets import Datasets
from app.protocol.datasets_protocol import DatasetsResponse, DatasetCreateRequest
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
    if format_type == 'txt':
        content_list = content_str.split(split_type)

    sample_count = len(content_list)
    # 创建数据集
    tenant_id = request.state.tenant_id
    creator_email = request.state.email
    store: Repository = get_repository(db)
    # store: Repository = request.state.store
    uid = f"dataset-{uuid.uuid4()}"
    dataset = store.datasets().create(
        dataset=Datasets(name=name, sample_count=len(content_list), uuid=uid, remark=remark, format_type=format_type,
                         creator_email=creator_email,
                         tenant_id=tenant_id, type="text",
                         ))
    print(dataset)
    # 保存切割好的内容到数据库

    return {"message": "Dataset created successfully"}


@router.put("/update", tags=["datasets"])
async def update_dataset():
    return {"message": "Dataset updated successfully"}


@router.delete("/delete/{datasetId}", tags=["datasets"])
async def delete_dataset(datasetId: str):
    return {"message": "Dataset deleted successfully"}


@router.get("/list", tags=["datasets"])
async def datasets_list(page: int = 1, page_size: int = 10,
                        dataset_type: str = "all",
                        format_type: str = "all",
                        name: str = "", db: Session = Depends(get_db)):
    return {"message": "Dataset list"}

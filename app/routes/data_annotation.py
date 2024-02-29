import uuid
from datetime import datetime
from typing import List, Type

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.data_annotation import DataAnnotation, DataAnnotationSegments, DataAnnotationStatus
from app.models.datasets import Datasets
from app.protocol.api_protocol import SuccessResponse
from app.protocol.data_annotation_protocol import DataAnnotationResponse, AnnotationCreateRequest, \
    DataAnnotationsResponse, DataAnnotationSegmentResponse, DataAnnotationSegmentMarkRequest
from app.repository.repository import get_repository, Repository

router = APIRouter(
    prefix="/annotation",
    tags=["annotation"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.delete("/task/{annotationId}/delete", tags=["annotation"], description="删除标注任务")
async def delete_annotation(request: Request, annotationId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    data_annotation = await store.data_annotation().get_by_uuid(tenant_id=tenant_id, uid=annotationId, datasets=False)
    if not data_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    status = DataAnnotationStatus(data_annotation.status)
    if status != DataAnnotationStatus.COMPLETED and status != DataAnnotationStatus.CLEANED:
        raise HTTPException(status_code=400,
                            detail="The annotation task is not completed or cleaned, cannot be deleted.")

    try:
        await store.data_annotation().delete(data_annotation.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete annotation failed: {e}")

    return SuccessResponse()


@router.get("/task/{annotationId}/info", tags=["annotation"], description="获取标注任务详情")
async def annotation_info(request: Request, annotationId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    data_annotation = await store.data_annotation().get_by_uuid(tenant_id=tenant_id, uid=annotationId, datasets=True)
    if not data_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    return SuccessResponse(
        data=DataAnnotationResponse(uuid=data_annotation.uuid, datasetName=data_annotation.Datasets.name,
                                    name=data_annotation.name,
                                    remark=str(data_annotation.remark),
                                    annotationType=data_annotation.annotation_type,
                                    principal=data_annotation.principal,
                                    status=data_annotation.status,
                                    dataSequence=list(map(int, data_annotation.data_sequence.split("-"))),
                                    total=data_annotation.total, createdAt=str(data_annotation.created_at),
                                    completedAt=str(data_annotation.completed_at),
                                    completed=data_annotation.completed,
                                    abandoned=data_annotation.abandoned))


@router.put("/task/{annotationId}/clean", tags=["annotation"], description="清理标注任务")
async def clean_annotation(request: Request, annotationId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    data_annotation = await store.data_annotation().get_by_uuid(tenant_id=tenant_id, uid=annotationId, datasets=False)
    if not data_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    if data_annotation.status != DataAnnotationStatus.PENDING:
        raise HTTPException(status_code=400, detail="The annotation task is not pending, cannot be cleaned.")

    data_annotation.status = DataAnnotationStatus.CLEANED
    data_annotation.completed_at = datetime.now()

    try:
        await store.data_annotation().update_data_annotation(data_annotation.id, data_annotation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clean annotation failed: {e}")

    return SuccessResponse()


@router.post("/task/create", tags=["annotation"], description="Create a new annotation.")
async def create_annotation(request: Request, req: AnnotationCreateRequest, db: Session = Depends(get_db)):
    tenant_id: int = request.state.tenant_id
    store: Repository = get_repository(db)
    dataset: Datasets = await store.datasets().find_by_uuid(tenant_id, req.datasetId)
    if not dataset:
        raise HTTPException(status_code=400, detail="Dataset not found.")

    if len(req.dataSequence) != 2:
        raise HTTPException(status_code=400, detail="Data sequence must be a list of two integers.")

    data_sequence = "-".join(map(str, req.dataSequence))
    total = req.dataSequence[1] - req.dataSequence[0]

    segments = await store.dataset_segments().get_by_dataset_id_and_sn(dataset.id, req.dataSequence[0],
                                                                       req.dataSequence[1])
    if not segments:
        raise HTTPException(status_code=400, detail="Segments not found.")

    annotation_segments: List[DataAnnotationSegments] = []
    try:
        data_annotation: DataAnnotation = await store.data_annotation().create(
            DataAnnotation(dataset_id=dataset.id, uuid=f"annotation-{uuid.uuid4()}", name=req.name, remark=req.remark,
                           annotation_type=req.annotationType, tenant_id=tenant_id,
                           principal=req.principal,
                           status=DataAnnotationStatus.PENDING,
                           data_sequence=data_sequence,
                           total=total))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create annotation failed: {e}")

    for segment in segments:
        annotation_segments.append(
            DataAnnotationSegments(data_annotation_id=data_annotation.id, segment_id=segment.id,
                                   uuid=f"das-{uuid.uuid4()}",
                                   annotation_type=data_annotation.annotation_type,
                                   segment_content=segment.content, status=DataAnnotationStatus.PENDING, ))
    try:
        # 将数据集里的内容放到标注任务里
        await store.data_annotation().add_annotation_segments(annotation_segments)
    except Exception as e:
        await store.data_annotation().delete(data_annotation.id)
        raise HTTPException(status_code=500, detail=f"Create annotation segments failed: {e}")

    return SuccessResponse(data=DataAnnotationResponse(uuid=data_annotation.uuid, name=data_annotation.name,
                                                       annotationType=data_annotation.annotation_type,
                                                       principal=data_annotation.principal,
                                                       status=data_annotation.status,
                                                       createdAt=str(data_annotation.created_at),
                                                       dataSequence=list(
                                                           map(int, data_annotation.data_sequence.split("-")))))


@router.get("/task/list", tags=["annotation"], description="获取标注任务列表")
async def list_annotation(request: Request, status: str = None, page: int = 1, page_size: int = 10,
                          db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    annotations, total = await store.data_annotation().get_annotation_tasks(tenant_id, status, datasets=True,
                                                                            page=page, page_size=page_size)

    result_list: List[DataAnnotationResponse] = []

    for annotation in annotations:
        result_list.append(
            DataAnnotationResponse(uuid=annotation.uuid, datasetName=annotation.Datasets.name, name=annotation.name,
                                   remark=str(annotation.remark),
                                   annotationType=annotation.annotation_type,
                                   principal=annotation.principal,
                                   status=annotation.status,
                                   dataSequence=list(map(int, annotation.data_sequence.split("-"))),
                                   total=annotation.total, createdAt=str(annotation.created_at),
                                   completedAt=str(annotation.completed_at),
                                   completed=annotation.completed,
                                   abandoned=annotation.abandoned))

    return SuccessResponse(
        data=DataAnnotationsResponse(list=result_list, total=total, page=page, pageSize=page_size))


@router.get("/task/{annotationId}/segment/next", tags=["annotation"], description="获取一条标注任务样本")
async def annotation_segment_next(request: Request, annotationId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    data_annotation = await store.data_annotation().get_by_uuid(tenant_id=tenant_id, uid=annotationId, datasets=False)
    if not data_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    if data_annotation.status != DataAnnotationStatus.PENDING and data_annotation.status != DataAnnotationStatus.PROCESSING:
        raise HTTPException(status_code=400,
                            detail="The annotation task is not pending or processing, cannot be annotated.")

    # 根据sn号获取标注记录
    annotation_segment_info = await store.data_annotation().get_annotation_one_segment(data_annotation.id,
                                                                                       status=DataAnnotationStatus.PENDING)
    if not annotation_segment_info:
        return SuccessResponse(data=None)

    return SuccessResponse(
        data=DataAnnotationSegmentResponse(uuid=annotation_segment_info.uuid,
                                           segmentContent=annotation_segment_info.segment_content,
                                           createdAt=annotation_segment_info.created_at.strftime("%Y-%m-%d %H:%M:%S")),
        updatedAt=annotation_segment_info.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        status=annotation_segment_info.status, annotationType=annotation_segment_info.annotation_type,
        document=annotation_segment_info.document, instruction=annotation_segment_info.instruction,
        input=annotation_segment_info.input, question=annotation_segment_info.question,
        intent=annotation_segment_info.intent, output=annotation_segment_info.output,
        creatorEmail=annotation_segment_info.creator_email,
    )


@router.get("/task/{annotationId}/segment/{segmentId}/info", tags=["annotation"], description="获取一条标注任务样本")
async def annotation_segment_next(request: Request, annotationId: str, segmentId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    data_annotation = await store.data_annotation().get_by_uuid(tenant_id=tenant_id, uid=annotationId, datasets=False)
    if not data_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    if data_annotation.status != DataAnnotationStatus.PENDING:
        raise HTTPException(status_code=400, detail="The annotation task is not pending, cannot be annotated.")

    # 根据sn号获取标注记录
    annotation_segment_info = await store.data_annotation().get_annotation_segment_by_uuid(data_annotation.id,
                                                                                           segmentId)
    if not annotation_segment_info:
        raise HTTPException(status_code=404, detail="Segment not found.")

    return SuccessResponse(
        data=DataAnnotationSegmentResponse(uuid=annotation_segment_info.uuid,
                                           segmentContent=annotation_segment_info.segment_content,
                                           createdAt=annotation_segment_info.created_at.strftime("%Y-%m-%d %H:%M:%S")),
        updatedAt=annotation_segment_info.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        status=annotation_segment_info.status, annotationType=annotation_segment_info.annotation_type,
        document=annotation_segment_info.document, instruction=annotation_segment_info.instruction,
        input=annotation_segment_info.input, question=annotation_segment_info.question,
        intent=annotation_segment_info.intent, output=annotation_segment_info.output,
        creatorEmail=annotation_segment_info.creator_email,
    )


@router.get("/task/{annotationId}/segment/{index}/get", tags=["annotation"], description="获取一条标注任务样本")
async def annotation_segment_get(request: Request, annotationId: str, index: int = 0, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    data_annotation = await store.data_annotation().get_by_uuid(tenant_id=tenant_id, uid=annotationId, datasets=False)
    if not data_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    if data_annotation.status != DataAnnotationStatus.PENDING:
        raise HTTPException(status_code=400, detail="The annotation task is not pending, cannot be annotated.")

    # 根据sn号获取标注记录
    annotation_segment_info = await store.data_annotation().get_annotation_one_segment(data_annotation.id, index)
    if not annotation_segment_info:
        raise HTTPException(status_code=404, detail="Segment not found.")

    return SuccessResponse(
        data=DataAnnotationSegmentResponse(uuid=annotation_segment_info.uuid,
                                           segmentContent=annotation_segment_info.segment_content,
                                           createdAt=annotation_segment_info.created_at.strftime("%Y-%m-%d %H:%M:%S")),
        updatedAt=annotation_segment_info.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        status=annotation_segment_info.status, annotationType=annotation_segment_info.annotation_type,
        document=annotation_segment_info.document, instruction=annotation_segment_info.instruction,
        input=annotation_segment_info.input, question=annotation_segment_info.question,
        intent=annotation_segment_info.intent, output=annotation_segment_info.output,
        creatorEmail=annotation_segment_info.creator_email,
    )


@router.post("/task/{annotationId}/segment/{annotationSegmentId}/mark", tags=["annotation"],
             description="标注一条任务样本")
async def annotation_mark(request: Request, annotationId: str, annotationSegmentId: str,
                          req: DataAnnotationSegmentMarkRequest, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    email = request.state.email
    store: Repository = get_repository(db)
    data_annotation = await store.data_annotation().get_by_uuid(tenant_id=tenant_id, uid=annotationId, datasets=False)
    if not data_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    segment: DataAnnotationSegments = await store.data_annotation().get_annotation_segment_by_uuid(data_annotation.id,
                                                                                                   annotationSegmentId)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found.")

    segment.creator_email = email
    segment.status = DataAnnotationStatus.COMPLETED
    segment.document = req.document
    segment.instruction = req.instruction
    segment.input = req.input
    segment.question = req.question
    segment.intent = req.intent
    segment.output = req.output
    segment.updated_at = datetime.now()

    try:
        data_annotation.completed = data_annotation.completed + 1
        await store.data_annotation().update_annotation_segment(data_annotation, segment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mark annotation failed: {e}")

    return SuccessResponse()


@router.put("/task/{annotationId}/segment/{annotationSegmentId}/abandoned", tags=["annotation"],
            description="放弃一条标注任务样本")
async def abandoned_annotation(request: Request, annotationId: str, annotationSegmentId: str,
                               db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    email = request.state.email
    store: Repository = get_repository(db)

    data_annotation = await store.data_annotation().get_by_uuid(tenant_id=tenant_id, uid=annotationId, datasets=False)
    if not data_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    segment = await store.data_annotation().get_annotation_segment_by_uuid(data_annotation.id, annotationSegmentId)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found.")

    segment.status = DataAnnotationStatus.ABANDONED
    segment.updated_at = datetime.now()
    segment.creator_email = email

    try:
        data_annotation.abandoned = data_annotation.abandoned + 1
        await store.data_annotation().update_annotation_segment(data_annotation, segment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mark annotation failed: {e}")

    return SuccessResponse()


@router.post("/task/{annotationId}/detect/annotation/sync", tags=["annotation"], description="同步检查标注任务是否完成")
async def detect_annotation(request: Request, annotationId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    data_annotation = await store.data_annotation().get_by_uuid(tenant_id=tenant_id, uid=annotationId, datasets=False)
    if not data_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    if data_annotation.status != DataAnnotationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="The annotation task is not completed.")
    # 获取所有已标注后的内容
    # 根据标内容的类型生成对应的文件
    # 异步调用模型对内容进行检测

    return SuccessResponse(data=True)

from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Request
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.protocol.annotation_protocol import AnnotationCreateRequest
from app.protocol.api_protocol import SuccessResponse
from app.repository.repository import get_repository, Repository

router = APIRouter(
    prefix="/annotation",
    tags=["annotation"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/create", tags=["annotation"])
async def create_annotation(request: Request, req: AnnotationCreateRequest, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    dataset = store.datasets().find_by_uuid(tenant_id, req.dataset_id)
    if not dataset:
        raise HTTPException(status_code=400, detail="Dataset not found.")

    return SuccessResponse()


@router.get("/list", tags=["annotation"])
async def list_annotation(request: Request, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    return


@router.get("/{annotationId}/get", tags=["annotation"])
async def detail_annotation(request: Request, annotationId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    return


@router.post("/{annotationId}/update", tags=["annotation"])
async def update_annotation(request: Request, annotationId: str, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    store: Repository = get_repository(db)
    return
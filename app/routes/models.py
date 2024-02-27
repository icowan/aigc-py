from fastapi import APIRouter

router = APIRouter(
    prefix="/api/models",
    tags=["models"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def list_models():
    return {"message": "List of models"}


@router.post("/")
async def create_model():
    return {"message": "Create a model"}


@router.get("/{model_id}")
async def get_model(model_id: str):
    return {"message": f"Model {model_id}"}


@router.delete("/{model_id}")
async def delete_model(model_id: str):
    return {"message": f"Delete model {model_id}"}


@router.post("/{model_id}/deploy")
async def deploy_model(model_id: str):
    return {"message": f"Deploy model {model_id}"}


@router.post("/{model_id}/undeploy")
async def undeploy_model(model_id: str):
    return {"message": f"Undeploy model {model_id}"}

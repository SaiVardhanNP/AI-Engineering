from fastapi import APIRouter
from models.echo import EchoRequest

router = APIRouter()


@router.post("/")
def echo(request: EchoRequest):
    return {"message": request.message}


@router.get("/health")
def health():
    return {"status": "ok"}

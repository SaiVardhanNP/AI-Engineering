from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dependencies import get_model_registry

router = APIRouter(prefix="/models", tags=["models"])


class ModelEntry(BaseModel):
    id: str
    label: str
    provider: str
    cloud: bool
    note: Optional[str] = None


class ProviderEntry(BaseModel):
    id: str
    label: str
    cloud: bool
    env: Optional[str] = None
    status: str


class ModelCatalog(BaseModel):
    default: str
    models: list[ModelEntry]
    providers: list[ProviderEntry]


@router.get("", response_model=ModelCatalog)
def list_models(registry=Depends(get_model_registry)):
    return registry.catalog()

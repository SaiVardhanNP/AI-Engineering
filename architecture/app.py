from fastapi import FastAPI
from api.routes.echo import router as echo_router
from api.routes.features import router as feature_router
from exceptions.pipeline import InvalidLLMResponseError
from api.exception_handlers import invalid_llm_response_handler

app = FastAPI()

app.add_exception_handler(InvalidLLMResponseError, invalid_llm_response_handler)

app.include_router(echo_router, prefix="/echo", tags=["Echo"])

app.include_router(feature_router, prefix="/feature", tags=["Features"])


@app.get("/")
def root():
    return {"msg": "Hey there!"}

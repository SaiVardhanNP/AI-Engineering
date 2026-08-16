from fastapi import Request
from fastapi.responses import JSONResponse


from exceptions.pipeline import InvalidLLMResponseError

async def invalid_llm_response_handler(request:Request,exc:InvalidLLMResponseError):
    return JSONResponse(
        status_code=500,
        content={
            "detail":"Model returned invalid structured output"
        }
    )
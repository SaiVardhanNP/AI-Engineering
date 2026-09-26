from pydantic import BaseModel


class QueryRewriteDecision(BaseModel):
    should_rewrite: bool
    rewritten_query: str | None

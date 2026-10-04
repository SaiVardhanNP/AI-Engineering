from pydantic import BaseModel, Field


class Claim(BaseModel):
    statement: str = Field(
        description="One factual claim made in the reply, keeping any qualifiers such as 'recent' or 'this month'"
    )
    supporting_quote: str | None = Field(
        default=None,
        description="A verbatim quote copied exactly from the findings that supports the claim, or null if none does",
    )


class EvaluationResult(BaseModel):
    relevant: bool = Field(description="The reply addresses what the customer asked")
    complete: bool = Field(description="Every issue the customer raised is addressed")
    claims: list[Claim] = Field(
        default_factory=list,
        description="Every factual claim in the reply, each with its supporting quote",
    )
    feedback: str = Field(
        description="What must change for the reply to be relevant and complete. Empty if nothing."
    )

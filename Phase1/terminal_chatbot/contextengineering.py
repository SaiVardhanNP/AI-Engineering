from pydantic import BaseModel


class QAContext(BaseModel):
    system_prompt: str
    user_question: str
    retrieved_docs: list[str]


def build_context(data: QAContext) -> str:

    sections = [
        data.system_prompt,
        "",
        "Use Only the following documents:",
        "",
    ]

    for i, doc in enumerate(data.retrieved_docs):
        sections.append(f"Document {i + 1}:")
        sections.append(doc)
        sections.append("")

    sections.append("Question: ")
    sections.append(data.user_question)

    return "\n".join(sections)


result = build_context(
    QAContext(
        system_prompt="You are a Python tutor.",
        user_question="Are Python lists mutable?",
        retrieved_docs=["Python lists are mutable.", "Python tuples are immutable."],
    )
)

print(result)

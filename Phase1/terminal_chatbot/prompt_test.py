from gemini_client import client
from prompts.summarize import build_prompt
from pydantic_models import SummarizeInput

# short_summarize_prompt = build_prompt(
#     SummarizeInput(
#         text="Large article...",
#         tone="professional",
#         length="short",
#     )
# )

# long_summarize_prompt = build_prompt(
#     SummarizeInput(
#         text="Large article...",
#         tone="casual",
#         length="long",
#     )
# )

# print(short_summarize_prompt)
# print(long_summarize_prompt)

software_prompt = build_prompt(
    SummarizeInput(
        text="This feature is broken.",
        tone="casual",
        length="long",
        persona="software_engineer",
    )
)

writer_prompt = build_prompt(
    SummarizeInput(
        text="This feature is broken.",
        tone="professional",
        length="long",
        persona="technical_writer",
    )
)

customer_prompt = build_prompt(
    SummarizeInput(
        text="This feature is broken.",
        tone="casual",
        length="long",
        persona="customer_support",
    )
)


print(software_prompt)
print(writer_prompt)
print(customer_prompt)

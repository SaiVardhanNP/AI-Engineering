from prompts.rewrite_prompt import Prompting
from pydantic_models import RewritePrompt


zero_shot_prompt = Prompting(
    RewritePrompt(text="Hey, send me the docs ASAP.", tone="professional")
)

zero_shot_prompt_response = zero_shot_prompt.zero_shot_prompting()

one_shot_prompt = Prompting(
    RewritePrompt(text="Hey, send me the docs ASAP.", tone="friendly")
)

one_shot_prompt_response = one_shot_prompt.one_shot_prompting()

few_shot_prompt = Prompting(
    RewritePrompt(text="Hey, send me the docs ASAP.", tone="friendly")
)

few_shot_prompt_response = few_shot_prompt.few_shot_prompting()

print(zero_shot_prompt_response)

print(one_shot_prompt_response)

print(few_shot_prompt_response)

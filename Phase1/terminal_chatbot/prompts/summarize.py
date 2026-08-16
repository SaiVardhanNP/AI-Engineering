from pydantic_models import SummarizeInput

tone_map = {"casual": "Use a casual tone.", "professional": "Use a professional tone."}

persona_map = {
    "software_engineer": (
        "You are a senior software engineer. "
        "Write clearly and concisely."
    ),
    "technical_writer": (
        "You are a technical writer. "
        "Prioritize clarity and structure."
    ),
    "customer_support": (
        "You are a customer support specialist. "
        "Be empathetic and professional."
    ),
}


length_map = {
    "long": "Keep it long",
    "medium": "Keep it medium",
    "short": "Keep it short",
}


def build_prompt(data: SummarizeInput) -> str:
    prompt = f"""
    {persona_map[data.persona]}
    
    
    {tone_map[data.tone]}
    {length_map[data.length]}
    
    Rewrite the following text:
    {data.text}
    """

    return prompt

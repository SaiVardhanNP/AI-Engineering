from models.ticket import TicketInput, TicketClassification


class TicketClassificationPrompt:
    schema = TicketClassification.model_json_schema()

    def build(self, prompt: TicketInput) -> str:
        return f"""
You are a customer support triage assistant.

Analyze the support ticket.

Choose exactly one department:
- billing
- technical
- sales
- general

Determine:
- priority (low, medium, high)
- customer sentiment (positive, neutral, negative)

Return ONLY valid JSON with this exact structure:

{self.schema}

Rules:
- Return only JSON.
- Do not include markdown or code fences.
- Use exactly the keys: department, priority, sentiment.
- department must be one of: billing, technical, sales, general.
- priority must be one of: low, medium, high.
- sentiment must be one of: positive, neutral, negative.

Ticket:
{prompt.ticket}"""

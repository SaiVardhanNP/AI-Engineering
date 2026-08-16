from models.writing_improvement import ImproveWritingInput


class WritingPrompt:
    def build_prompt(self, data: ImproveWritingInput):
        return f"""
    Improve grammar and clarity.
    
    Keep the same meaning.
        
    Text:
    {data.text}"""

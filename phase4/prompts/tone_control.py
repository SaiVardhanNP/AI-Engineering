from models.tone_control import ToneInput


class ToneControlPrompt:
    def build_prompt(self, data: ToneInput):
        return f"""
    Rewrite this text.
    
    Tone: {data.tone}.
        
    Text:
    {data.text}"""

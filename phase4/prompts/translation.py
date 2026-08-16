from models.translation import TranslationInput


class TranslationPrompt:
    def build_prompt(self, data: TranslationInput):
        return f"""
    Translate the following text into {data.target_language}
    
    Only return the translation.
    
    Text:
    
    {data.text}
    """

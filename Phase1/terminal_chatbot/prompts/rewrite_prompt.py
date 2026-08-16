from pydantic_models import RewritePrompt
from dataclasses import dataclass

tone_map = {"professional": "keep it professional", "friendly": "keep it friendly"}



@dataclass
class Prompting:
    data: RewritePrompt

    def zero_shot_prompting(self):
        prompt = f"""
        You are a rewriting assistant.
        {tone_map[self.data.tone]}
        
        Text: {self.data.text}
        """
        return prompt
    
    def one_shot_prompting(self):
        prompt = f"""
        You are a rewriting assistant.
        {tone_map[self.data.tone]}
        
        Example:
        Input:
        I can't attend today's meeting because I'm feeling sick.
        
        Output:
        Unfortunately, I won't be able to attend today's meeting as I'm feeling unwell. I appreciate your understanding.
        Now rewrite the following text in the same style.
        
        Input:
        {self.data.text}
        
        Output:
        """
        return prompt

    def few_shot_prompting(self):
        prompt = f"""
        You are a rewriting assistant.
        {tone_map[self.data.tone]}
        
        Examples:
        
        Input:
        I can't attend today's meeting because I'm feeling sick.
        
        Output:
        Unfortunately, I won't be able to attend today's meeting as I'm feeling unwell. I appreciate your understanding.
        
        Input:
        Send me the report today.
        
        Output:
        Could you please send me the report today? Thank you in advance.
        
        Input:
        This feature doesn't work.
        
        Output:
        It appears this feature isn't working as expected. Could you please look into it?
        
        Now rewrite the following text in the same style.
        
        Input:
        {self.data.text}
        
        Output:
        """
        return prompt
class PipelineError(Exception):
    """Something wrong with the LLMS"""



class InvalidLLMResponseError(PipelineError):
    """Something went wrong with the pipeline at the moment"""

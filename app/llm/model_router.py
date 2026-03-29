from app.llm.groqClient import generate_response
from app.config.settings import Settings

def route_model(task_type:str,prompt:str):
    if task_type=="blog":
        model=Settings.DEFAULT_MODEL
    else:
        model=Settings.FAST_MODEL
    return generate_response(model,prompt)

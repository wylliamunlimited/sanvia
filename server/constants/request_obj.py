from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str
    # thread_id: str = None ## Temporary
    
    
class SignInRequest(BaseModel):
    email: str
    password: str
    returnSecureToken: bool = True
    
    
class SignUpRequest(BaseModel):
    email: str
    password: str
    returnSecureToken: bool = True
    firstname: str
    lastname: str
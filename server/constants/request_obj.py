from pydantic import BaseModel


class EncryptedPromptRequest(BaseModel):
    encrypted_prompt: str
    iv: str
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
from pydantic import BaseModel

class NoteCreate(BaseModel):
    content: str
    type: str
    user_email: str

class NoteResponse(BaseModel):
    id: int
    timestamp: str
    content: str
    type: str
    user_email: str

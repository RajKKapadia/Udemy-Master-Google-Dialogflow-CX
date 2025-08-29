from pydantic import BaseModel


class CustomRequest(BaseModel):
    name: str
    number: int


class CustomResponse(BaseModel):
    status: str
    message: str

# api/v1/models.py

from pydantic import BaseModel, HttpUrl

class HackRxRequest(BaseModel):
    documents: HttpUrl  # Ensures the input is a valid URL
    questions: list[str]

class HackRxResponse(BaseModel):
    answers: list[str]